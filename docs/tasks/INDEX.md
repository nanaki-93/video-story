# Ordered implementation tasks

Statuses are recorded below and in each task. Update status and evidence during implementation; see [progress](../progress.md). T01–T05 are complete; T06–T08 need art review while synthetic infrastructure can continue. Contracts were established before media probing. The local web UI replaces Kotlin/Compose in T25–T33. Dependencies are prerequisites for completion; synthetic infrastructure may proceed while real art review is pending. Optional tasks do not block V1.

| Task | Title | Dependencies | Scope | Status |
| --- | --- | --- | --- | --- |
| [T01](t01.md) | Bootstrap repository and developer commands | None | mandatory | complete |
| [T03](t03.md) | Define schemas and safe project persistence | T01 | mandatory | complete |
| [T02](t02.md) | Probe toolchain and renderer capabilities | T01 | mandatory | complete |
| [T04](t04.md) | Generate synthetic fixture pack | T02, T03 | mandatory | complete |
| [T05](t05.md) | Create asset importer and immutable registry | T03, T04 | mandatory | complete |
| [T06](t06.md) | Prepare approved Tabi style and seated sources | T05 | mandatory | source review pending |
| [T07](t07.md) | Author core action pack and transition graph | T06 | mandatory | planned |
| [T08](t08.md) | Prepare train interior and Tokyo environment | T05, T06 | mandatory | planned |
| [T09](t09.md) | Implement global timeline and curves | T03, T04 | mandatory | complete |
| [T10](t10.md) | Compile actions and persistent state | T07, T09 | mandatory | core complete; real-art review pending |
| [T11](t11.md) | Implement scene renderer and window masking | T02, T08, T09 | mandatory | core complete; real-art review pending |
| [T12](t12.md) | Add parallax and scheduled landmarks | T09, T11 | mandatory | complete |
| [T13](t13.md) | Add preview CLI and frozen snapshots | T05, T10, T11, T12 | mandatory | complete |
| [T14](t14.md) | Approve 90 to 120 second visual pilot | T07, T08, T13 | mandatory | real-art inputs and review pending |
| [T15](t15.md) | Implement music import and audio timeline | T03, T05 | mandatory | complete |
| [T16](t16.md) | Mix continuous audio and ambience | T15 | mandatory | core complete; listening review pending |
| [T17](t17.md) | Add restrained lighting rain and reflections | T11, T14 | mandatory | core complete; effect review pending |
| [T18](t18.md) | Author episode continuity and scene transitions | T10, T13, T16, T17 | mandatory | core complete; story review pending |
| [T19](t19.md) | Complete first short music story | T18 | mandatory | original music, approved art and creative review pending |
| [T20](t20.md) | Implement jobs cancellation and persistence | T13 | mandatory | complete |
| [T21](t21.md) | Implement chunk planner and resumable assembly | T16, T18, T20 | mandatory | complete |
| [T22](t22.md) | Implement caches storage estimates and pruning | T05, T21 | mandatory | planned |
| [T23](t23.md) | Verify final export profiles | T02, T21, T22 | mandatory | planned |
| [T24](t24.md) | Build release preparation exporter | T19, T23 | mandatory | planned |
| [T25](t25.md) | Design web app pages and browser playback spike | T03, T13 | mandatory | planned |
| [T26](t26.md) | Implement authenticated local service and worker lifecycle | T20, T25 | mandatory | planned |
| [T27](t27.md) | Implement projects assets and episode setup pages | T05, T25, T26 | mandatory | planned |
| [T28](t28.md) | Implement story editor and timeline | T09, T10, T18, T27 | mandatory | planned |
| [T29](t29.md) | Implement preview and frame inspection page | T13, T26, T28 | mandatory | planned |
| [T30](t30.md) | Implement audio page and release metadata forms | T15, T16, T27 | mandatory | planned |
| [T31](t31.md) | Implement render queue settings and recovery UI | T22, T23, T26 | mandatory | planned |
| [T32](t32.md) | Implement release page and project portability | T24, T30, T31 | mandatory | planned |
| [T33](t33.md) | Package and verify local web app launch | T26, T29, T31, T32 | mandatory | planned |
| [T34](t34.md) | Add café scene template and prove extensibility | T11, T28 | mandatory | planned |
| [T35](t35.md) | Add optional activity and outfit packs | T07, T10, T34 | optional expansion | planned |
| [T36](t36.md) | Add optional local ComfyUI asset bridge | T05, T26 | optional expansion | planned |
| [T37](t37.md) | Benchmark long form and tune resource use | T21, T23, T33, T34 | mandatory reliability | planned |
| [T38](t38.md) | Document operations and complete V1 acceptance | T19, T24, T33, T34, T37 | mandatory | planned |
