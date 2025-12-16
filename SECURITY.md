## Security Policy

### Reporting a vulnerability

If you discover a security issue, please do not open a public issue with exploit details.
Instead, report it privately to the maintainers.

Include:

- A clear description of the issue and impact
- Steps to reproduce
- Affected versions/commit
- Suggested mitigation (if known)

### Security posture (high-level)

This repo implements:

- **Model and decision audit logs** (tamper-evident by convention; see `docs/THREAT_MODEL.md`)
- **Least-privilege defaults** (no sensitive attributes used in models by default)
- **Config-driven secrets** (no secrets committed to the repo)


