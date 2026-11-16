# PolicyDiff - Project Context

## Overview
PolicyDiff is an enterprise document intelligence and governance platform that ingests unstructured company policy documents (PDF, DOCX), decomposes clauses into atomic deontic compliance rules, and identifies contradictions, missing exceptions, superseded rules, and ambiguous instructions across policies and revisions.

## Completed Milestones

### Milestone 1: Architectural Foundation & Domain Modeling
- Decoupled repository layout (`backend/`, `frontend/`, `docs/`).
- SQLAlchemy 2.0 ORM models and Alembic migration structure across all 8 core entities:
  `User`, `Workspace`, `Document`, `DocumentVersion`, `ExtractedSection`, `ExtractedRule`, `ConflictFinding`, and `ReviewDecision`.
- Formalized 9-tuple structured rule schema (`rule_id`, `subject`, `action`, `object`, `conditions`, `obligations`, `exceptions`, `source_document`, `source_section`).
- Conflict categories taxonomy and severity classification.
- Baseline FastAPI health endpoints and Pydantic schemas.

### Milestone 2: Backend & Document Ingestion
- Multi-format document upload endpoint (`POST /api/v1/documents/upload`).
- Structure-aware PyMuPDF (`fitz`) PDF extraction preserving headings, section numbers, and page numbers.
- `python-docx` parser preserving styles, bullet lists, and tables.
- File type and 50MB size validation, empty file checks, and corrupted archive handling.
- Cascading document deletion and version inspection endpoints.

### Milestone 3: Rule Extraction & Contradiction Detection Engine
- Linguistic deontic parser identifying normative modals (`MUST`, `MUST_NOT`, `SHOULD`, `MAY`, `CANNOT`), subjects, verbs, objects, conditions, and exceptions.
- Rule normalization and token canonicalization.
- Sub-quadratic candidate retrieval via TF-IDF n-grams preventing $O(N^2)$ exhaustive comparisons.
- Deontic Contradiction Logic Matrix classifying all 6 conflict categories:
  `Direct contradiction`, `Conditional contradiction`, `Missing exception`, `Superseded rule`, `Ambiguous instruction`, `Harmless wording change`.
- NetworkX graph generation modeling policy dependency topologies, clusters, and circular contradictions.
- Reproducible synthetic dataset generator producing 516 rules across 10 enterprise domains with planted ground truth held strictly separate from model inputs.
- Evaluator measuring precision, recall, and F1 comparing PolicyDiff against a naive baseline.

### Milestone 4: Complete Frontend & API Integration
- Built with React 18, TypeScript, and Tailwind CSS using a neutral, commercial enterprise aesthetic (no purple gradients or decorative animations).
- 9 fully connected views:
  1. **Workspace Dashboard**: KPI cards, resolution rates, quick contradiction trigger.
  2. **Document Library**: Information-dense table with category filtering and search.
  3. **Document Upload**: Drag-and-drop file ingestion with metadata and validation.
  4. **Document Version Management**: Revision history and section hierarchy viewer.
  5. **Conflict Investigation**: Deep dive workbench with side-by-side evidence inspection.
  6. **Split-Screen Evidence Viewer**: Dual-pane comparative text diff.
  7. **Rule Relationship Graph**: NetworkX graph topology with interactive node inspector.
  8. **Review Queue**: Rapid auditor triage workflow (Accept, Dismiss, Escalate to Legal).
  9. **Audit Reports**: Compliance statistics export and live benchmark runner.

### Milestone 5: Final Engineering & Deployment
- Comprehensive test suite with 22 unit, integration, and end-to-end tests passing in ~5 seconds.
- Multi-stage `Dockerfile` and `docker-compose.yml` with PostgreSQL 15 and volume mounts.
- Environment template `.env.example`.
- Complete `README.md` with problem statement, architecture diagram, algorithms, measured results, and limitations.
