export interface Country {
  code: string;
  name: string;
  phase: number;
  active: boolean;
}

export interface Sector {
  id: number;
  name: string;
  priority: number;
  active: boolean;
}

export interface TriggerDef {
  id: number;
  code: string;
  name: string;
  description: string;
  keywords: string[];
  potential_services: string[];
  base_need_score: number;
  active: boolean;
}

export interface Source {
  id: number;
  name: string;
  url: string;
  country_code: string | null;
  category: string;
  reliability_score: number;
  active: boolean;
  created_at: string;
}

export interface Opportunity {
  id: number;
  company_id: number | null;
  trigger_id: number | null;
  description: string;
  country_code: string | null;
  sector_id: number | null;
  amount: number | null;
  currency: string | null;
  source_url: string;
  related_sources: string[];
  detected_at: string;
  opportunity_score: number;
  score_breakdown: Record<string, unknown>;
  urgency: "low" | "medium" | "high";
  suggested_service: string[];
  confidence: number;
  status: string;
  company_name?: string | null;
  country_name?: string | null;
  sector_name?: string | null;
  trigger_name?: string | null;
}

export interface Company {
  id: number;
  name: string;
  country_code: string | null;
  sector_id: number | null;
  website: string | null;
  description: string;
  size: string | null;
  revenue: string | null;
  employees: string | null;
  executives: unknown[];
  created_at: string;
  updated_at: string;
}

export interface CompanyDetail extends Company {
  contacts: Contact[];
  opportunity_count: number;
  commercial_score: number;
}

export interface Contact {
  id: number;
  company_id: number;
  name: string;
  position: string;
  source: string;
  public_profile: string | null;
  verification_date: string | null;
}

export interface Tender {
  id: number;
  institution: string;
  country_code: string | null;
  sector_id: number | null;
  title: string;
  description: string;
  budget: string | null;
  deadline: string | null;
  source_url: string;
  fit_score: number;
  status: string;
  detected_at: string;
}

export interface Investor {
  id: number;
  name: string;
  type: string;
  countries: string[];
  sectors: string[];
  ticket_size: string | null;
  recent_activity: string;
}

export interface Partner {
  id: number;
  name: string;
  category: string;
  countries: string[];
  sectors: string[];
  description: string;
  contact_info: string;
}

export interface CrmDeal {
  id: number;
  opportunity_id: number;
  stage: string;
  estimated_value: number | null;
  probability: number;
  expected_close: string | null;
  owner: string;
  next_action: string;
  lost_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface Alert {
  id: number;
  opportunity_id: number;
  type: string;
  channel: string;
  recipient: string;
  message: string;
  sent_at: string;
  status: string;
}

export interface KpiData {
  nouvelles_opportunites: number;
  opportunites_prioritaires: number;
  opportunites_cette_semaine: number;
  appels_offres_actifs: number;
  entreprises_surveillees: number;
  investisseurs_actifs: number;
  partenariats_potentiels: number;
  valeur_commerciale_potentielle: number;
}

export interface ScoringWeight {
  criterion: string;
  weight_percent: number;
  label: string;
}
