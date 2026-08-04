import type {
  GradeMCQResponse,
  GradeScenarioResponse,
  Profile,
  QuizStartResponse,
  Topic,
} from './types'

const BASE = 'http://localhost:8000/api'

class ApiError extends Error {}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new ApiError(body.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

export const api = {
  login: (pin: string) =>
    request<{ ok: boolean }>('/auth/login', { method: 'POST', body: JSON.stringify({ pin }) }),

  authStatus: () => request<{ authenticated: boolean }>('/auth/status'),

  listProfiles: () => request<Profile[]>('/profiles'),

  createProfile: (name: string) =>
    request<Profile>('/profiles', { method: 'POST', body: JSON.stringify({ name }) }),

  listTopics: () => request<Topic[]>('/topics'),

  startQuiz: (profile_id: number, topic: string, difficulty: string, count: number) =>
    request<QuizStartResponse>('/quiz/start', {
      method: 'POST',
      body: JSON.stringify({ profile_id, topic, difficulty, count }),
    }),

  gradeMcq: (profile_id: number, question_id: number, selected_index: number) =>
    request<GradeMCQResponse>('/quiz/grade/mcq', {
      method: 'POST',
      body: JSON.stringify({ profile_id, question_id, selected_index }),
    }),

  gradeScenario: (profile_id: number, question_id: number, answer_text: string) =>
    request<GradeScenarioResponse>('/quiz/grade/scenario', {
      method: 'POST',
      body: JSON.stringify({ profile_id, question_id, answer_text }),
    }),
}
