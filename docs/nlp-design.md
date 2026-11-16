# PolicyDiff - NLP & Conflict Detection Design

## 1. Objective
Transform complex natural language compliance sentences into atomic, formal deontic logic tuples, and execute deterministic and semantic contradiction analysis.

## 2. Structured Rule Representation

Each extracted policy statement is formalized as a normalized 9-tuple:
```python
class StructuredRule:
    rule_id: str             # e.g., "SEC-V1-R014"
    subject: str             # Governing subject ("All full-time employees")
    obligation: ObligationType  # MUST | MUST_NOT | SHOULD | MAY | CANNOT
    action: str              # Canonical action verb phrase ("retain")
    object: str              # Target entity/object ("system audit logs")
    conditions: list[str]    # Prerequisites ("for a minimum period of 365 days")
    exceptions: list[str]    # Carve-outs ("unless requested earlier by subpoena")
    source_document: str     # Document title/ID
    source_section: str      # Section name/number & character offsets
```

### Deontic Modality Mapping
| Modal Token in Text | Canonical Obligation | Meaning |
|---|---|---|
| *must*, *shall*, *is required to*, *will ensure* | `MUST` | Mandatory affirmative duty |
| *must not*, *shall not*, *prohibited*, *forbidden* | `MUST_NOT` | Strict prohibition |
| *should*, *ought to*, *is recommended*, *advised* | `SHOULD` | Strong recommendation |
| *may*, *is permitted to*, *is authorized to* | `MAY` | Discretionary permission |
| *cannot*, *are not allowed to*, *ineligible* | `CANNOT` | Incapacity / Negative permission |

## 3. Linguistic Extraction Pipeline (spaCy + Heuristics)

```
[Policy Text / Paragraph]
           │
           ▼
[Sentence Segmentation]
           │
           ▼
[Modal Pattern Matcher (Matcher/PhraseMatcher)]
   ├── Check for obligation / prohibition markers
   └── Discard non-normative narrative sentences
           │
           ▼
[Dependency Parse Analysis]
   ├── nsubj / csubj        -> Subject
   ├── ROOT / aux / xcomp   -> Action (Verb + modifiers)
   ├── dobj / pobj / attr   -> Object / Target
   ├── mark + advcl (if/when) -> Condition clauses
   └── prep / mark (unless/except) -> Exception clauses
           │
           ▼
[Entity & Acronym Resolution]
           │
           ▼
[Canonical Structured Rule]
```

## 4. Conflict Taxonomy & Detection Matrix

Conflicts are detected across policies or across versions by categorizing pairwise interactions:

### 4.1 Conflict Categories

1. **Direct Contradiction (`DIRECT_CONTRADICTION`)**
   - **Criteria**: Rule $A$ and Rule $B$ share identical or synonymous Subject and Action/Object, but have opposite modalities.
   - **Example**:
     - *Policy A (Data Retention)*: "Engineers **must** store production backups in us-east-1."
     - *Policy B (Disaster Recovery)*: "Engineers **must not** store backups in us-east-1 during transition."
   - **Severity**: `CRITICAL`

2. **Conditional Contradiction (`CONDITIONAL_CONTRADICTION`)**
   - **Criteria**: Both rules allow or mandate an action, but establish mutually incompatible conditions.
   - **Example**:
     - *Policy A*: "Expense reports over \$500 require Director approval."
     - *Policy B*: "Expense reports over \$250 require VP approval only."
   - **Severity**: `HIGH`

3. **Missing Exception (`MISSING_EXCEPTION`)**
   - **Criteria**: Rule $A$ provides a specific exemption or fallback path, but Rule $B$ (often an updated version or blanket company rule) imposes an unyielding mandate without the exception.
   - **Example**:
     - *Policy v1*: "All external USB devices are blocked, except encrypted corporate hardware."
     - *Policy v2*: "No external USB devices may be connected under any circumstances."
   - **Severity**: `HIGH`

4. **Superseded Rule (`SUPERSEDED_RULE`)**
   - **Criteria**: A newer policy version modifies deadlines, thresholds, or contacts without explicitly referencing or revoking the predecessor rule.
   - **Example**:
     - *IT Policy 2023*: "Passwords expire every 90 days."
     - *IT Policy 2024*: "Passwords never expire; FIDO2 MFA is enforced."
   - **Severity**: `MEDIUM`

5. **Ambiguous Instruction (`AMBIGUOUS_INSTRUCTION`)**
   - **Criteria**: Single rule containing vague quantifiers or subjective obligations without measurable criteria.
   - **Triggers**: "reasonable effort", "appropriate security", "in a timely manner", "regularly", "as needed".
   - **Severity**: `LOW` to `MEDIUM`

6. **Harmless Wording Change (`HARMLESS_WORDING_CHANGE`)**
   - **Criteria**: Text differs in phrasing, grammar, or passive-to-active voice, but the deontic modality, subject, action, conditions, and exceptions are logically equivalent.
   - **Example**:
     - *Old*: "Reports shall be filed by the employee by 5 PM."
     - *New*: "Employees must submit their reports by 5:00 PM."
   - **Severity**: `INFO`

## 5. NetworkX Graph Model for Cascading Dependencies
PolicyDiff models policy rules as a directed multigraph $G = (V, E)$:
- **Nodes ($V$)**: Individual `ExtractedRule` nodes enriched with metadata (category, source, effective date).
- **Edges ($E$)**: Relational predicates:
  - `CONTRADICTS`: Bidirectional or directed conflict edge.
  - `SUPERSEDES`: Directed edge from newer rule to older rule.
  - `EXEMPTS`: Directed edge from rule establishing an exception to target rule.
  - `DEPENDS_ON`: Prerequisite dependency between policies.

Graph algorithms identify:
- **Connected Conflict Components**: Subgraphs of interconnected conflicting guidelines.
- **Cycles**: Inconsistent circular rules (Rule A requires B, Rule B requires C, Rule C forbids A).
