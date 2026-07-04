import { useState, useRef, useEffect } from 'react'
import { Send, Trash2, Cpu, Check, HelpCircle } from 'lucide-react'
import Message from './Message'

const EXAMPLE_COMPANIES = ['notion.so', 'Figma', 'Linear', 'Vercel']

const RESEARCH_STEPS = [
  'Searching Serper.dev for official website',
  'Crawling key pages — home, about, products, pricing',
  'Cross-referencing competitor databases',
  'Sending extracted content to OpenRouter',
  'Generating AI insights & identifying competitors',
]

const ChatArea = ({
  messages,
  isLoading,
  onSendMessage,
  onClearChat,
  selectedModel,
  onModelChange,
}) => {
  const [companyInput, setCompanyInput] = useState('')
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  // Auto-scroll when messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Reset step index when loading state changes
  useEffect(() => {
    if (isLoading) {
      setCurrentStepIndex(0)
      const interval = setInterval(() => {
        setCurrentStepIndex((prev) => {
          if (prev < RESEARCH_STEPS.length - 1) {
            return prev + 1
          }
          clearInterval(interval)
          return prev
        })
      }, 2500) // Cycle steps every 2.5 seconds

      return () => clearInterval(interval)
    }
  }, [isLoading])

  const handleSubmit = (e) => {
    if (e) e.preventDefault()
    if (!companyInput.trim() || isLoading) return
    onSendMessage(companyInput)
    setCompanyInput('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleTextareaInput = (e) => {
    const target = e.target
    target.style.height = 'auto'
    target.style.height = `${Math.min(target.scrollHeight, 120)}px`
  }

  const handleChipClick = (company) => {
    if (isLoading) return
    onSendMessage(company)
  }

  return (
    <div className="chat-area">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-left">
          <div className="chat-title-mobile-spacer" />
          <h2 className="chat-header-title">Company Research</h2>
          <div className="live-badge">
            <div className="live-dot" />
            <span className="live-text">LIVE</span>
          </div>
        </div>

        <div className="chat-header-actions">
          {/* Model Selector Dropdown */}
          <div className="model-selector">
            <select
              value={selectedModel}
              onChange={(e) => onModelChange(e.target.value)}
              className="model-selector-select"
              title="Change OpenRouter Model"
              id="model-selector-dropdown"
            >
              <option value="google/gemini-2.0-flash">Gemini 2.0 Flash</option>
              <option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet</option>
              <option value="openai/gpt-4o">GPT-4o</option>
              <option value="meta-llama/llama-3.1-70b-instruct">Llama 3.1 70B</option>
            </select>
          </div>

          {messages.length > 0 && (
            <button
              onClick={onClearChat}
              className="chat-header-btn"
              title="Clear conversation"
              id="clear-chat-btn"
            >
              <Trash2 size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-screen" id="welcome-screen">
            <div className="welcome-eyebrow">AI-POWERED INTELLIGENCE</div>
            <h1 className="welcome-title">Know any company<br />in minutes.</h1>
            <p className="welcome-subtitle">
              Enter a company name or website URL below. We'll search and crawl public data to extract overview, products, competitors, and pain points in seconds.
            </p>

            <div className="example-chips-container">
              {EXAMPLE_COMPANIES.map((company, index) => (
                <button
                  key={company}
                  onClick={() => handleChipClick(company)}
                  className="example-chip"
                  id={`example-chip-${index}`}
                >
                  {company}
                </button>
              ))}
            </div>
            
            <div className="welcome-hint">
              Configure your API keys in the sidebar to get started.
            </div>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((msg, idx) => (
              <Message
                key={idx}
                role={msg.role}
                content={msg.content}
                report={msg.report}
                pdfUrl={msg.pdfUrl}
                targetUrl={msg.targetUrl}
                isError={msg.isError}
              />
            ))}
          </div>
        )}

        {/* Loading Steps Block */}
        {isLoading && (
          <div className="message ai loading-block-message">
            <div className="message-avatar ai">AI</div>
            <div className="message-content">
              <div className="loading-card" id="loading-card">
                <div className="loading-card-title">RESEARCHING COMPANY DETAILS</div>
                
                <div className="loading-steps-list">
                  {RESEARCH_STEPS.map((step, idx) => {
                    const isDone = currentStepIndex > idx
                    const isActive = currentStepIndex === idx
                    const isPending = currentStepIndex < idx

                    let statusClass = 'pending'
                    if (isDone) statusClass = 'done'
                    if (isActive) statusClass = 'active'

                    return (
                      <div key={idx} className={`loading-step-row ${statusClass}`}>
                        <div className={`step-indicator-circle ${statusClass}`}>
                          {isDone ? (
                            <Check size={11} strokeWidth={3} />
                          ) : isActive ? (
                            <div className="step-spinner" />
                          ) : (
                            <span className="step-num">{idx + 1}</span>
                          )}
                        </div>
                        <div className={`step-text-label ${statusClass}`}>
                          {step}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input Form */}
      <div className="input-container">
        <form onSubmit={handleSubmit} className="input-box" id="research-input-form">
          <textarea
            ref={textareaRef}
            rows={1}
            value={companyInput}
            onChange={(e) => setCompanyInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onInput={handleTextareaInput}
            placeholder="Enter a company name (e.g., Stripe) or website URL (e.g., figma.com)..."
            className="input-field"
            id="company-query-input"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !companyInput.trim()}
            className="submit-btn"
            id="query-submit-btn"
            title="Start Research"
          >
            Research
            <Send size={14} style={{ marginLeft: '4px' }} />
          </button>
        </form>
        <div className="footer-hint">
          ENTER TO RESEARCH · SHIFT+ENTER FOR NEW LINE
        </div>
      </div>
    </div>
  )
}

export default ChatArea
