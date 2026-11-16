# PolicyDiff - Implementation Plan

## Completed Roadmap

### Milestone 1: Architectural Foundation & Domain Modeling
- [x] Create project directory layout (`backend`, `frontend`, `docs`).
- [x] Define data models (Users, Workspaces, Documents, Document Versions, Sections, Rules, Conflicts, Reviews).
- [x] Formalize structured rule schema (subject, action, object, conditions, obligations, exceptions, sources).
- [x] Formalize conflict categories and taxonomy.
- [x] Document architecture, database schema, and NLP design.
- [x] Scaffold FastAPI backend with health endpoints and dependency setup.
- [x] Scaffold React + Vite + TypeScript frontend skeleton with Tailwind CSS.
- [x] Write baseline schema validation tests.

### Milestone 2: Document Ingestion & Section Parsing
- [x] Implement file upload API (`POST /api/v1/documents/upload`) supporting PDF and DOCX.
- [x] Implement document versioning and storage service.
- [x] Build PyMuPDF (`fitz`) extractor for structure-aware PDF parsing (headers, paragraphs, lists, page numbers).
- [x] Build `python-docx` extractor for Word documents.
- [x] Persist extracted hierarchy into `extracted_sections` with ordering and nesting.
- [x] Tests: Parsing accuracy, empty files, corrupted archives, format validation, and DB operations.

### Milestone 3: NLP Rule Extraction Pipeline & Conflict Engine
- [x] Setup linguistic deontic matcher identifying modals (`MUST`, `MUST_NOT`, `SHOULD`, `MAY`, `CANNOT`).
- [x] Implement dependency parser isolating Subject, Action, and Target Object.
- [x] Implement condition and exception clause extractors (`if`, `when`, `unless`, `except`).
- [x] Sub-quadratic candidate retrieval using TF-IDF n-grams + cosine similarity.
- [x] Build Deontic Contradiction Logic Matrix:
  - Direct Contradiction
  - Conditional Contradiction
  - Missing Exception
  - Superseded Rule
  - Ambiguous Instruction
  - Harmless Wording Change
- [x] NetworkX policy dependency & contradiction graph generation.
- [x] Synthetic dataset generator producing 516 rules across 10 domains with ground truth isolated from model inputs.
- [x] Evaluator benchmarking precision, recall, and F1 against naive baseline.

### Milestone 4: Complete Frontend & API Integration
- [x] Connect all pages to actual backend APIs without mock data.
- [x] Workspace Dashboard: Metrics, resolution rate, and trigger action.
- [x] Document Library: High-density table with search and category filtering.
- [x] Document Upload: Drag-and-drop file ingestion with metadata and validation.
- [x] Document Version Management: Revisions timeline and section viewer.
- [x] Conflict Investigation: Dual-pane evidence comparison and determination actions.
- [x] Split-Screen Document Evidence Viewer: Comparative side-by-side reading.
- [x] Rule Relationship Graph: NetworkX topology visualizer with node inspector.
- [x] Review Queue: Rapid triage queue for pending conflict decisions.
- [x] Audit Reports: Compliance report exporter and live benchmark runner.

### Milestone 5: Final Engineering & Deployment
- [x] Complete end-to-end integration test (`test_complete_end_to_end_workflow.py`).
- [x] Multi-stage `Dockerfile` (Node.js build stage + Python runtime).
- [x] `docker-compose.yml` with PostgreSQL service and volumes.
- [x] `.env.example` environment variables configuration.
- [x] Complete `README.md` containing problem statement, features, architecture, algorithms, dataset generation, evaluation, installation, limitations, and architecture diagram.
- [x] Verified full test suite passing (22/22 tests).
