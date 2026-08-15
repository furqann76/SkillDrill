import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import './App.css'
import { api } from './api'
import { AuthPage } from './components/AuthPage'
import { Dashboard } from './components/Dashboard'
import { QuizRunner, type QuestionResult } from './components/QuizRunner'
import { QuizSetup } from './components/QuizSetup'
import { Summary } from './components/Summary'
import type { Profile, QuestionOut } from './types'

type Screen = 'checking' | 'auth' | 'setup' | 'quiz' | 'summary' | 'dashboard'

function App() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const initialTopic = searchParams.get('topic') || undefined

  const [screen, setScreen] = useState<Screen>('checking')
  const [profile, setProfile] = useState<Profile | null>(null)
  const [questions, setQuestions] = useState<QuestionOut[]>([])
  const [results, setResults] = useState<QuestionResult[]>([])

  useEffect(() => {
    api
      .authStatus()
      .then((s) => {
        if (s.authenticated && s.profile) {
          setProfile(s.profile)
          setScreen('setup')
        } else {
          setScreen('auth')
        }
      })
      .catch(() => setScreen('auth'))
  }, [])

  function handleAuthenticated(p: Profile) {
    setProfile(p)
    setScreen('setup')
  }

  async function handleLogout() {
    await api.logout().catch(() => {})
    setProfile(null)
    setScreen('auth')
  }

  // Wordmark click, from any of the themed screens -- goes to the public
  // landing page, not back into the authenticated app. The session is left
  // alone (no logout): if they navigate back into /app they land straight
  // in quiz setup again.
  function goHome() {
    navigate('/')
  }

  return (
    <>
      {screen === 'checking' && <div className="screen" />}

      {screen === 'auth' && (
        <AuthPage initialTopic={initialTopic} onSuccess={handleAuthenticated} />
      )}

      {screen === 'setup' && profile && (
        <QuizSetup
          profile={profile}
          initialTopic={initialTopic}
          onStart={(qs) => {
            setQuestions(qs)
            setScreen('quiz')
          }}
          onViewDashboard={() => setScreen('dashboard')}
          onGoHome={goHome}
          onLogout={handleLogout}
        />
      )}

      {screen === 'quiz' && (
        <QuizRunner
          questions={questions}
          onFinish={(r) => {
            setResults(r)
            setScreen('summary')
          }}
          onGoHome={goHome}
        />
      )}

      {screen === 'summary' && (
        <Summary results={results} onRestart={() => setScreen('setup')} onGoHome={goHome} />
      )}

      {screen === 'dashboard' && profile && (
        <Dashboard
          profile={profile}
          onBack={() => setScreen('setup')}
          onGoHome={goHome}
          onLogout={handleLogout}
        />
      )}
    </>
  )
}

export default App
