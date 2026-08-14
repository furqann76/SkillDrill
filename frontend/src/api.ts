import type {
  AnalyticsResponse,
  GradeMCQResponse,
  GradeScenarioResponse,
  LeaderboardEntry,
  Profile,
  PublicTopic,
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

  listTopics: (includeInactive = false) =>
    request<Topic[]>(`/topics${includeInactive ? '?include_inactive=true' : ''}`),

  createTopic: (name: string, display_name?: string) =>
    request<Topic>('/topics', { method: 'POST', body: JSON.stringify({ name, display_name }) }),

  setTopicActive: (topicId: number, is_active: boolean) =>
    request<Topic>(`/topics/${topicId}`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active }),
    }),

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

  getAnalytics: (profile_id: number) =>
    request<AnalyticsResponse>(`/analytics/${profile_id}`),

  publicTopics: () => request<PublicTopic[]>('/public/topics'),

  publicLeaderboard: (limit?: number) =>
    request<LeaderboardEntry[]>(`/public/leaderboard${limit ? `?limit=${limit}` : ''}`),
}
