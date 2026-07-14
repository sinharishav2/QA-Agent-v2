import React, { useState, useEffect } from 'react'
import { CheckCircle, AlertCircle, XCircle } from 'lucide-react'

const toastStore = {
  toasts: [],
  listeners: [],
  
  subscribe(listener) {
    this.listeners.push(listener)
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener)
    }
  },
  
  notify(message, type = 'info', duration = 3000) {
    const id = Date.now()
    const toast = { id, message, type }
    this.toasts.push(toast)
    this.listeners.forEach(l => l([...this.toasts]))
    
    setTimeout(() => {
      this.toasts = this.toasts.filter(t => t.id !== id)
      this.listeners.forEach(l => l([...this.toasts]))
    }, duration)
  }
}

export const toast = {
  success: (msg) => toastStore.notify(msg, 'success'),
  error: (msg) => toastStore.notify(msg, 'error'),
  info: (msg) => toastStore.notify(msg, 'info'),
}

function Toaster() {
  const [toasts, setToasts] = useState([])

  useEffect(() => {
    const unsubscribe = toastStore.subscribe(setToasts)
    return unsubscribe
  }, [])

  return (
    <div className="fixed bottom-4 right-4 space-y-2 z-50">
      {toasts.map(t => (
        <div
          key={t.id}
          className={`flex items-center gap-2 px-4 py-3 rounded-lg shadow-lg text-white animate-slide-in ${
            t.type === 'success' ? 'bg-success-500' :
            t.type === 'error' ? 'bg-error-500' :
            'bg-primary-500'
          }`}
        >
          {t.type === 'success' && <CheckCircle size={20} />}
          {t.type === 'error' && <XCircle size={20} />}
          {t.type === 'info' && <AlertCircle size={20} />}
          <span>{t.message}</span>
        </div>
      ))}
    </div>
  )
}

export default Toaster
