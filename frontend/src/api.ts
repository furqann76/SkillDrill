import type {
  AnalyticsResponse,
  AuthResponse,
  AuthStatusResponse,
  GradeMCQResponse,
  GradeScenarioResponse,
  LeaderboardEntry,
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
  signup: (
    username: string,
    email: string,
    password: string,
    confirm_password: string,
    preferred_topic?: string,
  ) =>
    request<AuthResponse>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ username, email, password, confirm_password, preferred_topic }),
    }),

  login: (identifier: string, password: string, remember: boolean) =>
    request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ identifier, password, remember }),
    }),

  logout: () => request<{ ok: boolean }>('/auth/logout', { method: 'POST' }),

  authStatus: () => request<AuthStatusResponse>('/auth/status'),

  listTopics: (includeInactive = false) =>
    request<Topic[]>(`/topics${includeInactive ? '?include_inactive=true' : ''}`),

  createTopic: (name: string, display_name?: string) =>
    request<Topic>('/topics', { method: 'POST', body: JSON.stringify({ name, display_name }) }),

  setTopicActive: (topicId: number, is_active: boolean) =>
    request<Topic>(`/topics/${topicId}`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active }),
    }),

  startQuiz: (topic: string, difficulty: string, count: number) =>
    request<QuizStartResponse>('/quiz/start', {
      method: 'POST',
      body: JSON.stringify({ topic, difficulty, count }),
    }),

  gradeMcq: (question_id: number, selected_index: number) =>
    request<GradeMCQResponse>('/quiz/grade/mcq', {
      method: 'POST',
      body: JSON.stringify({ question_id, selected_index }),
    }),

  gradeScenario: (question_id: number, answer_text: string) =>
    request<GradeScenarioResponse>('/quiz/grade/scenario', {
      method: 'POST',
      body: JSON.stringify({ question_id, answer_text }),
    }),

  getAnalytics: () => request<AnalyticsResponse>('/analytics'),

  publicTopics: () => request<PublicTopic[]>('/public/topics'),

  publicLeaderboard: (limit?: number) =>
    request<LeaderboardEntry[]>(`/public/leaderboard${limit ? `?limit=${limit}` : ''}`),
}
