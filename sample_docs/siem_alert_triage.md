# Runbook: SIEM Alert Triage (Splunk)

## Purpose
Standardize how analysts triage inbound SIEM alerts so that response time and quality stay consistent regardless of who is on shift.

## Triage Priority Order
1. Alerts tagged `critical` or involving privileged/admin accounts.
2. Alerts involving data exfiltration indicators (large outbound transfers, uploads to personal cloud storage, unusual DNS query volume).
3. Alerts involving authentication anomalies (impossible travel, brute-force patterns, MFA bypass attempts).
4. Everything else, in order received.

## Standard Triage Steps
1. Read the raw alert and identify the triggering rule and the asset(s) involved.
2. Pull the surrounding 30 minutes of log activity for the source host/user to establish context.
3. Determine whether this is a true positive, false positive, or benign-but-expected activity (e.g., a known backup job).
4. If true positive: classify severity, open a case, and begin containment steps appropriate to the alert type.
5. If false positive: document the reason and consider whether the detection rule needs tuning to reduce future noise.
6. Update the shift handoff log with any alert still open at the end of the shift, including current status and next steps.

## Common Alert Types and First Actions
- **Multiple failed logins followed by success**: check for brute-force pattern, verify the successful login's source IP/geography against the user's normal pattern.
- **Large outbound data transfer**: identify destination, check DLP logs for matching policy triggers, confirm whether the transfer was sanctioned.
- **New scheduled task or service created**: check the creating account's privilege level and recent activity; correlate with EDR process-creation logs.
- **Antivirus/EDR detection with no automatic remediation**: manually isolate the host if the detection is not confirmed benign within 15 minutes.

## Service-Level Targets
- Critical alerts: initial triage within 15 minutes.
- High alerts: initial triage within 1 hour.
- Medium/Low alerts: initial triage within one shift.
