## Contributing

Thanks for contributing to **Inclusive Credit Infrastructure**.

### Principles

- **Transparency-first**: design for auditability and explanation.
- **Privacy-first**: minimize data; protect sensitive attributes; document data flows.
- **Safety-first**: prefer conservative defaults; require explicit opt-in for risky behavior.
- **Non-commercial, public benefit posture**: keep the core implementation open and reusable.

### Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[api,dev]"
```

### Run tests and lint

```bash
make test
make lint
```

### Pull requests

- Keep PRs small and focused.
- Add or update tests for behavior changes.
- Update `docs/` if you change governance/security/compliance semantics.


