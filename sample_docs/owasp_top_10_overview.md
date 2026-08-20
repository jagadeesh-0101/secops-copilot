# Reference: OWASP Top 10 (Web Application Security Risks)

## Purpose
A high-level summary of the OWASP Top 10 web application security risk categories, for quick reference during design review, code review, or triage. Not a substitute for the full OWASP documentation for any category you're actively working on.

## The Categories

**Broken Access Control** — Users acting outside their intended permissions: viewing or modifying another user's data by changing an ID in a URL, bypassing access checks by modifying a request, or elevating privileges without proper authorization checks. The most commonly reported category in real-world testing.

**Cryptographic Failures** — Sensitive data exposed due to weak or missing encryption: transmitting data over HTTP instead of HTTPS, storing passwords in plaintext or with weak hashing (e.g. unsalted MD5), using outdated TLS versions, or hardcoding cryptographic keys in source code.

**Injection** — Untrusted input executed as code or commands: SQL injection, command injection, LDAP injection, and similar. Occurs when user input is concatenated into a query or command instead of being parameterized or properly escaped.

**Insecure Design** — Security flaws baked into the architecture itself, not fixable by patching an implementation bug — e.g. a password-reset flow with no rate limiting, or a business logic flow that assumes users won't act maliciously.

**Security Misconfiguration** — Default credentials left in place, unnecessary features/ports/services enabled, verbose error messages leaking stack traces, missing security headers, or overly permissive cloud storage settings.

**Vulnerable and Outdated Components** — Using libraries, frameworks, or dependencies with known vulnerabilities, or components that are no longer maintained and receive no security patches.

**Identification and Authentication Failures** — Weak password policies, missing multi-factor authentication, session tokens that don't expire or aren't invalidated on logout, and credential-stuffing-friendly login endpoints (no rate limiting or lockout).

**Software and Data Integrity Failures** — Trusting software updates, CI/CD pipelines, or serialized data without verifying integrity — e.g. auto-updaters that don't verify digital signatures, or deserializing untrusted data without validation.

**Security Logging and Monitoring Failures** — Insufficient logging of security-relevant events (logins, access-control failures, high-value transactions), or logs that exist but nobody monitors, delaying breach detection from hours to months.

**Server-Side Request Forgery (SSRF)** — An application fetches a remote resource without validating the user-supplied URL, allowing an attacker to make the server issue requests to internal-only systems (e.g. cloud metadata endpoints) it shouldn't be able to reach.

## How to use this in practice
Treat this as a checklist during design and code review, not a standalone control. Each category maps to concrete, testable controls (parameterized queries for injection, MFA for authentication failures, dependency scanning for outdated components) — the category name alone doesn't fix anything.
