export interface Profile {
  id: number
  name: string
}

export interface Topic {
  id: number
  name: string
  display_name: string
}

export interface QuestionOut {
  id: number
  type: 'mcq' | 'scenario'
  difficulty: string
  question_text: string
  options?: string[] | null
}

export interface QuizStartResponse {
  questions: QuestionOut[]
  requested: number
  available: number
}

export interface GradeMCQResponse {
  is_correct: boolean
  correct_index: number
  explanation: string
}

export interface RubricPoint {
  point: string
  covered: boolean
}

export interface GradeScenarioResponse {
  score: number
  is_correct: boolean
  rubric_breakdown: RubricPoint[]
  feedback: string
  model_answer: string
}
