import React, { useState, useEffect } from 'react'
import ChatLayout from '../components/ChatLayout'
import ChatMessage from '../components/ChatMessage'

const API_BASE_URL = 'http://localhost:8000/api'

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'Hello! I\'m your QA Automation Assistant. Upload your documents (feature spec, test cases, and expected output) to get started.',
      isUser: false,
    },
  ])
  const [inputValue, setInputValue] = useState('')
  const [currentProjectId, setCurrentProjectId] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState({})
  const [generationStats, setGenerationStats] = useState(null)

  const handleNewConversation = (projectId) => {
    setCurrentProjectId(projectId)
    setMessages([
      {
        id: 1,
        text: 'Project created! Now upload your 3 documents: feature specification, test cases, and expected output.',
        isUser: false,
      },
    ])
    setUploadedFiles({})
    setGenerationStats(null)
  }

  const handleFileUpload = async (file, documentType) => {
    if (!currentProjectId) {
      alert('Please create a project first')
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('document_type', documentType)

      const response = await fetch(`${API_BASE_URL}/projects/${currentProjectId}/upload`, {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        setUploadedFiles({
          ...uploadedFiles,
          [documentType]: true,
        })

        const newMessage = {
          id: messages.length + 1,
          text: `✓ Uploaded ${documentType.replace('_', ' ')}`,
          isUser: false,
        }
        setMessages([...messages, newMessage])
      } else {
        alert('Failed to upload file')
      }
    } catch (error) {
      console.error('Error uploading file:', error)
      alert('Error uploading file: ' + error.message)
    }
  }

  const handleGenerateCode = async () => {
    if (!currentProjectId) {
      alert('Please create a project first')
      return
    }

    const requiredDocs = ['functional_specification', 'test_cases', 'expected_output']
    const missingDocs = requiredDocs.filter(doc => !uploadedFiles[doc])

    if (missingDocs.length > 0) {
      alert(`Please upload all required documents: ${missingDocs.join(', ')}`)
      return
    }

    setIsGenerating(true)
    const generatingMsg = {
      id: messages.length + 1,
      text: '⏳ Generating automation code... This may take a minute.',
      isUser: false,
    }
    setMessages([...messages, generatingMsg])

    try {
      const response = await fetch(`${API_BASE_URL}/projects/${currentProjectId}/generate`, {
        method: 'POST',
      })

      if (response.ok) {
        const data = await response.json()
        setGenerationStats(data)
        const successMsg = {
          id: messages.length + 2,
          text: `✓ Code generation complete!\n\n📊 Generated:\n• Test Scripts: ${data.total_test_cases} test cases\n• Feature Files: ${data.total_features} features\n• Page Objects: ${data.total_pages} pages\n\nFramework: ${data.framework?.selected_framework || 'Java/Selenium'}\n\nYou can now download the generated files from the right panel.`,
          isUser: false,
        }
        setMessages((prev) => [...prev.slice(0, -1), successMsg])
      } else {
        const errorMsg = {
          id: messages.length + 2,
          text: '❌ Failed to generate code. Please check your documents and try again.',
          isUser: false,
        }
        setMessages((prev) => [...prev.slice(0, -1), errorMsg])
      }
    } catch (error) {
      console.error('Error generating code:', error)
      const errorMsg = {
        id: messages.length + 2,
        text: '❌ Error: ' + error.message,
        isUser: false,
      }
      setMessages((prev) => [...prev.slice(0, -1), errorMsg])
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDeleteProject = async () => {
    if (!currentProjectId) return
    try {
      await fetch(`${API_BASE_URL}/projects/${currentProjectId}`, { method: 'DELETE' })
    } catch (error) {
      console.error('Error deleting project:', error)
    }
    setCurrentProjectId(null)
    setUploadedFiles({})
    setGenerationStats(null)
    setMessages([{ id: 1, text: 'Project deleted. Create a new conversation to start over.', isUser: false }])
  }

  const handleSendMessage = async () => {
    const text = inputValue.trim()
    if (!text) return

    const userMsg = { id: Date.now(), text, isUser: true }
    const typingId = Date.now() + 1
    const typingMsg = { id: typingId, text: '⏳ Thinking...', isUser: false, isTyping: true }

    setMessages(prev => [...prev, userMsg, typingMsg])
    setInputValue('')

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, project_id: currentProjectId }),
      })

      const data = response.ok ? await response.json() : null
      const replyText = data?.response || 'Sorry, I could not get a response. Please try again.'

      setMessages(prev => [
        ...prev.filter(m => m.id !== typingId),
        { id: Date.now() + 2, text: replyText, isUser: false },
      ])
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => [
        ...prev.filter(m => m.id !== typingId),
        { id: Date.now() + 2, text: 'Error reaching the server. Please make sure the backend is running.', isUser: false },
      ])
    }
  }

  return (
    <ChatLayout 
      onNewConversation={handleNewConversation}
      onFileUpload={handleFileUpload}
      onGenerateCode={handleGenerateCode}
      isGenerating={isGenerating}
      uploadedFiles={uploadedFiles}
      currentProjectId={currentProjectId}
      inputValue={inputValue}
      onInputChange={setInputValue}
      onSendMessage={handleSendMessage}
      generationStats={generationStats}
      onDeleteProject={handleDeleteProject}
    >
      <div className="space-y-4">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg.text} isUser={msg.isUser} />
        ))}
      </div>
    </ChatLayout>
  )
}
