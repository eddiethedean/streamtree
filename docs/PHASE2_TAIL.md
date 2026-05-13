# Phase 2 backlog — follow-up work (post-0.6.0)

This note listed **larger Phase 2 themes** beyond the **0.6.0** slice. Most items have **shipped** through **0.9.0**; what remains is **stretch** or belongs to **Phase 3 / 4**. For shipped detail, see [ROADMAP.md](./ROADMAP.md) and [CHANGELOG.md](CHANGELOG.md).

## Phase 2 closure checklist (0.9.0)

Phase 2 is considered **feature-complete for the application track** when all of the following are true (met by **0.9.0**):

- **Navigation / multipage:** stdlib `pages/` discovery plus **sectioned sidebar helpers** and documented **`Routes` vs multipage** guidance.
- **Imperative edge (URL):** `routing` helpers for **batch query updates** and **clearing** params / routes where Streamlit allows.
- **Forms:** layout grid supports **bool** (and docs for **batch / `Form`** semantics).
- **`[ui]` breadth:** additional **streamlit-extras** wrappers shipped behind the extra.
- **Async slice:** **batch `dismiss_task`** and docs; no new async backends in Phase 2.
- **Auth:** extension limits documented (optional provider abstraction deferred).
- **Examples:** composite **ErrorBoundary** + **context** + **async** patterns linked from the roadmap.

## Richer navigation and app shell

- **Shipped in 0.8.0:** **`page_links`**, **`init --with-pages`**, **`App(sidebar=..., body=...)`**.
- **Shipped in 0.9.0:** **`iter_page_entries`**, **`prefetch_page_sources`**, **`SplitView`** (pseudo-sidebar), **portals**.
- **Shipped in 0.9.0:** **`group_page_entries_by_order_prefix`**, **`page_links_sidebar_sections`**, **`multipage_sidebar_nav`**; README / docs on **`Routes` + query params** vs **`pages/`** multipage.
- **Still stretch:** opinionated **templates** that tightly couple **`Routes`** + **`App`** (beyond helpers and docs).

## `streamtree.asyncio` orchestration

- **Shipped in 0.7.0–0.8.0:** `submit_many`, cooperative cancel, **`dismiss_task`**.
- **Shipped in 0.9.0:** **`dismiss_tasks`** (batch terminal cleanup) and doc polish.
- **Deferred (Phase 3+):** new worker backends, non-thread pools, heavy composition frameworks.

## Form builder

- **Shipped in 0.9.0:** **`streamtree.forms_layout`** — scalar **str** / **numeric** grid + **`build_model_from_bindings`**.
- **Shipped in 0.9.0:** **bool** fields in layout grid + design note [PHASE2_FORMS.md](./PHASE2_FORMS.md).
- **Deferred (Phase 3):** rich data widgets (date ranges, file uploads, nested models) unless kept thin and stdlib-only.

## `streamlit-extras` breadth

- **Shipped in 0.8.0–0.9.0:** ColoredHeader, VerticalSpaceLines, SocialBadge, StyleMetricCards, BottomDock, FloatingActionButton.
- **Shipped in 0.9.0:** **Stoggle**, **TaggerRow**, **MentionChip** (see CHANGELOG).
- **Ongoing:** more wrappers behind **`[ui]`** as maintainers curate pins (see [DEPENDENCY_STRATEGY.md](./DEPENDENCY_STRATEGY.md)).

## Imperative handles

- **Documented:** README “Imperative handles (limits)” and [PHASE2_PORTALS_AND_PREFETCH.md](./PHASE2_PORTALS_AND_PREFETCH.md).
- **Shipped in 0.9.0:** extra **`routing`** helpers for **multi-key** query updates and **clear** operations (no DOM focus/scroll APIs).

## Auth

- **`[auth]`** remains **`streamlit-authenticator`** via **`AuthGate`**.
- **0.9.0:** README + dependency strategy document **extension limits** and custom-credential patterns; **no** mandatory `AuthProvider` protocol in this release.

## References

- [PHASE2_PORTALS_AND_PREFETCH.md](./PHASE2_PORTALS_AND_PREFETCH.md) — portals, prefetch, layout-form baseline.
- [PHASE2_FORMS.md](./PHASE2_FORMS.md) — extended form layout (bool, `Form` batch notes).
- [ROADMAP.md](ROADMAP.md) — phase table and release index.
- [PLAN.md](PLAN.md) — packaging philosophy.
- [DEPENDENCY_STRATEGY.md](DEPENDENCY_STRATEGY.md) — pins and optional stacks.
