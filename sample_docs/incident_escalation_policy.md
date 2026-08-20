# Policy: Security Incident Escalation

## Purpose
Defines who gets notified, and how fast, once an incident is confirmed above a given severity.

## Severity Definitions
- **SEV-4 (Low)**: No business impact, contained automatically or by standard triage.
- **SEV-3 (Medium)**: Limited business impact, contained by the on-shift analyst without additional support.
- **SEV-2 (High)**: Significant business impact, or containment requires cross-team coordination (IT, network, application owners).
- **SEV-1 (Critical)**: Active, ongoing compromise with material business impact (data breach, ransomware, production outage caused by a security event).

## Escalation and Notification Timelines
- **SEV-1**: Notify Incident Response lead and CISO within 15 minutes of confirmation. Stand up an incident bridge within 30 minutes. Notify Legal and executive leadership within 1 hour.
- **SEV-2**: Notify Incident Response lead within 1 hour. Notify affected system/application owners immediately.
- **SEV-3**: Notify Incident Response lead by end of shift if not already resolved.
- **SEV-4**: No proactive notification required; included in the weekly security summary.

## Roles During a SEV-1/SEV-2 Incident
- **Incident Commander**: Owns overall coordination and status communication; usually the Incident Response lead.
- **Technical Lead**: Owns containment and remediation actions.
- **Communications Lead**: Owns internal/external status updates and, if needed, coordinates with Legal/PR on breach notification obligations.

## Post-Incident Requirements
Every SEV-1 and SEV-2 incident requires a written post-incident review within 5 business days, covering: root cause, timeline, what worked, what didn't, and follow-up action items with owners and due dates.
