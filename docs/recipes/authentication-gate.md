# Authentication gate

## Goal

Wrap authenticated subtrees behind **`AuthGate`** using **`streamlit-authenticator`** with
StreamTree’s thin builder API.

## Install

```bash
pip install "streamtree[auth]"
```

Treat authenticator **config as trusted secrets**—never commit real credentials to git.

## Pattern

Full demo:

```python
--8<-- "examples/auth_demo.py"
```

Run (after you supply a real config dict in your own app):

```bash
streamlit run examples/auth_demo.py
```

## Integration notes

- **`streamtree.auth.build_authenticator`** returns objects the renderer expects when it
  mounts **`AuthGate`**.
- Keep **login UI** and **post-login shell** as separate subtrees so reruns do not recreate
  expensive authenticator state unnecessarily.
- Alternate identity providers (OIDC, SSO) remain **app-wrapped** until a pinned StreamTree
  abstraction exists ([Roadmap](../ROADMAP.md), [Dependency strategy](../DEPENDENCY_STRATEGY.md)).

## See also

- [App shell, theme & context](app-theme-context.md)
- [Layouts & error boundaries](layout-shells.md)
- [Examples](../EXAMPLES.md)
