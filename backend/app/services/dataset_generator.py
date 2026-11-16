import random
from typing import List, Dict, Any, Tuple


DOMAINS = [
    {
        "domain": "Information Security",
        "doc": "Global Information Security Policy",
        "templates": [
            ("All employees must rotate personal workstation passwords every 90 days.", "rotate", "personal workstation passwords"),
            ("System administrators must enable multi-factor authentication on all administrative portals.", "enable", "multi-factor authentication"),
            ("Cloud engineers must store cryptographic keys in certified hardware security modules.", "store", "cryptographic keys"),
            ("Database administrators must encrypt database backups at rest using AES-256.", "encrypt", "database backups"),
            ("Security analysts must review access control logs on a weekly basis.", "review", "access control logs"),
            ("Employees must not share user account credentials with colleagues or third parties.", "share", "user account credentials"),
            ("Engineers must apply security patches to operating systems within 14 days of release.", "apply", "security patches"),
            ("Personnel must lock computer screens upon leaving workstations unattended.", "lock", "computer screens"),
            ("Staff must report security incidents immediately to the SOC helpline.", "report", "security incidents"),
            ("Developers must not disable endpoint protection software on corporate machines.", "disable", "endpoint protection software"),
        ],
    },
    {
        "domain": "Data Privacy",
        "doc": "Customer Data Privacy Protocol",
        "templates": [
            ("Data custodians must anonymize customer personal data prior to analytical modeling.", "anonymize", "customer personal data"),
            ("Privacy officers must delete inactive user profiles after 24 months of dormancy.", "delete", "inactive user profiles"),
            ("Marketing personnel must obtain explicit user consent prior to sending promotional emails.", "obtain", "explicit user consent"),
            ("Engineers must restrict access to raw credit card numbers to PCI-DSS certified systems.", "restrict", "access to raw credit card numbers"),
            ("Compliance leads must maintain records of processing activities under GDPR Article 30.", "maintain", "records of processing activities"),
            ("Staff must not export unencrypted customer personally identifiable information to personal drives.", "export", "unencrypted customer information"),
            ("System operators must log all access to sensitive customer health records.", "log", "access to sensitive records"),
            ("Product teams must conduct privacy impact assessments prior to launching new features.", "conduct", "privacy impact assessments"),
            ("Representatives must verify requester identity before honoring subject access requests.", "verify", "requester identity"),
            ("Database engineers must mask sensitive customer identifiers in test environments.", "mask", "sensitive customer identifiers"),
        ],
    },
    {
        "domain": "Travel and Expense",
        "doc": "Corporate Travel and Reimbursement Standard",
        "templates": [
            ("Traveling personnel must book domestic airfare through the corporate travel management portal.", "book", "domestic airfare"),
            ("Employees must submit expense claims with receipts within 30 days of trip completion.", "submit", "expense claims"),
            ("Business travelers must limit hotel accommodations to the standard approved city caps.", "limit", "hotel accommodations"),
            ("Staff may claim a standard daily meal allowance when traveling on business for more than 8 hours.", "claim", "daily meal allowance"),
            ("Managers must review and approve subordinate expense reports within 5 business days.", "review", "subordinate expense reports"),
            ("Travelers must not use luxury limousine services without prior executive approval.", "use", "luxury limousine services"),
            ("Employees must provide itemized receipts for all entertainment expenditures exceeding $50.", "provide", "itemized receipts"),
            ("Staff should select non-refundable standard economy seats when available.", "select", "standard economy seats"),
            ("Travelers must notify corporate security prior to high-risk international travel.", "notify", "corporate security"),
            ("Employees must return unused foreign currency cash advances within 10 days of return.", "return", "unused cash advances"),
        ],
    },
    {
        "domain": "Remote Work",
        "doc": "Remote Work and Telecommuting Guidelines",
        "templates": [
            ("Telecommuters must connect via company VPN when accessing internal infrastructure.", "connect", "company VPN"),
            ("Remote workers must maintain a secure and private home office workspace.", "maintain", "secure home office"),
            ("Employees must attend scheduled core-hour video team meetings.", "attend", "video team meetings"),
            ("Staff must immediately notify IT of home router or network security breaches.", "notify", "IT of security breaches"),
            ("Remote workers should maintain high-speed broadband connections meeting company requirements.", "maintain", "high-speed broadband"),
            ("Telecommuters must not allow non-employees to use company-provided hardware.", "allow", "non-employees to use hardware"),
            ("Employees must keep software update schedules active on remote laptops.", "keep", "software update schedules"),
            ("Staff must obtain prior management approval before working from an alternative international location.", "obtain", "prior management approval"),
            ("Remote personnel should take regular ergonomic breaks throughout the workday.", "take", "ergonomic breaks"),
            ("Employees must return all remote hardware upon request from IT asset management.", "return", "remote hardware"),
        ],
    },
    {
        "domain": "Procurement",
        "doc": "Vendor Procurement and Sourcing Policy",
        "templates": [
            ("Procurement buyers must solicit at least three competitive quotes for purchases over $25,000.", "solicit", "three competitive quotes"),
            ("Contract managers must execute signed non-disclosure agreements prior to vendor discussions.", "execute", "signed non-disclosure agreements"),
            ("Category leads must perform financial due diligence on strategic supplier candidates.", "perform", "financial due diligence"),
            ("Staff must not accept gifts or gratuities from suppliers exceeding $50 in value.", "accept", "gifts or gratuities from suppliers"),
            ("Legal counsel must review all non-standard commercial vendor contracts.", "review", "non-standard vendor contracts"),
            ("Purchasing agents must verify budget availability prior to issuing purchase orders.", "verify", "budget availability"),
            ("Project managers must track supplier deliverables against established contractual milestones.", "track", "supplier deliverables"),
            ("Buyers should prioritize environmentally sustainable vendors when commercially viable.", "prioritize", "sustainable vendors"),
            ("Finance leads must enforce net-45 payment terms on standard commercial supplier invoices.", "enforce", "net-45 payment terms"),
            ("Contracting officers must archive executed supplier agreements in the central contract repository.", "archive", "executed supplier agreements"),
        ],
    },
    {
        "domain": "Software Development",
        "doc": "Secure Software Engineering Lifecycle",
        "templates": [
            ("Software engineers must require peer code approval from at least one senior committer.", "require", "peer code approval"),
            ("Developers must run automated security vulnerability scans before merging code.", "run", "automated security vulnerability scans"),
            ("Release managers must deploy software updates to staging environments prior to production release.", "deploy", "software updates to staging"),
            ("Engineers must not commit plain-text credentials or API secrets to version control.", "commit", "plain-text credentials to git"),
            ("Architects must document system architecture decisions in version-controlled records.", "document", "system architecture decisions"),
            ("QA engineers must execute regression test suites before staging sign-off.", "execute", "regression test suites"),
            ("Developers must write automated unit tests covering all new business logic modules.", "write", "automated unit tests"),
            ("Teams should maintain test code coverage above 80 percent across all microservices.", "maintain", "test code coverage above 80%"),
            ("Engineers must tag production releases with semantic version numbers.", "tag", "production releases with semver"),
            ("DevOps personnel must isolate staging and production cloud infrastructure networks.", "isolate", "staging and production networks"),
        ],
    },
    {
        "domain": "Incident Response",
        "doc": "Cybersecurity Incident Management Protocol",
        "templates": [
            ("Incident responders must document all forensic timeline actions during an active incident.", "document", "forensic timeline actions"),
            ("Operations teams must isolate infected virtual machines within 30 minutes of malware alert.", "isolate", "infected virtual machines"),
            ("Incident commanders must brief executive leadership within two hours of Sev-1 confirmation.", "brief", "executive leadership"),
            ("Security engineers must preserve digital evidence chain of custody according to NIST guidelines.", "preserve", "digital evidence chain of custody"),
            ("Teams must conduct blameless post-mortem reviews within 7 days of incident closure.", "conduct", "blameless post-mortem reviews"),
            ("Staff must not communicate incident specifics to external press without PR authorization.", "communicate", "incident specifics to press"),
            ("System leads must rotate all exposed credentials following incident containment.", "rotate", "exposed credentials"),
            ("Security operations must maintain on-call escalation rosters with 24/7 responsiveness.", "maintain", "on-call escalation rosters"),
            ("Responders should retain memory dumps before rebooting compromised hosts.", "retain", "memory dumps before reboot"),
            ("Incident managers must archive final post-incident reports in the security portal.", "archive", "final post-incident reports"),
        ],
    },
    {
        "domain": "Asset Management",
        "doc": "Corporate IT Asset and Hardware Policy",
        "templates": [
            ("Inventory specialists must barcode and record every new company laptop upon receipt.", "barcode", "new company laptop"),
            ("Employees must return all assigned hardware assets upon termination of employment.", "return", "assigned hardware assets"),
            ("Support staff must wipe decommissioned storage drives in compliance with DoD standards.", "wipe", "decommissioned storage drives"),
            ("Personnel must not perform unauthorized physical modifications to company hardware.", "perform", "unauthorized physical modifications"),
            ("IT administrators must run bi-annual physical audits of server room equipment.", "run", "bi-annual physical audits"),
            ("Employees should transport company laptops in protective padded carrying sleeves.", "transport", "company laptops in padded sleeves"),
            ("Asset managers must renew hardware support warranties prior to OEM expiration dates.", "renew", "hardware support warranties"),
            ("Field personnel must register portable testing equipment before taking items offsite.", "register", "portable testing equipment"),
            ("IT specialists must verify user eligibility before issuing loaner laptop equipment.", "verify", "user eligibility for loaner laptops"),
            ("Staff must report lost or stolen hardware devices within 4 hours of discovery.", "report", "lost or stolen hardware devices"),
        ],
    },
    {
        "domain": "Workplace Conduct",
        "doc": "Employee Code of Ethics and Professional Conduct",
        "templates": [
            ("All employees must treat colleagues, clients, and partners with respect and dignity.", "treat", "colleagues with respect"),
            ("Personnel must report suspected legal or ethics violations through the anonymous helpline.", "report", "suspected ethics violations"),
            ("Staff must complete mandatory annual compliance and anti-bribery training modules.", "complete", "annual compliance training"),
            ("Employees must not engage in insider trading based on material non-public information.", "engage", "in insider trading"),
            ("Managers must foster an inclusive and discrimination-free work environment.", "foster", "inclusive work environment"),
            ("Staff must declare potential personal conflicts of interest to the compliance officer.", "declare", "potential conflicts of interest"),
            ("Supervisors must not retaliate against employees who raise good-faith compliance concerns.", "retaliate", "against whistleblowers"),
            ("Personnel should avoid personal use of company communications systems for outside commercial gain.", "avoid", "personal use of systems"),
            ("Employees must disclose secondary outside employment or board directorships.", "disclose", "secondary outside employment"),
            ("Staff must protect proprietary company trade secrets from unauthorized external disclosure.", "protect", "proprietary trade secrets"),
        ],
    },
    {
        "domain": "Document Retention",
        "doc": "Enterprise Records Management and Archival Schedule",
        "templates": [
            ("Financial controllers must retain corporate tax records for a minimum of seven years.", "retain", "corporate tax records"),
            ("HR coordinators must archive terminated employee personnel files for five years.", "archive", "terminated personnel files"),
            ("Legal staff must preserve all relevant documents subject to an active legal hold notice.", "preserve", "documents under legal hold"),
            ("Records officers must shred confidential paper records using cross-cut industrial shredders.", "shred", "confidential paper records"),
            ("Project teams must archive final project delivery artifacts upon contract completion.", "archive", "final project artifacts"),
            ("Staff must not destroy documents that are the subject of an ongoing regulatory audit.", "destroy", "documents under audit"),
            ("Facility managers must maintain physical archive room climate controls at stable levels.", "maintain", "archive room climate controls"),
            ("Records custodians must catalog digital archives with searchable metadata tags.", "catalog", "digital archives with metadata"),
            ("Compliance teams must conduct annual audits of record disposal certification logs.", "conduct", "audits of disposal certification logs"),
            ("Staff should minimize unnecessary duplication of electronic files across shared servers.", "minimize", "unnecessary file duplication"),
        ],
    },
]


