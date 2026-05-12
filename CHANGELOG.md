# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-05-12

### Added

- Initial public API: `@component`, `render`, virtual elements (`Page`, layouts, widgets).
- Session helpers: `state`, `toggle_state`, `form_state`, `session_state`, `memo`, `cache`.
- Streamlit renderer mapping the virtual tree to `st.*` calls (including `Form` and submit flows).
- `streamtree.testing.render_to_tree` for structure-focused tests without a live Streamlit session.
- Runnable example: `examples/counter.py`.
- Design docs under `docs/` (plan, roadmap, dependency strategy).

[0.1.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.1.0
