import { useState, useEffect } from 'react'
import { CheckCircle, AlertCircle, AlertTriangle, Info, X } from 'lucide-react'

const ICON_MAP = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
}

const Toast = ({ id, type = 'info', title, message, duration = 4000, onClose }) => {
  const [exiting, setExiting] = useState(false)
  const IconComponent = ICON_MAP[type] || Info

  useEffect(() => {
    const timer = setTimeout(() => {
      setExiting(true)
      setTimeout(() => onClose(id), 300)
    }, duration)

    return () => clearTimeout(timer)
  }, [id, duration, onClose])

  const handleClose = () => {
    setExiting(true)
    setTimeout(() => onClose(id), 300)
  }

  return (
    <div
      className={`toast ${type} ${exiting ? 'exiting' : ''}`}
      id={`toast-${id}`}
      role="alert"
      style={{ position: 'relative', overflow: 'hidden' }}
    >
      <div className="toast-icon">
        <IconComponent size={14} />
      </div>
      <div className="toast-body">
        {title && <div className="toast-title">{title}</div>}
        {message && <div className="toast-message">{message}</div>}
      </div>
      <button
        className="toast-close"
        onClick={handleClose}
        id={`toast-close-${id}`}
        aria-label="Close notification"
      >
        <X size={14} />
      </button>
      <div
        className="toast-progress"
        style={{ animationDuration: `${duration}ms` }}
      />
    </div>
  )
}

export default Toast
