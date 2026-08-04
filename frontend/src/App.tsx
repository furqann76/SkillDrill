import { useEffect, useState } from 'react'
import './App.css'
import { api } from './api'
import { AdminTopics } from './components/AdminTopics'
import { Dashboard } from './components/Dashboard'
import { Login } from './components/Login'
import { ProfileSelect } from './components/ProfileSelect'
import { QuizRunner, type QuestionResult } from './components/QuizRunner'
import { QuizSetup } from './components/QuizSetup'
import { Summary } from './components/Summary'
import type { Profile, QuestionOut } from './types'

type Screen = 'checking' | 'login' | 'profile' | 'setup' | 'quiz' | 'summary' | 'dashboard' | 'admin'

function App() {
  const [screen, setScreen] = useState<Screen>('checking')
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [profile, setProfile] = useState<Profile | null>(null)
  const [questions, setQuestions] = useState<QuestionOut[]>([])
  const [results, setResults] = useState<QuestionResult[]>([])

  useEffect(() => {
    api
      .authStatus()
      .then((s) => (s.authenticated ? enterApp() : setScreen('login')))
      .catch(() => setScreen('login'))
  }, [])

  async function enterApp() {
    const p = await api.listProfiles()
    setProfiles(p)
    setScreen('profile')
  }

  return (
    <>
      {screen === 'checking' && <div className="screen" />}

      {screen === 'login' && <Login onSuccess={enterApp} />}

      {screen === 'profile' && (
        <ProfileSelect
          profiles={profiles}
          onProfilesChange={setProfiles}
          onSelect={(p) => {
            setProfile(p)
            setScreen('setup')
          }}
        />
      )}

      {screen === 'setup' && profile && (
        <QuizSetup
          profile={profile}
          onStart={(qs) => {
            setQuestions(qs)
            setScreen('quiz')
          }}
          onViewDashboard={() => setScreen('dashboard')}
          onManageTopics={() => setScreen('admin')}
        />
      )}

      {screen === 'quiz' && profile && (
        <QuizRunner
          profile={profile}
          questions={questions}
          onFinish={(r) => {
            setResults(r)
            setScreen('summary')
          }}
        />
      )}

      {screen === 'summary' && <Summary results={results} onRestart={() => setScreen('setup')} />}

      {screen === 'dashboard' && profile && (
        <Dashboard profile={profile} onBack={() => setScreen('setup')} />
      )}

      {screen === 'admin' && <AdminTopics onBack={() => setScreen('setup')} />}
    </>
  )
}

export default App
