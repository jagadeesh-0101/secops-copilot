# Runbook: Phishing Email Response

## Trigger
A user reports a suspicious email, or a phishing simulation/awareness platform flags a real click-through.

## Severity Classification
- **Low**: Suspicious email reported, no user interaction (no click, no reply, no attachment opened).
- **Medium**: Link clicked, but no credentials entered and no attachment executed.
- **High**: Credentials entered on a phishing page, or an attachment was opened/executed.
- **Critical**: Confirmed credential compromise on a privileged account, or evidence of lateral movement following the click.

## Response Steps
1. Acquire the original email (headers included) from the reporting user or mail gateway quarantine.
2. Extract indicators of compromise (IOCs): sender address, reply-to address, links, attachment hashes.
3. Check IOCs against threat intelligence feeds and internal blocklists.
4. If the link was clicked, pull proxy/EDR logs for the affected host to confirm whether the page rendered or a payload executed.
5. If credentials were entered, force a password reset for the affected account and review recent authentication logs for anomalous logins (new geography, new device, impossible travel).
6. Block the sender domain and any malicious URLs at the email gateway and web proxy.
7. Notify affected user(s) and their manager if the incident is Medium severity or above.
8. Document the full timeline: initial report time, containment time, and remediation actions.

## Escalation
Escalate to the Incident Response lead immediately if severity is High or Critical, or if more than 5 users received the same campaign.

## Metrics to Track
- Time from report to containment.
- Percentage of employees who reported vs. clicked during simulated phishing campaigns (target: reported rate trending up, click rate trending down quarter over quarter).
