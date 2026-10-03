# Tabi Story Studio implementation plan

Prepared 3 October 2026 for Marco. This is an implementation handoff, not an implemented application or a finished asset pack.

Build a local macOS production application for original Tabi music stories. Reuse approved artwork and controlled animation; author each episode's development; automate validation, previews, assembly, and exports. Melotrail provides finished music. DistroKid distribution and YouTube publishing remain separate manual operations in V1.

## Start here

1. Read [PLAN.md](PLAN.md) for scope, decisions, milestones, and completion gates.
2. Read [AGENTS.md](AGENTS.md) before modifying the eventual application repository.
3. Read [asset production](docs/01-assets.md), [architecture](docs/02-architecture.md), [contracts](docs/03-contracts.md), [rendering](docs/04-rendering.md), [desktop UX](docs/05-desktop.md), [publishing](docs/06-publishing.md), and [QA](docs/07-qa.md).
4. Execute the [task index](docs/tasks/INDEX.md) in dependency order. Each task has its own specification.
5. Use the [agent kickoff](templates/agent-kickoff.md) to start the first implementation session.

Examples are contract illustrations using synthetic IDs and nonexistent media paths. They are not production assets or executable application code. The implementation agent must generate schemas and make them pass validation before calling the examples runnable.

## Package contents

The master plan defines the full product through V1 and its expansion path. Detailed documents provide asset inventories and prompt briefs, timeline semantics, CLI and service contracts, rendering recovery, every desktop page, music and rights handoffs, acceptance criteria, and target-machine verification. The task folder splits this into independently reviewable work units.

Human review is reserved for art direction, original music, episode storytelling, rights decisions, and release. A coding agent can proceed with clearly labeled synthetic assets while those inputs are unavailable.
