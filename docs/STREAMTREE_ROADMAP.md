
# Streamtree Roadmap

This roadmap is aligned with the dependency and packaging approach in [STREAMTREE_DEPENDENCY_STRATEGY.md](./STREAMTREE_DEPENDENCY_STRATEGY.md) (base vs optional extras, wrapper-first public API).

---

# Phase 0 — Foundation

## Goals
- Establish package architecture
- Build core rendering concepts
- Validate developer ergonomics
- Lock dependency philosophy: small **hard** set, heavier stacks **opt-in** via extras

## Deliverables
- Element base classes
- Component decorator
- Tree renderer
- Basic Streamlit renderer
- Minimal documentation
- **`pyproject.toml` aligned with strategy:** documented install tiers (`streamtree`, `[tables]`, `[charts]`, `[ui]`, `[auth]`, `[dev]`, `[all]`) and rationale (see plan + dependency strategy doc)

---

# Phase 1 — MVP

## Goals
- Build a usable application framework
- Preserve Streamlit simplicity
- Deliver core layout primitives

## Features

### Elements
- Text
- Markdown
- Button
- TextInput
- NumberInput
- SelectBox
- Checkbox
- DataFrame
- Image

### Layouts
- VStack
- HStack
- Grid
- Columns
- Tabs
- Sidebar
- Form
- Card

### State
- state()
- toggle_state()
- form_state()
- session_state()

### Rendering
- render()
- component identity
- key management

## Dependency alignment (MVP)
- Ship **core** with the **hard** dependency set from the strategy (`streamlit`, `pydantic`, `typing-extensions`, `streamlit-extras`) once wrappers are ready; until then document any gap vs the strategy doc
- Introduce **Pydantic** for typed component props and early form models where MVP scope allows
- Add **curated** `streamlit-extras`-backed helpers only behind stable Streamtree names (avoid exposing the full grab bag)

## Deliverables
- pip-installable package
- documentation
- examples
- demo applications
- **Base dependencies** per strategy: `streamlit`, `pydantic`, `typing-extensions`, `streamlit-extras` (only **curated** surfaces in `streamtree.*`, not blanket re-exports)
- **Stub or document optional extras** in `pyproject.toml` (`tables`, `charts`, `ui`, `auth`, `all`) even if wrappers land in later phases

---

# Phase 2 — Application Features

## Goals
- Support real production applications

## Features
- Routing
- Page system
- Query param synchronization
- Typed forms (Pydantic-first models and validation)
- Validation helpers
- Theme system
- Authentication abstractions

## Optional dependency alignment
- **`[auth]` extra:** `streamlit-authenticator` (+ shared helpers such as `extra-streamlit-components` where needed), wrapped as `AuthProvider`, protected routes, or similar—document limitations and future pluggable providers
- **`[ui]` extra:** use `streamlit-shadcn-ui` / `extra-streamlit-components` only behind Streamtree components (badges, alerts, modern cards, tab bars, cookie/router helpers) to avoid API leakage

## Deliverables
- App object
- Navigation framework
- Theme engine
- Form builder

---

# Phase 3 — Data Application Toolkit

## Goals
- Become the best architecture layer for data apps

## Features
- Data tables
- CRUD scaffolding
- Filtering systems
- Query state management
- Dashboard layouts
- Chart wrappers

## Optional dependency alignment
- **`[tables]` extra:** `streamlit-aggrid` (or equivalent) behind elements such as `DataGrid` (selectable, editable, filterable rows)
- **`[charts]` extra:** `plotly`, `streamlit-echarts`, `altair` behind elements such as `Chart`, `LineChart`, `EChart`—declarative specs where it matches Streamtree’s model

## Deliverables
- Admin dashboard templates
- Data exploration toolkit
- Enterprise data components

---

# Phase 4 — Testing and Tooling

## Goals
- Enable enterprise-scale development workflows

## Features
- Snapshot testing
- render_to_tree()
- Component assertions
- Storybook-style previews
- Devtools
- State inspection

## Optional dependency alignment
- **`[dev]` extra:** `pytest`, `ruff`, `mypy` as the standard contributor and CI toolchain (see dependency strategy)

## Deliverables
- pytest integration
- Component preview server
- Visual regression tooling

---

# Phase 5 — Ecosystem Expansion

## Goals
- Expand beyond Streamlit-only rendering

## Features
- FastAPI renderer
- Static HTML renderer
- Alternate runtime support
- Plugin architecture (optional backends and extras register through Streamtree, not ad-hoc direct imports)

## Deliverables
- Multi-renderer abstraction
- Plugin SDK
- Extension registry

---

# Long-Term Vision

Streamtree becomes:
- the architecture layer for Streamlit
- a Python-native UI framework ecosystem
- a production-grade application platform

Potential ecosystem packages:
- streamtree-auth
- streamtree-testing
- streamtree-fastapi
- streamtree-admin
- streamtree-charts
- streamtree-enterprise