def generate_synthetic_rules_dataset(
    min_rules: int = 505,
    seed: int = 42,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Generates a reproducible dataset containing at least 500 mutually consistent
    background rules, plus 6 specifically planted ground-truth conflict pairs.
    """
    random.seed(seed)
    rules_data: List[Dict[str, Any]] = []
    ground_truth_conflicts: List[Dict[str, Any]] = []
    rule_idx = 1

    # 1. Generate clean non-conflicting background rules (10 domains x 10 unique templates = 100 core rules)
    # Replicate across organizational subsidiaries/departments with distinct identifiers and slight phrasing variation
    subsidiaries = [
        "Global Corporate", "North America Division", "EMEA Operations", 
        "APAC Regional", "Cloud Services Unit", "Payment Technologies Sub"
    ]

    for sub in subsidiaries:
        for domain_info in DOMAINS:
            doc_title = f"{sub} - {domain_info['doc']}"
            for text, action, obj in domain_info["templates"]:
                rule_id = f"SYN-{rule_idx:04d}"
                rules_data.append({
                    "rule_id": rule_id,
                    "domain": domain_info["domain"],
                    "source_document": doc_title,
                    "source_section": f"Section {random.randint(1, 8)}.{random.randint(1, 4)}",
                    "text": text,
                    "effective_date": "2024-01-01",
                })
                rule_idx += 1
                if len(rules_data) >= min_rules - 15:
                    break
            if len(rules_data) >= min_rules - 15:
                break
        if len(rules_data) >= min_rules - 15:
            break

    # 2. Plant Exactly 6 Distinct Ground-Truth Conflicts Across All Categories

    # Conflict 1: Direct Contradiction
    c1_a = f"SYN-{rule_idx:04d}"
    rules_data.append({
        "rule_id": c1_a,
        "domain": "Information Security",
        "source_document": "Central IT Security Policy",
        "source_section": "Section 3.1 - Backup Locations",
        "text": "Cloud engineers must store production database backups in the primary us-east-1 region.",
        "effective_date": "2024-01-01",
    })
    rule_idx += 1

    c1_b = f"SYN-{rule_idx:04d}"
    rules_data.append({
        "rule_id": c1_b,
        "domain": "Information Security",
        "source_document": "Disaster Recovery Guideline",
        "source_section": "Section 5.4 - Regional Restrictions",
        "text": "Cloud engineers must not store production database backups in the primary us-east-1 region.",
        "effective_date": "2024-01-01",
    })
    rule_idx += 1

    ground_truth_conflicts.append({
        "rule_a_id": c1_a,
        "rule_b_id": c1_b,
        "expected_category": "Direct contradiction",
        "planted_reason": "Opposing modalities (must vs must not) for storing production database backups.",
    })

    # Conflict 2: Conditional Contradiction
    c2_a = f"SYN-{rule_idx:04d}"
    rules_data.append({
        "rule_id": c2_a,
        "domain": "Travel and Expense",
        "source_document": "Corporate Travel Policy",
        "source_section": "Section 4.1 - Receipt Limits",
        "text": "Employees must submit expense claims with receipts for all purchases exceeding $25.",
        "effective_date": "2024-01-01",
    })
    rule_idx += 1

    c2_b = f"SYN-{rule_idx:04d}"
    rules_data.append({
        "rule_id": c2_b,
        "domain": "Travel and Expense",
        "source_document": "Executive Travel Addendum",
        "source_section": "Section 1.2 - Executive Limits",
        "text": "Employees must submit expense claims with receipts for all purchases exceeding $100.",
        "effective_date": "2024-01-01",
    })
    rule_idx += 1

    ground_truth_conflicts.append({
        "rule_a_id": c2_a,
        "rule_b_id": c2_b,
        "expected_category": "Conditional contradiction",
        "planted_reason": "Incompatible condition thresholds ($25 vs $100).",
    })

    # Conflict 3: Missing Exception
    c3_a = f"SYN-{rule_idx:04d}"
    rules_data.append({
        "rule_id": c3_a,
        "domain": "Information Security",
        "source_document": "Endpoint Security Standard",
        "source_section": "Section 2.1 - Removable Media",
        "text": "Employees must not connect external USB storage drives, except encrypted hardware keys approved by IT.",
        "effective_date": "2024-01-01",
    })
    rule_idx += 1

    c3_b = f"SYN-{rule_idx:04d}"
    rules_data.append({
        "rule_id": c3_b,
        "domain": "Information Security",
        "source_document": "Zero Trust Architecture Directive",
        "source_section": "Section 4.3 - Hardware Restrictions",
        "text": "Employees must not connect external USB storage drives under any circumstances.",
        "effective_date": "2024-01-01",
    })
    rule_idx += 1

    ground_truth_conflicts.append({
        "rule_a_id": c3_a,
        "rule_b_id": c3_b,
        "expected_category": "Missing exception",
        "planted_reason": "Endpoint Standard includes exception for encrypted hardware keys which Zero Trust directive omits.",
    })

    # Conflict 4: Superseded Rule
    c4_a = f"SYN-{rule_idx:04d}"
    rules_data.append({
        "rule_id": c4_a,
        "domain": "Information Security",
        "source_document": "Authentication Standard 2023",
        "source_section": "Section 2.1 - Password Rotation",
        "text": "Database administrators must rotate production database passwords every 90 days.",
        "effective_date": "2023-01-01",
    })
    rule_idx += 1

    c4_b = f"SYN-{rule_idx:04d}"
    rules_data.append({
        "rule_id": c4_b,
        "domain": "Information Security",
        "source_document": "Authentication Standard 2024",
        "source_section": "Section 2.1 - Password Lifecycle",
        "text": "Database administrators may retain production database passwords without rotation when FIDO2 MFA is active.",
        "effective_date": "2024-01-01",
    })
    rule_idx += 1

    ground_truth_conflicts.append({
        "rule_a_id": c4_b,
        "rule_b_id": c4_a,
        "expected_category": "Superseded rule",
        "planted_reason": "2024 Authentication standard modifies rotation terms from 2023 without explicit deprecation.",
    })

    # Conflict 5: Ambiguous Instruction (Single rule)
    c5_a = f"SYN-{rule_idx:04d}"
    rules_data.append({
        "rule_id": c5_a,
        "domain": "Remote Work",
        "source_document": "Remote Work Policy",
        "source_section": "Section 4.2 - General Safeguards",
        "text": "Remote personnel should take all commercially reasonable and appropriate measures to safeguard corporate assets.",
        "effective_date": "2024-01-01",
    })
    rule_idx += 1

    ground_truth_conflicts.append({
        "rule_a_id": c5_a,
        "rule_b_id": None,
        "expected_category": "Ambiguous instruction",
        "planted_reason": "Contains 'commercially reasonable and appropriate measures' with no objective criteria.",
    })

    # Conflict 6: Harmless Wording Change
    c6_a = f"SYN-{rule_idx:04d}"
    rules_data.append({
        "rule_id": c6_a,
        "domain": "Software Development",
        "source_document": "Engineering Manual v1",
        "source_section": "Section 3.1 - Peer Reviews",
        "text": "Software engineers must require peer code approval from at least one senior committer.",
        "effective_date": "2024-01-01",
    })
    rule_idx += 1

    c6_b = f"SYN-{rule_idx:04d}"
    rules_data.append({
        "rule_id": c6_b,
        "domain": "Software Development",
        "source_document": "Engineering Manual v2",
        "source_section": "Section 3.1 - Committer Approvals",
        "text": "Software engineers must obtain peer code approval from at least one senior committer.",
        "effective_date": "2024-01-01",
    })
    rule_idx += 1

    ground_truth_conflicts.append({
        "rule_a_id": c6_a,
        "rule_b_id": c6_b,
        "expected_category": "Harmless wording change",
        "planted_reason": "Minor synonym change ('require' vs 'obtain') preserving identical legal requirement.",
    })

    ground_truth_dataset = {
        "metadata": {
            "total_rules": len(rules_data),
            "planted_conflicts": len(ground_truth_conflicts),
            "categories_covered": [
                "Direct contradiction",
                "Conditional contradiction",
                "Missing exception",
                "Superseded rule",
                "Ambiguous instruction",
                "Harmless wording change",
            ],
            "seed": seed,
        },
        "conflicts": ground_truth_conflicts,
    }

    return rules_data, ground_truth_dataset
