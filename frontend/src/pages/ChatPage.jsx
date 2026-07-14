import React, { useState } from 'react'
import ChatLayout from '../components/ChatLayout'
import ChatMessage from '../components/ChatMessage'

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'Hello! I\'m your QA Automation Assistant. I can help you create automated test scripts, generate test cases, and manage your QA projects. What would you like to do today?',
      isUser: false,
    },
    {
      id: 2,
      text: 'I need to create test cases for my e-commerce application',
      isUser: true,
    },
    {
      id: 3,
      text: 'Great! I can help with that. I\'ll need some information about your application:\n\n1. What are the main features you want to test?\n2. Do you have any existing test documentation?\n3. What\'s your preferred testing framework?\n\nOnce I have these details, I can generate comprehensive test cases for you.',
      isUser: false,
    },
    {
      id: 4,
      text: 'The main features are: user registration, product search, shopping cart, and checkout. We have a functional spec document. We prefer Selenium with Python.',
      isUser: true,
    },
    {
      id: 5,
      text: 'Perfect! Based on your requirements, I\'ve analyzed your functional specification and generated:\n\n✓ 24 test cases covering all features\n✓ Page object models for maintainability\n✓ Step definitions for BDD framework\n✓ Test data generators\n✓ Selenium Python scripts\n\nYou can download all the generated files from the right panel. Would you like me to explain any specific test case or generate additional scenarios?',
      isUser: false,
    },
  ])
  const [inputValue, setInputValue] = useState('')

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      const newMessage = {
        id: messages.length + 1,
        text: inputValue,
        isUser: true,
      }
      setMessages([...messages, newMessage])
      setInputValue('')

      // Simulate bot response
      setTimeout(() => {
        const botResponse = {
          id: messages.length + 2,
          text: 'I\'ve processed your request. You can now download the generated automation scripts from the right panel.',
          isUser: false,
        }
        setMessages((prev) => [...prev, botResponse])
      }, 1000)
    }
  }

  return (
    <ChatLayout>
      <div className="space-y-4">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg.text} isUser={msg.isUser} />
        ))}
      </div>
    </ChatLayout>
  )
}
