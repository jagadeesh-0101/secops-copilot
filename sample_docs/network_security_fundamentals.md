# Reference: Network Security Fundamentals

## Purpose
A high-level summary of core network security concepts, architectures, and controls essential for analyzing network-based indicators and alerts.

## Firewalls
Devices or software that monitor and control incoming and outgoing network traffic based on predetermined security rules. They establish a barrier between a trusted network and an untrusted network (like the Internet). Modern Next-Generation Firewalls (NGFW) also include deep packet inspection, intrusion prevention, and application-level awareness.

## Intrusion Detection and Prevention Systems (IDS/IPS)
Systems that monitor network traffic for suspicious activity and known threats. An **IDS** only detects and alerts on the activity (out-of-band), while an **IPS** is placed inline and can actively block or drop the malicious traffic before it reaches the target.

## Virtual Private Network (VPN)
A technology that creates a safe and encrypted connection over a less secure network, such as the Internet. Used to provide remote workers secure access to internal corporate networks, ensuring data transmitted is protected from interception.

## Demilitarized Zone (DMZ)
A physical or logical subnetwork that contains and exposes an organization's external-facing services (web servers, email servers, DNS) to an untrusted network, usually the Internet. It adds an extra layer of security to an organization's local area network (LAN), as external attackers only have direct access to equipment in the DMZ.

## Network Segmentation
The practice of splitting a computer network into subnetworks, each being a network segment. This limits the "blast radius" of an intrusion; if an attacker compromises one segment, they cannot easily pivot and move laterally to other segments (e.g., keeping guest Wi-Fi completely isolated from internal financial systems).

## Zero Trust Architecture
A security framework requiring all users, whether in or outside the organization's network, to be authenticated, authorized, and continuously validated before being granted or keeping access to applications and data. It assumes that there is no traditional network edge and that threats exist both inside and outside.

## DNS Sinkholing
A mechanism aimed at protecting users by intercepting DNS requests attempting to connect to known malicious domains and returning a false IP address. This prevents the malware from communicating with its command and control (C2) servers or users from reaching phishing sites.

## Proxy Server
An intermediary server that sits between client applications and other servers. **Forward proxies** protect the clients by inspecting outbound traffic and masking their IPs. **Reverse proxies** sit in front of web servers to protect them, often providing load balancing, web application firewall (WAF) capabilities, and SSL termination.
