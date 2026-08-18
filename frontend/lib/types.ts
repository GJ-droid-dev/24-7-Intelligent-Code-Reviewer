export type Severity = "critical" | "high" | "medium" | "low";
export type ReviewStatus = "queued" | "processing" | "complete" | "failed" | "partial";
export type ScoreLabel = "Excellent" | "Good" | "Fair" | "Poor" | "Critical";
export type Recommendation = "safe_to_merge" | "merge_with_non_blocking_changes" | "changes_required" | "manual_review_required";

export interface FindingLocation {
  file?: string;
  startLine?: number;
  endLine?: number;
  symbol?: string;
  snippet?: string;
}

export interface Finding {
  id: string;
  agentSources: string[];
  category: string;
  severity: Severity;
  title: string;
  location?: FindingLocation;
  description?: string;
  evidence?: string;
  impact?: string;
  suggestedFix?: string;
  matchedRuleId?: string | null;
  confidence?: number;
}

export interface ScoreDimension {
  score: number;
  rationale: string;
}

export interface ScoreBreakdown {
  security: ScoreDimension;
  performance: ScoreDimension;
  codeQuality: ScoreDimension;
  testCoverage: ScoreDimension;
  historical: ScoreDimension;
}

export interface AgentStatus {
  agent: string;
  status: "pending" | "running" | "success" | "failed" | "timeout" | "partial" | "skipped";
  attempts?: number;
  durationMs?: number;
  findingCount?: number;
  error?: string;
}

export interface Review {
  reviewId: string;
  userId: string;
  status: ReviewStatus;
  language: string;
  title?: string;
  description?: string;
  codeSnippet?: string;
  overallScore?: number;
  scoreLabel?: ScoreLabel;
  recommendation?: Recommendation;
  scoreBreakdown?: ScoreBreakdown;
  findings?: Finding[];
  blockingIssues?: Finding[];
  nonBlockingIssues?: Finding[];
  agentStatuses?: AgentStatus[];
  specialistCoverage?: Array<{
    agent: string;
    status: string;
    findingCountReceived: number;
    findingCountAccepted: number;
  }>;
  historicalRulesApplied?: Array<{
    id: string;
    type: string;
    description: string;
    findingId?: string;
  }>;
  limitations?: string[];
  humanReviewNote?: string;
  submittedAt: string;
  completedAt?: string;
}

export interface HistoricalRule {
  id: string;
  type: string;
  description: string;
  source?: string;
  createdAt?: string;
}

export interface ReviewSubmission {
  code: string;
  title?: string;
  description?: string;
  language?: string;
}

export interface UserProfile {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL?: string | null;
  isDemo?: boolean;
}
