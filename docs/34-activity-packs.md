# Activity and outfit packs

`tabi fixtures --profile activities --output ".local/Activity café"` creates a visibly
synthetic café with sipping, reading and sleeping. Each has a six-frame entry, a prepared
twelve-frame loop and a six-frame exit; the compiler fills only complete loops. Cup and book
ownership moves between table and hand and returns to the table before the next activity.
Sleeping owns both body and face channels so an unrelated blink cannot overwrite its eyes.
These short geometric transitions are technical fixtures, not approved animation timing.

An action pack may declare `outfit_id`; its clips explicitly list compatible `outfits`.
A scene declares `character_outfit_id`. The compiler requires the same outfit, camera,
template version, canvas, frame rate and anchor where declared. An outfit change between
scenes requires an authored cut with `continuity: deliberate_reset`. Omitted outfit fields
preserve legacy serialization and hashes; a legacy unspecified pack does not silently fit a
scene that declares a particular outfit.

Story scene cards show exact pack versions, cameras, outfits and approval states. Select a
pack and click **Apply pack to cafe** (or the scene's ID). Python changes all action references
and the scene outfit in one revision-checked save, preserving action IDs, timing and source
media. The replacement must contain every requested action and satisfy all transitions and
prop preconditions. Missing actions or changed loop lengths that no longer fit fail without
modifying the saved episode. Seeded actions and changes across several scenes require an
explicit atomic episode edit. Undo/redo uses the same guarded document mechanism.

Import new authored pack JSON through Assets. Approved versions remain immutable: use a new
version with new media IDs/versions and factual provenance. Approval does not carry over to
the new content. The synthetic blue/amber fixtures demonstrate this mechanism without changing
or claiming to reproduce the supplied Tabi reference.

Four focused checks cover pose/prop schedules, exact pixel endpoints, camera/outfit rejection,
atomic version switching, source preservation and legacy hashes. The real-media gate renders
all transition boundaries and exports 300 frames / 480000 samples in four chunks. Chrome
switched amber → blue at revision 2, rejected a pack missing the activity IDs and reloaded
the preserved blue version. [Pack controls](evidence/t35-pack-controls.jpg).

Representative frames: [sipping](evidence/t35-sipping.png), [reading](evidence/t35-reading.png),
[sleeping](evidence/t35-sleeping.png), [alternate geometric outfit](evidence/t35-outfit.png).
Original Tabi animation, new outfits and artistic review are still pending. None of these
fixtures is production-approved or intended for publication.
