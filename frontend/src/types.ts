export interface CitizenProfile {
  age?: number | null;
  annual_income?: number | null;
  income_type?: "individual" | "household" | null;
  state?: string | null;
  district?: string | null;
  occupation?: string | null;
  gender?: string | null;
  social_category?: string | null;
  education?: string | null;
  disability?: boolean | null;
  marital_status?: string | null;
  query_text?: string | null;
}

export interface CriterionResult {
  criterion: string;
  status: "pass" | "fail" | "unknown" | "not_applicable";
  reason: string;
  source_text?: string | null;
}

export interface SchemeRecommendation {
  scheme_id: string;
  scheme_name: string;
  short_title: string;
  level: string;
  state?: string | null;
  categories: string[];
  benefit_type: string;
  eligibility_status:
    | "eligible_based_on_available_rules"
    | "potentially_eligible"
    | "not_eligible_based_on_known_rules"
    | "insufficient_information";
  match_score: number;
  semantic_score: number;
  criteria_results: CriterionResult[];
  matched_reasons: string[];
  unmet_conditions: string[];
  unknown_conditions: string[];
  brief_description: string;
  benefits: string[];
  documents_required: string[];
  application_steps: string[];
  official_application_url?: string | null;
}

export interface SimplifiedSchemeOutput {
  language: string;
  scheme_id: string;
  localized_scheme_name: string;
  simple_explanation: string;
  benefits: string[];
  eligibility_summary: string;
  application_steps: string[];
  required_documents: string[];
  official_application_url?: string | null;
  important_cautions: string[];
  is_fallback: boolean;
}

export interface MultiAgentWorkflowResponse {
  session_id: string;
  language: string;
  profile: CitizenProfile;
  profile_complete: boolean;
  clarification_question?: string | null;
  suggested_options?: string[] | null;
  acknowledgement_text?: string | null;
  recommendations: SimplifiedSchemeOutput[];
  raw_recommendations: SchemeRecommendation[];
  meta: {
    latencies?: Record<string, number>;
    matched_count?: number;
    unmatched_reasons?: string[];
    extracted_fields?: Record<string, any>;
  };
}

export interface SupportedLanguage {
  code: string;
  name: string;
  native: string;
}

export interface SchemeDetail {
  id: string;
  name: string;
  short_title: string;
  level: string;
  state?: string | null;
  ministry?: string | null;
  department?: string | null;
  benefit_type: string;
  categories: string[];
  sub_categories: string[];
  tags: string[];
  brief_description: string;
  detailed_description: string;
  benefits: string[];
  eligibility_text: string;
  exclusions?: string | null;
  application_mode: string;
  application_steps: string[];
  documents_required: string[];
  references: string[];
  source_url: string;
}
