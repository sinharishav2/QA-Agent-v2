import React from 'react'
import { Link } from 'react-router-dom'
import { Zap } from 'lucide-react'

function Navbar() {
  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-2xl font-bold text-primary-600">
          <Zap size={28} />
          QA AI Platform
        </Link>
        <div className="flex gap-6">
          <Link to="/" className="text-gray-700 hover:text-primary-600 transition">
            Dashboard
          </Link>
          <a href="#docs" className="text-gray-700 hover:text-primary-600 transition">
            Documentation
          </a>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
