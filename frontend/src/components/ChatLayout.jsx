import React, { useState } from 'react'
import { MessageCircle, Download, Settings, Trash2, Plus } from 'lucide-react'

export default function ChatLayout({ children }) {
  const [conversations, setConversations] = useState([
    { id: 1, name: 'Project Alpha - QA Setup', date: 'Today' },
    { id: 2, name: 'E-commerce Testing', date: 'Yesterday' },
    { id: 3, name: 'API Automation', date: '2 days ago' },
    { id: 4, name: 'Mobile App Testing', date: '1 week ago' },
  ])
  const [activeConversation, setActiveConversation] = useState(1)
  const [showRightPanel, setShowRightPanel] = useState(true)

  return (
    <div className="flex h-screen bg-gray-900">
      {/* Left Sidebar - Conversations */}
      <div className="w-64 bg-gray-950 border-r border-gray-800 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-800">
          <button className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors">
            <Plus size={20} />
            <span>New Conversation</span>
          </button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              onClick={() => setActiveConversation(conv.id)}
              className={`p-4 border-b border-gray-800 cursor-pointer transition-colors ${
                activeConversation === conv.id
                  ? 'bg-blue-900 bg-opacity-30 border-l-4 border-l-blue-500'
                  : 'hover:bg-gray-800'
              }`}
            >
              <div className="flex items-start gap-3">
                <MessageCircle size={18} className="text-blue-400 mt-1 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-100 truncate">{conv.name}</p>
                  <p className="text-xs text-gray-500 mt-1">{conv.date}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Settings */}
        <div className="p-4 border-t border-gray-800">
          <button className="w-full flex items-center justify-center gap-2 text-gray-400 hover:text-gray-200 py-2 px-4 rounded-lg hover:bg-gray-800 transition-colors">
            <Settings size={18} />
            <span className="text-sm">Settings</span>
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-gray-900">
        {/* Chat Header */}
        <div className="border-b border-gray-800 bg-gray-950 px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-white">
              {conversations.find(c => c.id === activeConversation)?.name}
            </h1>
            <p className="text-sm text-gray-400 mt-1">QA Automation Assistant</p>
          </div>
          <button
            onClick={() => setShowRightPanel(!showRightPanel)}
            className="text-gray-400 hover:text-gray-200 transition-colors"
          >
            <Settings size={20} />
          </button>
        </div>

        {/* Chat Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {children}
        </div>

        {/* Chat Input */}
        <div className="border-t border-gray-800 bg-gray-950 p-6">
          <div className="flex gap-3">
            <input
              type="text"
              placeholder="Ask about your QA automation project..."
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
            />
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors font-medium active:bg-blue-800">
              Send
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">Press Enter to send or click Send button</p>
        </div>
      </div>

      {/* Right Sidebar - Options */}
      {showRightPanel && (
        <div className="w-80 bg-gray-950 border-l border-gray-800 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="p-4 border-b border-gray-800">
            <h2 className="text-lg font-bold text-white">Project Options</h2>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* Project Info */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-200 mb-3">Project Information</h3>
              <div className="space-y-2 text-sm">
                <div>
                  <p className="text-gray-400">Status</p>
                  <p className="text-green-400 font-medium">Active</p>
                </div>
                <div>
                  <p className="text-gray-400">Framework</p>
                  <p className="text-blue-400 font-medium">Selenium + Python</p>
                </div>
                <div>
                  <p className="text-gray-400">Test Cases</p>
                  <p className="text-blue-400 font-medium">24 Total</p>
                </div>
              </div>
            </div>

            {/* Download Section */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-200 mb-3 flex items-center gap-2">
                <Download size={16} />
                Downloads
              </h3>
              <div className="space-y-2">
                <button className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-200 transition-colors">
                  📄 Test Scripts
                </button>
                <button className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-200 transition-colors">
                  📊 Test Report
                </button>
                <button className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-200 transition-colors">
                  🔧 Configuration
                </button>
                <button className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-200 transition-colors">
                  📦 Full Package
                </button>
              </div>
            </div>

            {/* Actions */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-200 mb-3">Actions</h3>
              <div className="space-y-2">
                <button className="w-full text-left px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm text-white transition-colors font-medium">
                  ▶️ Run Tests
                </button>
                <button className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-200 transition-colors">
                  🔄 Regenerate
                </button>
                <button className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-200 transition-colors">
                  📋 View Logs
                </button>
              </div>
            </div>

            {/* Statistics */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-200 mb-3">Statistics</h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-400">Test Coverage</span>
                    <span className="text-green-400">85%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '85%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-400">Automation Rate</span>
                    <span className="text-blue-400">72%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '72%' }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Delete Section */}
          <div className="p-4 border-t border-gray-800">
            <button className="w-full flex items-center justify-center gap-2 text-red-400 hover:text-red-300 py-2 px-4 rounded-lg hover:bg-red-900 hover:bg-opacity-20 transition-colors">
              <Trash2 size={18} />
              <span className="text-sm">Delete Project</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
