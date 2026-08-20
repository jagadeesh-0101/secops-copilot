# Reference: Common Attack Types Glossary

## Purpose
Short, plain-language definitions of attack types that come up constantly in security operations, written for quick lookup rather than academic completeness.

## Phishing
A social-engineering attack using deceptive email, text, or messages to trick someone into revealing credentials, clicking a malicious link, or executing a malicious attachment. **Spear phishing** targets a specific individual using personal context; **whaling** targets executives specifically.

## Credential Stuffing
Attackers use lists of usernames/passwords leaked from other breaches and try them against a different service, betting on password reuse. Distinct from brute-forcing, which guesses passwords rather than replaying known-real ones.

## Ransomware
Malware that encrypts a victim's files (or threatens to leak stolen data — "double extortion") and demands payment for decryption or non-disclosure. Typically spreads after an initial foothold (phishing, exposed RDP, an unpatched vulnerability) followed by lateral movement to maximize impact before detonating.

## SQL Injection
Untrusted input is inserted into a database query without proper parameterization, letting an attacker manipulate the query — extracting data, bypassing authentication, or in severe cases modifying/deleting data. Prevented with parameterized queries/prepared statements, not string sanitization alone.

## Cross-Site Scripting (XSS)
Malicious script is injected into a web page and executed in another user's browser, typically because user-supplied input is rendered without proper output encoding. Can be used to steal session cookies, perform actions as the victim, or deface content.

## Man-in-the-Middle (MitM)
An attacker intercepts (and potentially alters) communication between two parties who believe they're communicating directly with each other — e.g. on an unsecured public Wi-Fi network, or via a compromised network device. TLS/HTTPS with proper certificate validation is the primary defense.

## Denial of Service (DoS) / Distributed Denial of Service (DDoS)
Overwhelming a system with traffic or resource-exhausting requests so legitimate users can't access it. "Distributed" means the traffic comes from many sources at once (often a botnet), making it harder to block by simply denying a single IP.

## Privilege Escalation
Gaining access beyond what was originally granted — **vertical** escalation moves from a low-privilege account to a higher one (user to admin); **horizontal** escalation accesses another account at the same privilege level (another user's data).

## Zero-Day
A vulnerability that is exploited before the vendor has released (or in some cases even become aware of) a patch. "Zero days" refers to the amount of time the vendor has had to respond.

## Supply Chain Attack
Compromising a trusted third-party component — a software dependency, a build pipeline, a vendor with system access — to reach the actual target indirectly. Effective because the victim's own controls often implicitly trust that third party.

## Business Email Compromise (BEC)
A targeted social-engineering attack, usually impersonating an executive or vendor, aimed at tricking someone into an unauthorized wire transfer or sensitive-data disclosure — often no malware involved at all, just convincing pretext and urgency.
