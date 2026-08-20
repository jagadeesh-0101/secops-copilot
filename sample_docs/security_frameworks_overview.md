# Reference: Common Security Frameworks

## Purpose
A quick-orientation summary of the security frameworks most commonly referenced in industry — what each one actually is, who typically uses it, and how they differ. Useful for answering "what's the difference between X and Y" without digging through each framework's full documentation.

## NIST Cybersecurity Framework (CSF)
A voluntary framework organized around six functions: **Govern, Identify, Protect, Detect, Respond, Recover**. It doesn't prescribe specific controls — it's a common vocabulary and structure for organizing a security program and communicating maturity to leadership. Widely used in the US across both government and private sector because it's flexible and framework-agnostic (an organization can map its existing controls onto CSF categories rather than starting over).

## ISO/IEC 27001
An international, certifiable standard for an Information Security Management System (ISMS) — the actual management process (risk assessment, policies, continuous improvement) rather than a specific technical checklist. Organizations can be formally audited and certified against it, which matters for vendors selling into enterprises or regulated industries that require proof of a functioning security program, not just good intentions.

## CIS Controls
A prioritized, more prescriptive set of specific technical and procedural safeguards (currently organized into implementation groups by organizational maturity/resources). Where NIST CSF answers "what functions should our program cover," CIS Controls answers "what specific things should we actually configure and do" — inventory of assets, secure configuration baselines, access control management, and so on. Often used alongside CSF rather than instead of it.

## SOC 2
An auditing standard (not a security framework per se) built around five Trust Services Criteria: security, availability, processing integrity, confidentiality, and privacy. A SOC 2 report is what one company shows another as evidence its security practices are sound — extremely common in B2B SaaS due diligence and vendor security reviews.

## PCI DSS
A mandatory standard (not voluntary) for any organization that stores, processes, or transmits credit card data. Highly prescriptive with specific technical requirements (network segmentation, encryption of cardholder data, quarterly vulnerability scans). Non-compliance carries real financial and contractual consequences with payment processors.

## MITRE ATT&CK
Not a compliance framework — a knowledge base of real-world adversary tactics, techniques, and procedures (TTPs), organized by attack lifecycle stage (initial access, execution, persistence, privilege escalation, and so on). Used by defenders to map detection coverage ("do we have visibility into technique T1059?") and by red teams to structure realistic attack simulations.

## How these relate
A mid-size company might use NIST CSF to structure the overall program, CIS Controls to decide what to actually implement first, pursue SOC 2 to satisfy customer security reviews, and reference MITRE ATT&CK when building detection rules — these aren't competing choices, they solve different problems and are frequently used together.
