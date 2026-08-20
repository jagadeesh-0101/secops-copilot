# Runbook: Data Loss Prevention (DLP) Incident Handling

## Purpose
Defines how to respond when a DLP policy trigger fires, across severity tiers.

## Severity Tiers
- **Low**: Policy trigger involving internal transfer of moderately sensitive data (e.g., internal-only documents shared with another internal team).
- **Medium**: Sensitive data (PII, financial data) sent externally to a known/verified business partner.
- **High**: Sensitive data sent to an unverified or personal external destination (personal email, unsanctioned cloud storage).
- **Critical**: Confirmed intentional exfiltration of sensitive data, or a pattern of repeated policy violations by the same user.

## Response Steps
1. Review the DLP alert details: policy triggered, data classification, source user, destination.
2. Determine whether the transfer was blocked automatically or only logged/alerted.
3. If not blocked and severity is High or Critical, contact the user's manager and, if applicable, HR/Legal before further action.
4. Interview the user (or review available context) to determine intent: accidental misconfiguration vs. deliberate exfiltration.
5. For confirmed accidental incidents: provide user coaching, verify the data was not accessed by unauthorized parties, and close with documentation.
6. For confirmed intentional exfiltration: preserve all evidence (logs, the DLP alert, any related HR context) and escalate to Legal/HR per the organization's incident response policy immediately.
7. Review whether the DLP policy that fired needs tuning (too noisy, too permissive, or missing a data type).

## Documentation Requirements
Every DLP incident, regardless of severity, must be logged with: trigger time, policy name, user, data classification, destination, and final disposition (false positive, coached, escalated).
