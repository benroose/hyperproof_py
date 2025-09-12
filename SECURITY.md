# Security Guidelines

This document outlines recommended practices for securely using the Hyperproof Python API wrapper and summarizes relevant security considerations implemented by the library.

## Library security posture

- Authentication: OAuth2 Client Credentials (M2M) to obtain access tokens over HTTPS.
- Token handling: Authorization headers are never logged. Authentication parameters and responses are not logged.
- Logging: The library uses a module logger with a NullHandler by default; it does not configure console handlers or log at DEBUG unless your application opts in. Avoid enabling DEBUG in production.
- Network resiliency: Requests use default timeouts and limited retries with jitter; 429/5xx backoff is observed. TLS verification is enabled by default via `requests`.

## Your responsibilities and best practices

- Least privilege: Create API clients with minimal required scopes/roles. Rotate client secrets regularly.
- Secret storage: Store `CLIENT_ID` and `CLIENT_SECRET` in a secret manager or environment variables, not in code or VCS. Prefer a `.env` file only for local development.
- Logging hygiene: Do not log tokens, Authorization headers, or sensitive payloads. Keep application logging at INFO/WARNING in production.
- Dependency hygiene: Keep dependencies patched. Use pinned versions and a dependable scanning tool in CI.
- Network controls: Restrict egress to Hyperproof endpoints. Use HTTPS only.
- Input handling: Validate and sanitize any user-provided inputs you feed into API calls (filenames, search terms) to avoid injection in downstream consumers.
- Principle of minimal data: Request only data you need; avoid fetching full collections unnecessarily.
- Monitoring: Monitor API usage, rate limits, and error patterns. Alert on unusual spikes or repeated failures.

## Config recommendations

- Use a `.env` for local development:
```bash
CLIENT_ID="your_client_id"
CLIENT_SECRET="your_client_secret"
```
- In production, use a secret manager (AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault, etc.).
- Override application-level logging; do not enable debug logging for this library in production.

## Reporting vulnerabilities

If you believe you’ve found a security issue in this repository, please open a private disclosure channel (e.g., email the maintainer) rather than filing a public issue first. Provide steps to reproduce and impacted versions.