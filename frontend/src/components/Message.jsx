import { User, Download, ExternalLink, Phone, MapPin, Package, ShieldAlert, Users, Check } from 'lucide-react'

const Message = ({ role, content, report, pdfUrl, targetUrl, isError }) => {
  const isUser = role === 'user'
  const API_BASE = window.location.port === '5173' ? 'http://127.0.0.1:8000' : ''

  if (isUser) {
    return (
      <div className="message user" id="user-message">
        <div className="avatar user">
          <User size={18} />
        </div>
        <div className="message-content">
          <p style={{ margin: 0 }}>{content}</p>
        </div>
      </div>
    )
  }

  // AI Message - Error state or basic markdown (no structured report)
  if (isError || !report) {
    return (
      <div className={`message ai ${isError ? 'error-state' : ''}`} id="ai-error-message">
        <div className="avatar ai">AI</div>
        <div className="message-content">
          <div className="error-text-container">
            {content || 'An unexpected error occurred during company analysis.'}
          </div>
        </div>
      </div>
    )
  }

  // AI Message - Beautiful Structured Report Layout
  const {
    company_name,
    website,
    phone,
    address,
    summary,
    products = [],
    pain_points = [],
    competitors = [],
  } = report

  return (
    <div className="message ai report-message" id="ai-report-message">
      <div className="avatar ai">AI</div>
      
      <div className="message-content">
        <div className="report-card" id={`report-card-${company_name.replace(/\s+/g, '-').toLowerCase()}`}>
          
          {/* Header Section */}
          <div className="report-head">
            <div>
              <h3 className="report-company-name">{company_name}</h3>
              {website && website !== 'Not listed' ? (
                <a
                  href={website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="report-website"
                  id="report-website-link"
                >
                  {website}
                  <ExternalLink size={11} style={{ marginLeft: '4px', display: 'inline-block', verticalAlign: 'middle' }} />
                </a>
              ) : (
                <span className="report-website muted">Website not listed</span>
              )}
            </div>
            <div className="report-complete-badge">
              <Check size={12} style={{ marginRight: '4px' }} />
              RESEARCH COMPLETE
            </div>
          </div>

          {/* Metadata Grid */}
          <div className="report-grid">
            <div className="report-stat">
              <div className="report-stat-label">
                <Phone size={10} />
                PHONE
              </div>
              <div className="report-stat-value">{phone}</div>
            </div>
            <div className="report-stat">
              <div className="report-stat-label">
                <MapPin size={10} />
                ADDRESS
              </div>
              <div className="report-stat-value">{address}</div>
            </div>
          </div>

          {/* Overview */}
          <div className="report-section">
            <div className="report-section-title overview">
              1. COMPANY OVERVIEW
            </div>
            <div className="report-summary-text">
              {summary}
            </div>
          </div>

          {/* Products & Services */}
          <div className="report-section">
            <div className="report-section-title products">
              <Package size={12} style={{ marginRight: '6px' }} />
              2. KEY PRODUCTS & SERVICES
            </div>
            <div className="chip-row">
              {products.length > 0 ? (
                products.map((product, i) => (
                  <div key={i} className="product-chip">
                    {product}
                  </div>
                ))
              ) : (
                <div className="no-data-msg">No key products or services detected.</div>
              )}
            </div>
          </div>

          {/* Pain Points */}
          <div className="report-section">
            <div className="report-section-title pain">
              <ShieldAlert size={12} style={{ marginRight: '6px' }} />
              3. AI-GENERATED PAIN POINTS
            </div>
            <div className="pain-points-list">
              {pain_points.length > 0 ? (
                pain_points.map((point, i) => (
                  <div key={i} className="pain-row">
                    <div className="pain-dot" />
                    <div className="pain-text">{point}</div>
                  </div>
                ))
              ) : (
                <div className="no-data-msg">No specific pain points identified.</div>
              )}
            </div>
          </div>

          {/* Competitors */}
          <div className="report-section">
            <div className="report-section-title competitors">
              <Users size={12} style={{ marginRight: '6px' }} />
              4. DIRECT COMPETITORS
            </div>
            <div className="competitor-grid">
              {competitors.length > 0 ? (
                competitors.map((comp, i) => (
                  <div key={i} className="competitor-card" id={`competitor-card-${i}`}>
                    <div className="competitor-name">{comp.name}</div>
                    {comp.website && comp.website !== 'N/A' && comp.website !== 'Not listed' ? (
                      <a
                        href={comp.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="competitor-site"
                      >
                        {comp.website}
                        <ExternalLink size={10} style={{ marginLeft: '2px' }} />
                      </a>
                    ) : (
                      <div className="competitor-site-empty">Website not listed</div>
                    )}
                  </div>
                ))
              ) : (
                <div className="no-data-msg">No direct competitors found.</div>
              )}
            </div>
          </div>

          {/* Actions Bar */}
          <div className="report-actions">
            {pdfUrl && (
              <a
                href={`${API_BASE}${pdfUrl}`}
                download
                className="download-btn"
                target="_blank"
                rel="noreferrer"
                id="pdf-download-button"
              >
                <Download size={14} />
                Download PDF Report
              </a>
            )}
            
            {/* Discord Status notification pill */}
            <div className="discord-status-pill sent">
              <div className="discord-indicator-dot" />
              <span>Hiring channels notified</span>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}

export default Message
