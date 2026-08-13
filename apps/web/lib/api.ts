const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export type Project = {
  id: string;
  name: string;
  address: string | null;
  property_type: string;
  supply_voltage: string | null;
  utility_company: string | null;
  resident_count: number | null;
  is_renovation: boolean;
  status: string;
  created_at: string;
};

export type Room = {
  id: string;
  project_id: string;
  name: string;
  room_type: string;
  area_m2: number | null;
  perimeter_m: number | null;
  source: string;
  confidence_score: number;
};

export type Load = {
  id: string;
  room_id: string;
  circuit_id: string | null;
  category: string;
  name: string;
  nominal_power_w: number;
  voltage_v: number;
  requires_dedicated_circuit: boolean;
  source: string;
  confidence_score: number;
};

export type CatalogEntry = {
  code: string;
  category: string;
  name: string;
  typical_power_w: number;
  voltage_v: number;
  requires_dedicated_circuit: boolean;
  confidence: number;
  source: string;
};

export type RuleResult = {
  rule_code: string;
  status: "VERDE" | "AMARELO" | "VERMELHO" | "AZUL";
  message: string;
  subject_type: string;
  subject_id: string | null;
};

export type ComplianceSummary = {
  counts: Record<string, number>;
  note: string;
};

export const api = {
  createUser: (email: string, name: string) =>
    request<{ id: string }>("/users", { method: "POST", body: JSON.stringify({ email, name }) }),

  listProjects: () => request<Project[]>("/projects"),
  getProject: (id: string) => request<Project>(`/projects/${id}`),
  createProject: (payload: Record<string, unknown>) =>
    request<Project>("/projects", { method: "POST", body: JSON.stringify(payload) }),

  listRooms: (projectId: string) => request<Room[]>(`/projects/${projectId}/rooms`),
  addRoom: (projectId: string, payload: Record<string, unknown>) =>
    request<Room>(`/projects/${projectId}/rooms`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listCatalog: () => request<CatalogEntry[]>("/catalog/loads"),
  listRoomLoads: (roomId: string) => request<Load[]>(`/rooms/${roomId}/loads`),
  addLoadFromCatalog: (roomId: string, catalogCode: string, quantity = 1) =>
    request<Load[]>("/loads/from-catalog", {
      method: "POST",
      body: JSON.stringify({ room_id: roomId, catalog_code: catalogCode, quantity }),
    }),

  generateDesign: (projectId: string) =>
    request<{ panel_id: string; circuit_count: number }>(`/projects/${projectId}/generate`, {
      method: "POST",
    }),

  getRuleResults: (projectId: string) =>
    request<RuleResult[]>(`/projects/${projectId}/rule-results`),
  getComplianceSummary: (projectId: string) =>
    request<ComplianceSummary>(`/projects/${projectId}/compliance-summary`),
  getCalculations: (projectId: string) => request<any[]>(`/projects/${projectId}/calculations`),

  chat: (projectId: string, message: string) =>
    request<{ reply: string; rule_codes_cited: string[]; calculation_types_cited: string[] }>(
      `/projects/${projectId}/chat`,
      { method: "POST", body: JSON.stringify({ message }) }
    ),

  interviewNext: (projectId: string, lastUserAnswer?: string) =>
    request<{ question: string; blocked: boolean }>(
      `/projects/${projectId}/interview/next${
        lastUserAnswer ? `?last_user_answer=${encodeURIComponent(lastUserAnswer)}` : ""
      }`,
      { method: "POST" }
    ),

  checkSocketPlacement: (
    projectId: string,
    payload: { room_type: string; distance_from_water_source_m?: number }
  ) =>
    request<RuleResult>(`/projects/${projectId}/socket-placement-check`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  documentUrl: (projectId: string) => `${API_URL}/projects/${projectId}/document.pdf`,
};
