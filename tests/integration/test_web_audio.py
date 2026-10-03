import hashlib
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from tabi.api.app import create_app
from tabi.api.runtime import Runtime
from tabi.core.audio.pcm import BLOCK_SAMPLES, PCMReader
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures

pytestmark = pytest.mark.media


def test_audio_http_waveform_gain_fades_mix_metadata_and_master_integrity(tmp_path):
    repo = Path(__file__).resolve().parents[2]
    root = tmp_path / "audio"
    generate_fixtures(root)
    sources = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*.wav")}
    settings = load_settings(repo / "examples/settings.macos.toml", env={}, cwd=repo, home=tmp_path)
    runtime = Runtime(settings, {"work": tmp_path})
    with TestClient(
        create_app(runtime, "http://testserver", repo / "web/dist", drive_jobs=False)
    ) as client:
        boot = client.post(
            "/api/v1/bootstrap",
            json={"protocol": "1", "secret": runtime.sessions.ticket()},
            headers={"Origin": "http://testserver"},
        )
        headers = {"Origin": "http://testserver", "X-Tabi-CSRF": boot.json()["csrf"]}
        opened = client.post(
            "/api/v1/projects/open", headers=headers, json={"root_id": "work", "path": "audio"}
        ).json()
        base = f"/api/v1/projects/{opened['handle']}"
        path = base + "/episodes/episode.synthetic/audio"
        data = client.get(path).json()
        original = data["episode"]["tracks"]
        asset = next(
            s["asset"] for s in data["sources"] if s["asset"]["id"] == original[0]["asset"]["id"]
        )
        waveform = client.get(
            base + f"/assets/{asset['id']}/{asset['version']}/waveform?bins=8"
        ).json()
        assert len(waveform["bins"]) == 8 and not waveform["silent"]

        def audition(revision):
            response = client.post(
                path + "/audition",
                headers=headers,
                json={"expected_revision": revision, "first_sample": 0, "end_sample": 480000},
            )
            assert response.status_code == 200, response.text
            result = response.json()
            media = client.get(base + f"/audio/auditions/{result['id']}/media")
            assert hashlib.sha256(media.content).hexdigest() == result["report"]["output_sha256"]
            target = tmp_path / f"{result['id']}.wav"
            target.write_bytes(media.content)
            with PCMReader(target) as reader:
                pcm = np.concatenate(
                    [
                        reader.read(start, min(BLOCK_SAMPLES, reader.samples - start))
                        for start in range(0, reader.samples, BLOCK_SAMPLES)
                    ]
                )
            return result["report"], pcm

        before, first = audition(0)
        changed = [
            {
                **t,
                "gain_db": t["gain_db"] - 6.0,
                "fade_in_samples": 48000,
                "fade_out_samples": 48000,
            }
            for t in original
        ]
        saved = client.post(path, headers=headers, json={"expected_revision": 0, "tracks": changed})
        assert saved.status_code == 200, saved.text
        after, second = audition(1)
        assert after["sample_count"] == 480000 and after["over_full_scale_samples"] == 0
        assert before["sample_peak_dbfs"] - after["sample_peak_dbfs"] == pytest.approx(6, abs=0.01)
        np.testing.assert_allclose(
            second[100000:200000], first[100000:200000] * 10 ** (-6 / 20), atol=1e-7
        )
        assert abs(second[0]).max() == 0
        assert (
            client.post(
                path, headers=headers, json={"expected_revision": 0, "tracks": original}
            ).status_code
            == 409
        )
        record = {
            "schema_version": "1.0",
            "document_type": "release_record",
            "id": "test-release",
            "artist": "Synthetic artist",
            "release_title": "Test only",
            "tracks": [
                {
                    "asset": {"id": asset["id"], "version": asset["version"]},
                    "title": "Test tone",
                    "master": asset["files"][0]["location"],
                    "sample_rate": asset["probe"]["sample_rate"],
                    "channels": asset["probe"]["channels"],
                    "duration_samples": asset["probe"]["duration_samples"],
                }
            ],
        }
        result = client.post(base + "/music-metadata", headers=headers, json={"record": record})
        assert result.status_code == 200, result.text
        assert result.json()["tracks"][0]["isrc"] is None and result.json()["upc"] is None
        assert result.json()["tracks"][0]["sha256"] == asset["files"][0]["sha256"]
        bad = {
            **result.json(),
            "tracks": [{**result.json()["tracks"][0], "commercial_use_status": "confirmed"}],
        }
        assert (
            client.post(
                base + "/music-metadata",
                headers=headers,
                json={"record": bad, "expected_revision": 0},
            ).status_code
            == 400
        )
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == h for p, h in sources.items())
