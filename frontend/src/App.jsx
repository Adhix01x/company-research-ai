import { useState, useCallback, createContext, useContext, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import Toast from './components/Toast'
import { Menu, X } from 'lucide-react'
import './App.css'

/* ---- Config ---- */
const API_BASE_URL = window.location.port === '5173' ? 'http://127.0.0.1:8000' : ''
const API_RESEARCH_ENDPOINT = `${API_BASE_URL}/api/research`

/* ---- Toast Context ---- */
const ToastContext = createContext(null)
export const useToast = () => useContext(ToastContext)

/* ---- Error Boundary ---- */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message || 'An unexpected error occurred.'}</p>
          <button id="error-boundary-reload" onClick={() => window.location.reload()}>
            Reload App
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

import React from 'react'

function App() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [history, setHistory] = useState(() => {
    try {
      const saved = localStorage.getItem('ai_analyst_history')
      return saved ? JSON.parse(saved) : []
    } catch {
      return []
    }
  })
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [toasts, setToasts] = useState([])

  /* ---- Config State ---- */
  const [apiKeys, setApiKeys] = useState(() => {
    try {
      const saved = localStorage.getItem('ai_analyst_apikeys')
      return saved ? JSON.parse(saved) : { openRouterKey: '', serperKey: '', model: 'google/gemini-2.0-flash' }
    } catch {
      return { openRouterKey: '', serperKey: '', model: 'google/gemini-2.0-flash' }
    }
  })

  const [discordConfig, setDiscordConfig] = useState(() => {
    try {
      const saved = localStorage.getItem('ai_analyst_discord')
      return saved ? JSON.parse(saved) : { botToken: '', channelId: '', name: '', email: '' }
    } catch {
      return { botToken: '', channelId: '', name: '', email: '' }
    }
  })

  // Save history to localStorage
  useEffect(() => {
    localStorage.setItem('ai_analyst_history', JSON.stringify(history))
  }, [history])

  /* ---- Toast methods ---- */
  const addToast = useCallback((type, title, message, duration = 4000) => {
    const id = Date.now() + Math.random()
    setToasts(prev => [...prev, { id, type, title, message, duration }])
    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const toast = {
    success: (title, message) => addToast('success', title, message),
    error: (title, message) => addToast('error', title, message, 6000),
    warning: (title, message) => addToast('warning', title, message),
    info: (title, message) => addToast('info', title, message),
  }

  /* ---- Save API Config ---- */
  const handleSaveApiKeys = (keys) => {
    setApiKeys(keys)
    localStorage.setItem('ai_analyst_apikeys', JSON.stringify(keys))
    toast.success('Configuration Saved', 'API keys and model preferences updated.')
  }

  /* ---- Save Discord Config ---- */
  const handleSaveDiscordConfig = (config) => {
    setDiscordConfig(config)
    localStorage.setItem('ai_analyst_discord', JSON.stringify(config))
    toast.success('Discord Config Saved', 'Discord integration settings updated.')
  }

  /* ---- New Chat ---- */
  const handleNewChat = () => {
    setMessages([])
    setSidebarOpen(false)
    toast.info('New Research', 'Ready to research a new company.')
  }

  /* ---- Clear Chat ---- */
  const handleClearChat = () => {
    setMessages([])
    toast.info('Chat Cleared', 'Conversation history cleared.')
  }

  /* ---- Send Message ---- */
  const handleSendMessage = async (companyInput) => {
    if (!companyInput.trim()) {
      toast.warning('Empty Input', 'Please enter a company name or website URL.')
      return
    }

    // Check if API keys are configured
    if (!apiKeys.openRouterKey.trim() || !apiKeys.serperKey.trim()) {
      toast.error('API Keys Required', 'Please configure your OpenRouter and Serper.dev API keys in the sidebar first.')
      setSidebarOpen(true)
      return
    }

    const userMessage = { role: 'user', content: `Research: ${companyInput}`, timestamp: Date.now() }
    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    setIsLoading(true)

    try {
      const response = await fetch(API_RESEARCH_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_input: companyInput,
          model: apiKeys.model || 'google/gemini-2.0-flash',
          applicant_name: discordConfig.name || '',
          applicant_email: discordConfig.email || '',
          serper_api_key: apiKeys.serperKey || '',
          openrouter_api_key: apiKeys.openRouterKey || '',
          discord_bot_token: discordConfig.botToken || '',
          discord_channel_id: discordConfig.channelId || ''
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Server error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()

      if (data.status === 'success') {
        const aiMessage = {
          role: 'ai',
          report: data.report, // This is structured JSON report
          pdfUrl: data.pdf_url,
          targetUrl: data.target_url,
          timestamp: Date.now()
        }
        setMessages([...newMessages, aiMessage])
        
        // Add to history
        setHistory(prev => {
          const exists = prev.some(item => item.title.toLowerCase() === companyInput.toLowerCase())
          if (exists) return prev
          return [{ id: Date.now(), title: companyInput, report: data.report, pdfUrl: data.pdf_url, targetUrl: data.target_url, timestamp: Date.now() }, ...prev]
        })
        toast.success('Research Complete', `Analysis for "${data.report.company_name || companyInput}" is ready.`)
      } else {
        setMessages([...newMessages, {
          role: 'ai',
          content: `**Research Failed**\n\n${data.message || 'Unknown error occurred.'}`,
          isError: true,
          timestamp: Date.now()
        }])
        toast.error('Research Failed', data.message || 'Something went wrong.')
      }
    } catch (error) {
      const errorMsg = error.message.includes('Failed to fetch')
        ? 'Cannot connect to backend server. Make sure the FastAPI backend is running.'
        : error.message
      
      setMessages([...newMessages, {
        role: 'ai',
        content: `**Connection Error**\n\n${errorMsg}\n\nPlease check your backend server status and try again.`,
        isError: true,
        timestamp: Date.now()
      }])
      toast.error('Connection Error', errorMsg)
    } finally {
      setIsLoading(false)
    }
  }

  /* ---- Load history item ---- */
  const handleHistoryClick = (item) => {
    setSidebarOpen(false)
    const aiMessage = {
      role: 'ai',
      report: item.report,
      pdfUrl: item.pdfUrl,
      targetUrl: item.targetUrl,
      timestamp: item.timestamp
    }
    setMessages([
      { role: 'user', content: `Research: ${item.title}`, timestamp: item.timestamp },
      aiMessage
    ])
    toast.info('Loaded Session', `Showing research for "${item.title}".`)
  }

  return (
    <ErrorBoundary>
      <ToastContext.Provider value={toast}>
        <div className="app-layout">
          {/* Mobile overlay */}
          {sidebarOpen && (
            <div
              className="sidebar-overlay visible"
              onClick={() => setSidebarOpen(false)}
              id="sidebar-overlay"
            />
          )}

          {/* Mobile menu button */}
          <button
            className="mobile-menu-btn"
            id="mobile-menu-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label={sidebarOpen ? 'Close menu' : 'Open menu'}
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

          <Sidebar
            onNewChat={handleNewChat}
            history={history}
            isOpen={sidebarOpen}
            onHistoryClick={handleHistoryClick}
            apiKeys={apiKeys}
            onSaveApiKeys={handleSaveApiKeys}
            discordConfig={discordConfig}
            onSaveDiscordConfig={handleSaveDiscordConfig}
          />

          <ChatArea
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            onClearChat={handleClearChat}
            selectedModel={apiKeys.model}
            onModelChange={(model) => handleSaveApiKeys({ ...apiKeys, model })}
          />

          {/* Toast container */}
          <div className="toast-container" id="toast-container">
            {toasts.map(t => (
              <Toast
                key={t.id}
                id={t.id}
                type={t.type}
                title={t.title}
                message={t.message}
                duration={t.duration}
                onClose={removeToast}
              />
            ))}
          </div>
        </div>
      </ToastContext.Provider>
    </ErrorBoundary>
  )
}

export default App
