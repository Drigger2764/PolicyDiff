export type ObligationType = 'MUST' | 'MUST_NOT' | 'SHOULD' | 'MAY' | 'CANNOT';

export type ConflictCategory =
  | 'Direct contradiction'
  | 'Conditional contradiction'
  | 'Missing exception'
  | 'Superseded rule'
  | 'Ambiguous instruction'
  | 'Harmless wording change';

export type ConflictSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export type ConflictStatus = 'PENDING' | 'RESOLVED' | 'DISMISSED';

export type ReviewDecisionType =
  | 'ACCEPTED_CONFLICT'
  | 'DISMISSED_FALSE_POSITIVE'
  | 'RESOLVED'
  | 'FLAGGED_FOR_LEGAL';

export interface StructuredRule {
  rule_id: string;
  subject: string;
  action: string;
  object: string;
  conditions: string[];
  obligations: ObligationType;
  exceptions: string[];
  source_document: string;
  source_section: string;
}

export interface ExtractedRuleEntity {
  id: string;
  rule_id: string;
  version_id: string;
  section_id: string;
  subject: string;
  obligation: ObligationType;
  action: string;
  target_object: string;
  conditions: string[];
  exceptions: string[];
  raw_text: string;
  char_start?: number;
  char_end?: number;
  confidence_score: number;
  created_at: string;
}

export interface ConflictFinding {
  id: string;
  workspace_id: string;
  rule_a_id: string;
  rule_b_id?: string;
  category: ConflictCategory;
  severity: ConflictSeverity;
  description: string;
  confidence: number;
  status: ConflictStatus;
  created_at: string;
  rule_a?: ExtractedRuleEntity;
  rule_b?: ExtractedRuleEntity;
}

export interface ReviewDecision {
  id: string;
  conflict_id: string;
  reviewer_id?: string;
  decision: ReviewDecisionType;
  notes?: string;
  action_taken?: string;
  created_at: string;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface ExtractedSection {
  id: string;
  version_id: string;
  parent_section_id?: string;
  section_number?: string;
  heading?: string;
  level: number;
  page_start?: number;
  page_end?: number;
  raw_text: string;
  order_index: number;
  created_at: string;
}

export interface DocumentVersion {
  id: string;
  document_id: string;
  version_tag: string;
  file_name: string;
  file_format: string;
  file_path: string;
  file_size_bytes: number;
  status: 'pending' | 'parsed' | 'extracted' | 'failed';
  effective_date?: string;
  uploaded_by?: string;
  created_at: string;
  sections?: ExtractedSection[];
}

export interface Document {
  id: string;
  workspace_id: string;
  title: string;
  category: string;
  description?: string;
  created_at: string;
  updated_at: string;
  versions?: DocumentVersion[];
}
