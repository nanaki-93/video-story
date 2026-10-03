# Café template engineering proof

Generate a separate reproducible project with:

```sh
.venv/bin/tabi fixtures --profile cafe --output ".local/Café proof"
```

Open that folder in Projects. Its saved episode appears in Story, Timeline, Audio and Preview
using the same authoring/preview services as the train fixture. The template is
`scene.synthetic.cafe@1.0`, the explicitly compatible pack is `pack.synthetic.cafe@1.0`, and
the character anchor is `at-table` at design pixel (145, 300), rather than the train's seat.
The original geometric actor clips are reused under their declared camera compatibility.
A train pack does not implicitly become compatible just because its clips look similar.

The café has a static room and street, a distinct grayscale window mask, a tabletop in front
of the actor, a transparent repeating cloud layer and one scheduled pedestrian silhouette.
The shared `travel_speed` curve is a horizontal outside-motion coordinate: 24 design pixels
per second for the pedestrian, multiplied by 0.08 for the clouds. It never moves the room or
street. The renderer/compiler contains no café or train-name branch. Prepared pedestrian
walk-cycle animation and approved artwork remain future asset authoring; this fixture tests
placement and one-shot passage, not realistic walking.

The integration check edits the motion curve through `EditorService`, renders three exact
frames and a two-chunk ten-second proxy, and verifies frame/sample counts. Pixel checks prove
stationary architecture, masked cloud motion, the different character anchor, tabletop
occlusion and pedestrian movement. The unit check rejects a train-only pack and proves
repeatable generation. [Representative frame](evidence/t34-cafe-frame.png).

All artwork and audio are synthetic and cannot receive production approval. This proves the
scene extension architecture; it does not reproduce Tabi, qualify café art or approve a release.
