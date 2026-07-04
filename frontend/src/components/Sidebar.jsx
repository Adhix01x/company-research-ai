import { useState } from 'react'
import { Plus, TerminalSquare, Key, MessageSquare, HelpCircle, Save } from 'lucide-react'

const MODEL_OPTIONS = [
  { name: 'Gemini 2.0 Flash (Recommended)', id: 'google/gemini-2.0-flash' },
  { name: 'Claude 3.5 Sonnet', id: 'anthropic/claude-3.5-sonnet' },
  { name: 'GPT-4o', id: 'openai/gpt-4o' },
  { name: 'Meta Llama 3.1 70B', id: 'meta-llama/llama-3.1-70b-instruct' },
]

const Sidebar = ({
  onNewChat,
  history,
  isOpen,
  onHistoryClick,
  apiKeys,
  onSaveApiKeys,
  discordConfig,
  onSaveDiscordConfig,
}) => {
  const [activeTab, setActiveTab] = useState('api') // 'api', 'discord', 'history'

  // Local form states
  const [openRouterKey, setOpenRouterKey] = useState(apiKeys.openRouterKey)
  const [serperKey, setSerperKey] = useState(apiKeys.serperKey)
  const [selectedModel, setSelectedModel] = useState(apiKeys.model || 'google/gemini-2.0-flash')

  const [botToken, setBotToken] = useState(discordConfig.botToken)
  const [channelId, setChannelId] = useState(discordConfig.channelId)
  const [applicantName, setApplicantName] = useState(discordConfig.name)
  const [applicantEmail, setApplicantEmail] = useState(discordConfig.email)

  const handleSaveApi = (e) => {
    e.preventDefault()
    onSaveApiKeys({
      openRouterKey,
      serperKey,
      model: selectedModel,
    })
  }

  const handleSaveDiscord = (e) => {
    e.preventDefault()
    onSaveDiscordConfig({
      botToken,
      channelId,
      name: applicantName,
      email: applicantEmail,
    })
  }

  const getRelativeTime = (timestamp) => {
    const diff = Date.now() - timestamp
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return 'Just now'
    if (mins < 60) return `${mins}m ago`
    const hours = Math.floor(mins / 60)
    if (hours < 24) return `${hours}h ago`
    return new Date(timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  }

  return (
    <div className={`sidebar glass-panel ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">
          <TerminalSquare size={20} color="#f1f5f9" />
        </div>
        <div>
          <h1>AI Analyst</h1>
          <div className="sidebar-brand-sub">Company Intelligence</div>
        </div>
      </div>

      <button className="new-chat-btn" onClick={onNewChat} id="new-research-btn">
        <Plus size={16} />
        New Research
      </button>

      {/* Tabs */}
      <div className="sidebar-tabs">
        <button
          className={`sidebar-tab-btn ${activeTab === 'api' ? 'active' : ''}`}
          onClick={() => setActiveTab('api')}
          id="tab-api-btn"
        >
          API
        </button>
        <button
          className={`sidebar-tab-btn ${activeTab === 'discord' ? 'active' : ''}`}
          onClick={() => setActiveTab('discord')}
          id="tab-discord-btn"
        >
          Discord
        </button>
        <button
          className={`sidebar-tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
          id="tab-history-btn"
        >
          History ({history.length})
        </button>
      </div>

      <div className="sidebar-content">
        {/* API PANEL */}
        {activeTab === 'api' && (
          <form onSubmit={handleSaveApi} className="sidebar-form" id="api-config-form">
            <div className="form-group">
              <label htmlFor="openrouter-key">OpenRouter API Key</label>
              <input
                id="openrouter-key"
                type="password"
                placeholder="sk-or-v1-..."
                value={openRouterKey}
                onChange={(e) => setOpenRouterKey(e.target.value)}
                className="sidebar-input"
              />
            </div>
            <div className="form-group">
              <label htmlFor="serper-key">Serper.dev API Key</label>
              <input
                id="serper-key"
                type="password"
                placeholder="Your Serper key..."
                value={serperKey}
                onChange={(e) => setSerperKey(e.target.value)}
                className="sidebar-input"
              />
            </div>
            <div className="form-group">
              <label htmlFor="model-select">AI Model</label>
              <select
                id="model-select"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="sidebar-select"
              >
                {MODEL_OPTIONS.map((opt) => (
                  <option key={opt.id} value={opt.id}>
                    {opt.name}
                  </option>
                ))}
              </select>
            </div>
            <button type="submit" className="sidebar-save-btn gold" id="save-api-btn">
              <Save size={14} />
              Save Config
            </button>
          </form>
        )}

        {/* DISCORD PANEL */}
        {activeTab === 'discord' && (
          <form onSubmit={handleSaveDiscord} className="sidebar-form" id="discord-config-form">
            <div className="discord-callout">
              <h4>Discord Bot Notification</h4>
              <p>After research is done, reports are automatically sent to your channel.</p>
            </div>
            <div className="form-group">
              <label htmlFor="bot-token">Bot Token</label>
              <input
                id="bot-token"
                type="password"
                placeholder="Token..."
                value={botToken}
                onChange={(e) => setBotToken(e.target.value)}
                className="sidebar-input"
              />
            </div>
            <div className="form-group">
              <label htmlFor="channel-id">Channel ID</label>
              <input
                id="channel-id"
                type="text"
                placeholder="Channel ID..."
                value={channelId}
                onChange={(e) => setChannelId(e.target.value)}
                className="sidebar-input"
              />
            </div>
            <div className="sidebar-section-divider">Applicant Details</div>
            <div className="form-group">
              <label htmlFor="applicant-name">Full Name</label>
              <input
                id="applicant-name"
                type="text"
                placeholder="Your name..."
                value={applicantName}
                onChange={(e) => setApplicantName(e.target.value)}
                className="sidebar-input"
              />
            </div>
            <div className="form-group">
              <label htmlFor="applicant-email">Email Address</label>
              <input
                id="applicant-email"
                type="email"
                placeholder="email@example.com"
                value={applicantEmail}
                onChange={(e) => setApplicantEmail(e.target.value)}
                className="sidebar-input"
              />
            </div>
            <button type="submit" className="sidebar-save-btn purple" id="save-discord-btn">
              <Save size={14} />
              Save Discord Config
            </button>
          </form>
        )}

        {/* HISTORY PANEL */}
        {activeTab === 'history' && (
          <div className="history-list" id="history-list">
            {history.length === 0 ? (
              <div className="history-empty">
                <MessageSquare size={20} />
                <p>No past research. Start a new session above!</p>
              </div>
            ) : (
              history.map((item) => (
                <div
                  key={item.id}
                  className="history-item"
                  onClick={() => onHistoryClick(item)}
                  id={`history-item-${item.id}`}
                >
                  <MessageSquare size={14} className="history-item-icon" />
                  <div className="history-item-content">
                    <div className="history-item-title">{item.title}</div>
                    <div className="history-item-time">{getRelativeTime(item.timestamp)}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Help Panel */}
        <div className="how-it-works">
          <div className="how-it-works-title">
            <HelpCircle size={12} />
            How It Works
          </div>
          <div className="how-step">
            <div className="how-step-num">1</div>
            <div className="how-step-label">Enter a company name or official URL</div>
          </div>
          <div className="how-step">
            <div className="how-step-num">2</div>
            <div className="how-step-label">Serper.dev resolves site and crawls pages</div>
          </div>
          <div className="how-step">
            <div className="how-step-num">3</div>
            <div className="how-step-label">OpenRouter models analyze data for insights</div>
          </div>
          <div className="how-step">
            <div className="how-step-num">4</div>
            <div className="how-step-label">Download customized professional report PDFs</div>
          </div>
        </div>
      </div>

      <div className="sidebar-footer">
        <span className="sidebar-footer-text">OpenRouter · Serper · FPDF2</span>
        <span className="sidebar-footer-version">v2.0</span>
      </div>
    </div>
  )
}

export default Sidebar
