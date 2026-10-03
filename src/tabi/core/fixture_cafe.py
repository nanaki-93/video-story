"""Stationary café engineering fixture, not proposed Tabi artwork."""

from PIL import Image, ImageDraw

from .documents import validate_data
from .models.base import AssetRef
from .render.synthetic import label


def populate_cafe(store, register, pack, episode):
    def ref(identity):
        return AssetRef(id=identity, version="1.0").model_dump()

    pixels = bytearray(bytes((92, 64, 56)) * 640 * 360)
    label(pixels, 640, "SYNTHETIC CAFE", 20, 16, 2)
    label(pixels, 640, "NOT FOR PUBLICATION", 20, 336, 2)
    room = Image.frombytes("RGB", (640, 360), bytes(pixels))
    draw = ImageDraw.Draw(room)
    draw.rectangle((235, 45, 599, 249), fill=(204, 162, 108))
    draw.rectangle((0, 312, 639, 330), fill=(62, 44, 42))
    register("fixture.cafe.room", [room])
    mask = Image.new("L", (640, 360))
    ImageDraw.Draw(mask).rectangle((245, 55, 589, 239), fill=255)
    register("fixture.cafe.window", [mask], kind="mask")

    street = Image.new("RGB", (640, 360), (164, 204, 220))
    draw = ImageDraw.Draw(street)
    for x in (220, 310, 400, 490, 580):
        draw.rectangle((x, 135, x + 65, 215), fill=(148, 170, 156))
        draw.rectangle((x + 14, 155, x + 34, 178), fill=(230, 202, 152))
    draw.rectangle((0, 216, 639, 359), fill=(132, 134, 142))
    register("fixture.cafe.street", [street])
    cloud = Image.new("RGBA", (640, 360))
    draw = ImageDraw.Draw(cloud)
    for x in (40, 260, 480):
        draw.ellipse((x, 73, x + 84, 94), fill=(244, 242, 224, 230))
    strip = Image.new("RGBA", (1280, 360))
    strip.paste(cloud, (0, 0))
    strip.paste(cloud, (640, 0))
    register("fixture.cafe.clouds", [strip])
    pedestrian = Image.new("RGBA", (24, 48))
    draw = ImageDraw.Draw(pedestrian)
    draw.ellipse((7, 2, 17, 12), fill=(232, 176, 128))
    draw.rectangle((5, 13, 19, 33), fill=(76, 108, 152))
    draw.line((9, 33, 4, 46), fill=(48, 54, 68), width=4)
    draw.line((15, 33, 21, 46), fill=(48, 54, 68), width=4)
    register("fixture.cafe.pedestrian", [pedestrian])
    table = Image.new("RGBA", (640, 360))
    draw = ImageDraw.Draw(table)
    draw.rectangle((56, 280, 223, 294), fill=(176, 120, 76))
    draw.rectangle((77, 295, 89, 328), fill=(116, 78, 58))
    draw.rectangle((200, 295, 212, 328), fill=(116, 78, 58))
    register("fixture.cafe.table", [table])

    template = validate_data(
        {
            "schema_version": "1.0",
            "document_type": "scene_template",
            **ref("scene.synthetic.cafe"),
            "camera_id": pack.camera_id,
            "design_canvas": {"width": 640, "height": 360},
            "capabilities": ["travel", "landmarks", "body", "face"],
            "channels": ["body", "face"],
            "anchors": {"at-table": {"x": 145, "y": 300}, "pavement": {"x": 0, "y": 176}},
            "mask_semantics": "white_visible_black_hidden",
            "parameter_limits": {"travel_speed": {"minimum": 0, "maximum": 30}},
            "slots": [
                {"id": "room", "z": 0, "kind": "still", "asset": ref("fixture.cafe.room")},
                {
                    "id": "street",
                    "z": 1,
                    "kind": "still",
                    "asset": ref("fixture.cafe.street"),
                    "mask": ref("fixture.cafe.window"),
                },
                {
                    "id": "clouds",
                    "z": 2,
                    "kind": "tile_strip",
                    "asset": ref("fixture.cafe.clouds"),
                    "mask": ref("fixture.cafe.window"),
                    "tile_period": 640,
                    "depth_factor": 0.08,
                },
                {
                    "id": "pedestrians",
                    "z": 3,
                    "kind": "scheduled_sprite",
                    "anchor": "pavement",
                    "mask": ref("fixture.cafe.window"),
                },
                {"id": "actor", "z": 4, "kind": "character", "anchor": "at-table"},
                {"id": "table", "z": 5, "kind": "still", "asset": ref("fixture.cafe.table")},
            ],
        }
    )
    store.save_draft(template, expected_revision=None)
    # Same explicit camera/media, separately declared template compatibility. No inferred pack fit.
    data = pack.model_dump(mode="json")
    data.update(id="pack.synthetic.cafe", template=ref(template.id), revision=0)
    cafe_pack = validate_data(data)
    store.save_draft(cafe_pack, expected_revision=None)
    data = episode.model_dump(mode="json")
    data.update(title="SYNTHETIC café — stationary room and slow outside motion")
    scene = data["scenes"][0]
    scene.update(
        id="cafe",
        template=ref(template.id),
        anchor="at-table",
        purpose="Rest at a stationary table while clouds and one pedestrian pass the window.",
        final_state=None,
    )
    for action in data["actions"]:
        action.update(scene_id="cafe", pack=ref(cafe_pack.id))
    data["curves"] = [
        {
            "scope": "cafe",
            "target": "travel_speed",
            "unit": "design_px_per_second",
            "interpolation": "constant",
            "limits": {"minimum": 0, "maximum": 30},
            "keys": [{"frame": 0, "value": 24}],
        }
    ]
    data["events"] = [
        {
            "type": "landmark",
            "id": "pedestrian.once",
            "scene_id": "cafe",
            "slot_id": "pedestrians",
            "asset": ref("fixture.cafe.pedestrian"),
            "start_frame": 30,
            "end_frame": 270,
            "world_x": 580,
        }
    ]
    data["beats"] = [
        {
            "id": "window-observation",
            "scene_id": "cafe",
            "start_frame": 90,
            "end_frame": 210,
            "summary": "Look toward the café window",
            "purpose": "Test reused entry/loop/exit media at a different composition anchor.",
            "music_placements": ["tone"],
        }
    ]
    return validate_data(data)
