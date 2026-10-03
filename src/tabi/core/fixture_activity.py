"""Geometric entry/loop/exit and outfit fixtures; no new Tabi design or approval."""

from PIL import ImageDraw

from .documents import validate_data


def activity_frame(color, *, sip=0, read=0, sleep=0, breath=0):
    from .fixtures import body_frame

    image = body_frame(0, breath)
    draw = ImageDraw.Draw(image)
    draw.rectangle((26, 46 - breath, 70, 85), fill=(*color, 255))
    if sleep:
        for x in (36, 52):
            draw.rectangle((x, 27, x + 4, 30), fill=(244, 184, 120, 255))
            draw.line((x, 29, x + 4, 29), fill=(32, 48, 64, 255))
    # The same objects are always visible, resting on the table or owned by the hands.
    cup_x, cup_y = 73 - sip * 3, 59 - sip * 5
    draw.line((67, 56, cup_x + 5, cup_y + 7), fill=(244, 184, 120, 255), width=3)
    draw.rectangle((cup_x, cup_y, cup_x + 10, cup_y + 12), fill=(236, 218, 154, 255))
    draw.rectangle((cup_x + 11, cup_y + 3, cup_x + 13, cup_y + 8), outline=(236, 218, 154, 255))
    book_x, book_y = 8 + read * 4, 62 - read * 2
    draw.rectangle((book_x, book_y, book_x + 24, book_y + 9), fill=(208, 222, 190, 255))
    draw.line((book_x + 12, book_y, book_x + 12, book_y + 9), fill=(72, 92, 72, 255))
    return image


def populate_activities(store, register, episode):
    def ref(identity):
        return {"id": identity, "version": "1.0"}

    for outfit, color in (("blue", (72, 164, 188)), ("amber", (192, 132, 64))):
        outfit_id = f"fixture.outfit.{outfit}"
        actions = []

        def add(
            name,
            frames,
            start,
            end,
            *,
            loop=False,
            requires=None,
            resulting=None,
            outfit=outfit,
            outfit_id=outfit_id,
            actions=actions,
        ):
            asset_id = f"fixture.activity.{outfit}.{name}"
            register(asset_id, frames, kind="sequence", channels=["body"], outfits=[outfit_id])
            actions.append(
                {
                    **ref(f"fixture.activity.{name}"),
                    "channel": "body",
                    "clip": ref(asset_id),
                    "start_pose": start,
                    "end_pose": end,
                    "frame_count": len(frames),
                    "kind": "loop" if loop else "one_shot",
                    "loop": {"start_frame": 0, "end_frame": len(frames)} if loop else None,
                    "occupies_channels": ["body", "face"] if name.startswith("sleep") else ["body"],
                    "requires_props": requires or {},
                    "resulting_props": resulting or {},
                }
            )

        breathing = (0, 1, 1, 2, 2, 1, 1, 0, -1, -1, 0, 0)
        resting = {"cup": "table", "book": "table"}
        add(
            "idle",
            [activity_frame(color, breath=n) for n in breathing],
            "idle",
            "idle",
            loop=True,
            requires=resting,
        )
        for name, parameter, prop in (
            ("sip", "sip", "cup"),
            ("read", "read", "book"),
            ("sleep", "sleep", None),
        ):
            held = {**resting, **({prop: "hand"} if prop else {})}
            entry = [activity_frame(color, **{parameter: n}) for n in range(6)]
            add(f"{name}.entry", entry, "idle", name, requires=resting, resulting=held)
            add(
                name,
                [activity_frame(color, **{parameter: 5}, breath=n) for n in breathing],
                name,
                name,
                loop=True,
                requires=held,
            )
            add(
                f"{name}.exit",
                list(reversed(entry)),
                name,
                "idle",
                requires=held,
                resulting=resting,
            )
        pack = validate_data(
            {
                "schema_version": "1.0",
                "document_type": "action_pack",
                **ref(f"pack.synthetic.activities.{outfit}"),
                "camera_id": "fixture.camera",
                "outfit_id": outfit_id,
                "template": ref("scene.synthetic.cafe"),
                "canvas": {"width": 96, "height": 96},
                "anchor": {"x": 48, "y": 92},
                "fps": {"num": 30, "den": 1},
                "alpha_mode": "straight",
                "actions": actions,
            }
        )
        store.save_draft(pack, expected_revision=None)
    data = episode.model_dump(mode="json")
    data["title"] = "SYNTHETIC café activities and outfit compatibility"
    data["scenes"][0].update(
        character_outfit_id="fixture.outfit.blue",
        initial_state={"body_pose": "idle", "props": {"cup": "table", "book": "table"}},
        purpose="Exercise sipping, reading and sleeping with explicit prop ownership.",
    )
    data["actions"] = [
        {
            "id": f"activity-{name}",
            "scene_id": "cafe",
            "pack": ref("pack.synthetic.activities.blue"),
            "action_id": f"fixture.activity.{name}",
            "version": "1.0",
            "channel": "body",
            "start_frame": start,
            "end_frame": end,
            "repeat": "loop_to_fill",
            "return_pose": "idle",
        }
        for name, start, end in (
            ("idle", 0, 48),
            ("sip", 48, 132),
            ("read", 132, 216),
            ("sleep", 216, 300),
        )
    ]
    data["beats"] = []
    data["continuity"] = {
        "summary": "Synthetic props return to the table after every activity.",
        "objects": ["cup", "book"],
        "object_notes": {"cup": "Table → hand → table", "book": "Table → hand → table"},
    }
    return validate_data(data)
