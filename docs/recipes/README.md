# Recipes

Cookbook-style patterns you can copy, adapt, and ship. These pages focus on **how** to
assemble StreamTree for common product shapes. For architecture and dependency rules,
see the **Guides** section (Plan, Roadmap, Dependency strategy, Performance, Phase 2/3
docs). For **every line** of each runnable script under `examples/`, see
**[Examples (full source)](../EXAMPLES.md)**.

## Quick map

| You want to… | Start here | Representative `examples/` script |
|----------------|------------|-------------------------------------|
| Boot the smallest `@component` app | [First app & components](first-app-and-components.md) | `counter.py` |
| Mix `st.*` with elements / `fragment()` | [Streamlit interop](streamlit-interop.md) | README patterns |
| Scope `state()`, memo, anonymous keys | [State, session & memo](state-session-and-memo.md) | `model_form.py`, `counter.py` |
| Pydantic-first forms and widgets | [Forms & validation](forms-and-validation.md) | `model_form.py` |
| URL routes and query-driven UI | [Routing & URLs](routing-and-urls.md) | `routed_app.py` |
| Background work + loading branches | [Async & loading](async-and-loading.md) | `async_loader_demo.py`, `async_bg.py` |
| Streamlit `pages/` sidebar | [Multipage navigation](multipage-navigation.md) | `pages_helpers_demo.py` |
| `App`, theme, shared context | [App shell, theme & context](app-theme-context.md) | `app_shell.py` |
| Layout primitives and resilience | [Layouts & error boundaries](layout-shells.md) | `phase2_composite_demo.py` |
| AgGrid / Plotly / Altair / ECharts | [Data grids & charts](data-grids-and-charts.md) | `datagrid_demo.py`, `chart_demo.py` |
| Login gate | [Authentication gate](authentication-gate.md) | `auth_demo.py` |
| `streamtree` CLI and scaffolds | [CLI & scaffolding](cli-and-scaffolding.md) | `streamtree_run_demo.md` |
| Portals, split shell, deferred regions | [Portals & deferred UI](portals-and-deferred.md) | `phase2_composite_demo.py`, `deferred_region_demo.py` |
| File structure and cross-cutting concerns | [Organizing large apps](organizing-large-apps.md) | `phase2_composite_demo.py` |
| List/detail/save + async orchestration | [List / detail / save (CRUD)](crud-list-detail-save.md) | `crud_pattern_demo.py`, `crud_automation_demo.py` |
| Counters, events, debugging | [Observability & ops](observability-and-ops.md) | `enterprise`-related patterns in docs |

## Recipe style

Each recipe lists **goal**, **what you install**, **core ideas**, and **one runnable shape**
(usually a shortened script or a pointer to an embedded example). Prefer **stable `key=`**
on widgets Streamlit requires keys for, and keep **one navigation model** per app
(multipage `pages/` *or* in-script `Routes`, not both fighting each other—see Roadmap).

When something needs an optional extra (`[tables]`, `[charts]`, `[auth]`, `[ui]`),
the recipe says so up front so default `pip install streamtree` users are not surprised.
