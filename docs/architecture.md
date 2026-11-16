# PolicyDiff - System Architecture

## 1. System Overview
PolicyDiff is designed as a decoupled full-stack application for automated policy governance and contradiction detection. It ingests enterprise documents, structures unstructured text into atomic deontic rules, analyzes relationships between rules, and surfaces conflicts for compliance review.

```
       +---------------------------------------------+
       |           Frontend (React + Vite)           |
       |  - Policy Diff Viewer    - Rule Inspector   |
       |  - Conflict Workbench   - Review Actions   |
       +----------------------+----------------------+
                              |  REST API / JSON
                              v
       +---------------------------------------------+
       |             Backend (FastAPI)               |
       |  - Document Management & Ingestion          |
       |  - Parsing Service (PyMuPDF & python-docx)  |
       |  - Rule Extraction Engine (spaCy NLP)       |
       |  - Conflict Detection Engine (Deontic Matrix|
       |    & NetworkX Graph Analyzer)               |
       +----------------------+----------------------+
                              |  SQLAlchemy 2.0 ORM
                              v
       +---------------------------------------------+
       |           PostgreSQL Database               |
       |  - Workspaces, Docs, Versions, Sections     |
       |  - Extracted Rules, Conflicts, Reviews      |
       +---------------------------------------------+
```

## 2. Component Architecture

### 2.1 Backend Services
1. **Document Ingestion Service (`app/services/document_parser.py`)**:
   - Parses `.pdf` documents via PyMuPDF (`fitz`), preserving heading hierarchy, font weights, paragraph boundaries, and page coordinates.
   - Parses `.docx` documents via `python-docx`, reading headings, lists, tables, and text runs.
   - Normalizes text into `document_sections` with hierarchical parent-child relationships (`level`, `section_number`, `heading`).

2. **NLP & Rule Extraction Service (`app/services/rule_extractor.py`)**:
   - Dissects section text into candidate sentences.
   - Applies spaCy linguistic models, tokenization, dependency parse trees, and custom pattern matchers.
   - Identifies deontic markers (obligation, prohibition, permission, recommendation).
   - Extracts subject, operative verb/action, target object, prepositional qualifiers, conditions, and exception clauses.
   - Produces structured `ExtractedRule` records tied to their source section and byte/character span offsets.

3. **Conflict Detection Engine (`app/services/conflict_detector.py`)**:
   - Compares pairs of rules across different documents (inter-document conflict) or across versions of the same document (inter-version diff).
   - Employs TF-IDF / semantic vector similarity to pair rules with related subjects and actions.
   - Evaluates a Deontic Contradiction Matrix:
     - Mutually exclusive obligations (`MUST` vs `MUST_NOT`, `PERMITTED` vs `PROHIBITED`).
     - Condition divergence (Rule A requires condition X, Rule B forbids action under condition X).
     - Missing exception detection (Rule A has exception E, updated Rule B omits E).
     - Superseded rules (newer effective date / version overriding prior mandate).
     - Ambiguity detection (subjective qualifiers like "promptly", "reasonable", "when practical" without thresholds).
   - Generates a NetworkX directed graph of policy dependencies to spot cyclical rules or cascading contradictions.

4. **Review & Audit Service (`app/services/review_service.py`)**:
   - Manages reviewer approvals, dismissals, and resolutions.
   - Preserves an immutable audit log of compliance decisions.

### 2.2 Data Layer
- **ORM**: SQLAlchemy 2.0 with declarative base and typed mapping (`Mapped`, `mapped_column`).
- **Migrations**: Alembic for versioned schema upgrades.
- **Transactions**: Atomic transaction boundaries per document upload and analysis run.

### 2.3 Frontend Application
- **Vite + React 18 + TypeScript**: Type-safe development.
- **Tailwind CSS**: High-density enterprise dashboard styling.
- **Lucide React**: Icons for modalities, conflict severities, and status flags.
- **Diff Viewer**: Dual-pane comparison displaying source text highlighted alongside structured rule cards.

## 3. Security & Scalability Considerations
- **Isolated Workspaces**: Data isolation by workspace/tenant so policies from different departments or clients remain strictly separated.
- **Stateless Analysis**: Rule extraction and conflict detection algorithms operate deterministically over persisted sections and rules.
- **Memory Footprint**: Streaming parsing for multi-hundred page PDF policies without holding unbounded binary objects in RAM.
