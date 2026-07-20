import React, { useState } from 'react'
import { MessageCircle, Download, Settings, Trash2, Plus, X, AlertTriangle, RefreshCw, PlayCircle, FileText } from 'lucide-react'

export default function ChatLayout({ 
  children, 
  onNewConversation, 
  onFileUpload, 
  onGenerateCode, 
  isGenerating, 
  uploadedFiles,
  currentProjectId,
  inputValue,
  onInputChange,
  onSendMessage,
  generationStats,
  onDeleteProject
}) {
  const [conversations, setConversations] = useState([
    { id: 1, name: 'Project Alpha - QA Setup', date: 'Today' },
    { id: 2, name: 'E-commerce Testing', date: 'Yesterday' },
    { id: 3, name: 'API Automation', date: '2 days ago' },
    { id: 4, name: 'Mobile App Testing', date: '1 week ago' },
  ])
  const [activeConversation, setActiveConversation] = useState(1)
  const [showRightPanel, setShowRightPanel] = useState(true)
  const [showNewConvModal, setShowNewConvModal] = useState(false)
  const [newConvName, setNewConvName] = useState('')
  const [showRunTestsModal, setShowRunTestsModal] = useState(false)
  const [showViewLogsModal, setShowViewLogsModal] = useState(false)
  const [showSettingsModal, setShowSettingsModal] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const handleDeleteConfirmed = async () => {
    setShowDeleteConfirm(false)
    if (onDeleteProject) await onDeleteProject()
  }

  const handleCreateConversation = async () => {
    if (!newConvName.trim()) {
      alert('Please enter a project name')
      return
    }

    try {
      // Call backend API to create project
      const response = await fetch('http://localhost:8000/api/projects?project_name=' + encodeURIComponent(newConvName) + '&description=QA Automation Project', {
        method: 'POST',
      })
      
      if (response.ok) {
        const data = await response.json()
        const newConv = {
          id: conversations.length + 1,
          name: newConvName,
          date: 'Today',
          projectId: data.project_id
        }
        setConversations([newConv, ...conversations])
        setActiveConversation(newConv.id)
        setNewConvName('')
        setShowNewConvModal(false)
        
        if (onNewConversation) {
          onNewConversation(data.project_id)
        }
      } else {
        alert('Failed to create project')
      }
    } catch (error) {
      console.error('Error creating project:', error)
      alert('Error creating project: ' + error.message)
    }
  }

  return (
    <div className="flex h-screen bg-gray-900">
      {/* Left Sidebar - Conversations */}
      <div className="w-64 bg-gray-950 border-r border-gray-800 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-800">
          <button 
            onClick={() => setShowNewConvModal(true)}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors"
          >
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
          <button
            onClick={() => setShowSettingsModal(true)}
            className="w-full flex items-center justify-center gap-2 text-gray-400 hover:text-gray-200 py-2 px-4 rounded-lg hover:bg-gray-800 transition-colors"
          >
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
              value={inputValue || ''}
              onChange={(e) => onInputChange && onInputChange(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && onSendMessage && onSendMessage()}
              placeholder="Ask about your QA automation project..."
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
            />
            <button
              onClick={() => onSendMessage && onSendMessage()}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors font-medium active:bg-blue-800"
            >
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
            {/* Upload Documents */}
            {currentProjectId && (
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-200 mb-3">Upload Documents</h3>
                <div className="space-y-2">
                  <label className="block">
                    <input
                      type="file"
                      accept=".txt,.docx,.pdf"
                      onChange={(e) => e.target.files?.[0] && onFileUpload(e.target.files[0], 'functional_specification')}
                      className="hidden"
                    />
                    <div className={`w-full text-left px-3 py-2 rounded text-sm transition-colors cursor-pointer ${
                      uploadedFiles?.functional_specification 
                        ? 'bg-green-700 text-white' 
                        : 'bg-gray-700 hover:bg-gray-600 text-gray-200'
                    }`}>
                      {uploadedFiles?.functional_specification ? '✓ Feature Spec' : '📋 Feature Spec'}
                    </div>
                  </label>
                  <label className="block">
                    <input
                      type="file"
                      accept=".txt,.docx,.xlsx,.csv"
                      onChange={(e) => e.target.files?.[0] && onFileUpload(e.target.files[0], 'test_cases')}
                      className="hidden"
                    />
                    <div className={`w-full text-left px-3 py-2 rounded text-sm transition-colors cursor-pointer ${
                      uploadedFiles?.test_cases 
                        ? 'bg-green-700 text-white' 
                        : 'bg-gray-700 hover:bg-gray-600 text-gray-200'
                    }`}>
                      {uploadedFiles?.test_cases ? '✓ Test Cases' : '📝 Test Cases'}
                    </div>
                  </label>
                  <label className="block">
                    <input
                      type="file"
                      accept=".txt,.docx,.pdf"
                      onChange={(e) => e.target.files?.[0] && onFileUpload(e.target.files[0], 'expected_output')}
                      className="hidden"
                    />
                    <div className={`w-full text-left px-3 py-2 rounded text-sm transition-colors cursor-pointer ${
                      uploadedFiles?.expected_output 
                        ? 'bg-green-700 text-white' 
                        : 'bg-gray-700 hover:bg-gray-600 text-gray-200'
                    }`}>
                      {uploadedFiles?.expected_output ? '✓ Expected Output' : '📊 Expected Output'}
                    </div>
                  </label>
                </div>
              </div>
            )}

            {/* Generate Button */}
            {currentProjectId && (
              <button
                onClick={onGenerateCode}
                disabled={isGenerating}
                className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                  isGenerating
                    ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {isGenerating ? '⏳ Generating...' : '🚀 Generate Code'}
              </button>
            )}

            {/* Project Info */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-200 mb-3">Project Information</h3>
              <div className="space-y-2 text-sm">
                <div>
                  <p className="text-gray-400">Status</p>
                  <p className={`font-medium ${generationStats ? 'text-green-400' : currentProjectId ? 'text-yellow-400' : 'text-gray-500'}`}>
                    {generationStats ? 'Generated ✓' : currentProjectId ? 'Active' : 'No project'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-400">Framework</p>
                  <p className="text-blue-400 font-medium">
                    {generationStats?.framework?.selected_framework || 'Java / Selenium'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-400">Test Cases</p>
                  <p className="text-blue-400 font-medium">
                    {generationStats ? `${generationStats.total_test_cases} Total` : '—'}
                  </p>
                </div>
                {generationStats && (
                  <>
                    <div>
                      <p className="text-gray-400">Feature Files</p>
                      <p className="text-blue-400 font-medium">{generationStats.total_features}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Page Objects</p>
                      <p className="text-blue-400 font-medium">{generationStats.total_pages}</p>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Download Section */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-200 mb-3 flex items-center gap-2">
                <Download size={16} />
                Downloads
              </h3>
              <div className="space-y-2">
                <button
                  onClick={() => {
                    if (!currentProjectId) { alert('Please generate code first'); return; }
                    window.open(`http://localhost:8000/api/projects/${currentProjectId}/download`, '_blank')
                  }}
                  className="w-full text-left px-3 py-2 bg-green-700 hover:bg-green-600 rounded text-sm text-white transition-colors font-medium flex items-center gap-2"
                >
                  <Download size={14} /> 📦 Download All Files (ZIP)
                </button>
              </div>
            </div>

            {/* Actions */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-200 mb-3">Actions</h3>
              <div className="space-y-2">
                <button
                  onClick={() => setShowRunTestsModal(true)}
                  className="w-full text-left px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm text-white transition-colors font-medium flex items-center gap-2"
                >
                  <PlayCircle size={14} /> ▶️ Run Tests
                </button>
                <button
                  onClick={onGenerateCode}
                  disabled={isGenerating || !currentProjectId}
                  className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <RefreshCw size={14} /> 🔄 Regenerate
                </button>
                <button
                  onClick={() => setShowViewLogsModal(true)}
                  className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-200 transition-colors flex items-center gap-2"
                >
                  <FileText size={14} /> 📋 View Logs
                </button>
              </div>
            </div>

            {/* Statistics */}
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-200 mb-3">Statistics</h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-400">Feature Coverage</span>
                    <span className="text-green-400">
                      {generationStats
                        ? `${Math.min(100, generationStats.total_features > 0 ? 100 : 0)}%`
                        : '0%'}
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{ width: generationStats && generationStats.total_features > 0 ? '100%' : '0%' }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-400">Page Objects</span>
                    <span className="text-blue-400">
                      {generationStats ? `${generationStats.total_pages} files` : '0 files'}
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: generationStats && generationStats.total_pages > 0 ? '100%' : '0%' }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Delete Section */}
          <div className="p-4 border-t border-gray-800">
            <button
              onClick={() => currentProjectId && setShowDeleteConfirm(true)}
              disabled={!currentProjectId}
              className="w-full flex items-center justify-center gap-2 text-red-400 hover:text-red-300 py-2 px-4 rounded-lg hover:bg-red-900 hover:bg-opacity-20 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Trash2 size={18} />
              <span className="text-sm">Delete Project</span>
            </button>
          </div>
        </div>
      )}

      {/* New Conversation Modal */}
      {showNewConvModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-950 border border-gray-800 rounded-lg p-6 w-96">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">Create New Project</h2>
              <button onClick={() => { setShowNewConvModal(false); setNewConvName('') }} className="text-gray-400 hover:text-white"><X size={20} /></button>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">Project Name</label>
              <input
                type="text"
                value={newConvName}
                onChange={(e) => setNewConvName(e.target.value)}
                placeholder="e.g., E-Commerce Testing"
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                onKeyPress={(e) => e.key === 'Enter' && handleCreateConversation()}
              />
            </div>
            <div className="flex gap-3">
              <button onClick={handleCreateConversation} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors font-medium">Create</button>
              <button onClick={() => { setShowNewConvModal(false); setNewConvName('') }} className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded-lg transition-colors">Cancel</button>
            </div>
          </div>
        </div>
      )}

      {/* Run Tests Modal */}
      {showRunTestsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-950 border border-gray-800 rounded-lg p-6 w-[500px] max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white flex items-center gap-2"><PlayCircle size={20} className="text-blue-400" /> Run Tests</h2>
              <button onClick={() => setShowRunTestsModal(false)} className="text-gray-400 hover:text-white"><X size={20} /></button>
            </div>
            <div className="space-y-4 text-sm text-gray-300">
              <p>To run the generated Java Selenium + Cucumber tests, follow these steps:</p>
              <div>
                <p className="text-gray-200 font-semibold mb-1">1. Download the generated files:</p>
                <p className="text-gray-400">Click "Download All Files (ZIP)" and extract to your workspace.</p>
              </div>
              <div>
                <p className="text-gray-200 font-semibold mb-1">2. Prerequisites:</p>
                <ul className="list-disc list-inside space-y-1 text-gray-400">
                  <li>Java JDK 11+</li>
                  <li>Maven 3.6+</li>
                  <li>Chrome browser + ChromeDriver on PATH</li>
                </ul>
              </div>
              <div>
                <p className="text-gray-200 font-semibold mb-1">3. Run all tests:</p>
                <pre className="bg-gray-800 rounded p-3 text-green-400 text-xs">{`cd your-project-folder\nmvn clean test`}</pre>
              </div>
              <div>
                <p className="text-gray-200 font-semibold mb-1">4. Run by tag:</p>
                <pre className="bg-gray-800 rounded p-3 text-green-400 text-xs">{`mvn test -Dcucumber.filter.tags="@smoke"`}</pre>
              </div>
              <div>
                <p className="text-gray-200 font-semibold mb-1">5. Reports:</p>
                <p className="text-gray-400">Generated at <code className="text-yellow-400">target/cucumber-reports/</code></p>
              </div>
            </div>
            <button onClick={() => setShowRunTestsModal(false)} className="mt-5 w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition-colors">Close</button>
          </div>
        </div>
      )}

      {/* View Logs Modal */}
      {showViewLogsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-950 border border-gray-800 rounded-lg p-6 w-[500px] max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white flex items-center gap-2"><FileText size={20} className="text-blue-400" /> Generation Logs</h2>
              <button onClick={() => setShowViewLogsModal(false)} className="text-gray-400 hover:text-white"><X size={20} /></button>
            </div>
            {generationStats ? (
              <div className="space-y-3 text-sm">
                <div className="bg-green-900 bg-opacity-30 border border-green-700 rounded p-3">
                  <p className="text-green-400 font-semibold">✓ Last Generation Successful</p>
                </div>
                <div className="bg-gray-800 rounded p-3 space-y-2 text-gray-300">
                  <p><span className="text-gray-400">Project ID:</span> {generationStats.project_id || currentProjectId}</p>
                  <p><span className="text-gray-400">Workflow ID:</span> {generationStats.workflow_id || 'N/A'}</p>
                  <p><span className="text-gray-400">Framework:</span> {generationStats.framework?.selected_framework || 'Java / Selenium'}</p>
                  <p><span className="text-gray-400">Test Cases:</span> {generationStats.total_test_cases}</p>
                  <p><span className="text-gray-400">Feature Files:</span> {generationStats.total_features}</p>
                  <p><span className="text-gray-400">Page Objects:</span> {generationStats.total_pages}</p>
                  <p><span className="text-gray-400">Status:</span> <span className="text-green-400">{generationStats.status}</span></p>
                </div>
              </div>
            ) : (
              <div className="text-gray-400 text-sm text-center py-8">
                <FileText size={40} className="mx-auto mb-3 opacity-40" />
                <p>No generation logs yet.</p>
                <p className="mt-1">Upload documents and click "Generate Code" to see logs here.</p>
              </div>
            )}
            <button onClick={() => setShowViewLogsModal(false)} className="mt-4 w-full bg-gray-700 hover:bg-gray-600 text-white py-2 rounded-lg transition-colors">Close</button>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettingsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-950 border border-gray-800 rounded-lg p-6 w-96">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white flex items-center gap-2"><Settings size={20} className="text-blue-400" /> Settings</h2>
              <button onClick={() => setShowSettingsModal(false)} className="text-gray-400 hover:text-white"><X size={20} /></button>
            </div>
            <div className="space-y-4 text-sm">
              <div>
                <label className="block text-gray-400 mb-1">Backend API URL</label>
                <input readOnly value="http://localhost:8000/api" className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-gray-300 text-xs" />
              </div>
              <div>
                <label className="block text-gray-400 mb-1">LLM Provider</label>
                <input readOnly value="Azure OpenAI (gpt-4o-mini)" className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-gray-300 text-xs" />
              </div>
              <div>
                <label className="block text-gray-400 mb-1">Generated Framework</label>
                <input readOnly value="Java Selenium + Cucumber (Maven)" className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-gray-300 text-xs" />
              </div>
            </div>
            <button onClick={() => setShowSettingsModal(false)} className="mt-4 w-full bg-gray-700 hover:bg-gray-600 text-white py-2 rounded-lg transition-colors">Close</button>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-950 border border-gray-800 rounded-lg p-6 w-96">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle size={24} className="text-red-400 flex-shrink-0" />
              <h2 className="text-xl font-bold text-white">Delete Project?</h2>
            </div>
            <p className="text-gray-400 text-sm mb-6">This will permanently delete the project and all associated documents and generated files. This action cannot be undone.</p>
            <div className="flex gap-3">
              <button onClick={handleDeleteConfirmed} className="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-lg transition-colors font-medium">Delete</button>
              <button onClick={() => setShowDeleteConfirm(false)} className="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded-lg transition-colors">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
