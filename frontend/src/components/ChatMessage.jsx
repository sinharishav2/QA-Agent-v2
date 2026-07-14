import React from 'react'
import { User, Bot } from 'lucide-react'

export default function ChatMessage({ message, isUser }) {
  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
            <Bot size={18} className="text-white" />
          </div>
        </div>
      )}
      
      <div className={`max-w-xs lg:max-w-md ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`rounded-lg px-4 py-2 ${
            isUser
              ? 'bg-blue-600 text-white rounded-br-none'
              : 'bg-gray-800 text-gray-100 rounded-bl-none'
          }`}
        >
          <p className="text-sm">{message}</p>
        </div>
      </div>

      {isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
            <User size={18} className="text-gray-300" />
          </div>
        </div>
      )}
    </div>
  )
}
