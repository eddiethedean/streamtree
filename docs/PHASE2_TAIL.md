# Phase 2 backlog — follow-up work (post-0.6.0)

This note captures **larger or cross-cutting** Phase 2 themes that are intentionally **not** part of the **0.6.0** slice. Use it to groom releases after [`streamtree init`](https://github.com/streamtree-dev/streamtree/blob/main/src/streamtree/cli.py), **[`auth`]**, **overlays** (`Dialog` / `Popover`), and the first **[`ui`]`** wrappers ship.

## Richer navigation and app shell

- Route prefetch, second-sidebar patterns, and generators for `pages/` trees.
- Tighter coupling between **`streamtree.helpers.pages`** discovery and **`Routes`** / **`App`** conventions (templates produced by **`streamtree init`**).

## `streamtree.asyncio` orchestration

- **Shipped in 0.7.0:** `submit_many`, cooperative cancel (`is_task_cancel_requested`, `complete_cancelled`), and stale-key documentation on the asyncio module.
- Further ideas: richer composition, cancellation UX polish, route prefetch (overlaps some Phase 3 language in the roadmap but remains fair game here).

## Form builder

- Layout-aware forms, batch submit, and validation UX beyond scalar string + numeric fields (likely spans Phase 2 forms and Phase 3 data work); treat as its own small design note before coding.

## `streamlit-extras` breadth

- Additional curated wrappers behind **`[ui]`** (badges, metric cards, etc.) without expanding the default install.

## References

- [ROADMAP.md](ROADMAP.md) — Phase 2 backlog table and release index.
- [PLAN.md](PLAN.md) — packaging philosophy and optional extras.
- [DEPENDENCY_STRATEGY.md](DEPENDENCY_STRATEGY.md) — pins, limits, and security posture for optional stacks.
