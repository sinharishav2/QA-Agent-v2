import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { Upload, Loader, ArrowLeft, Play, Download } from 'lucide-react'
import { toast } from '../components/Toaster'

function ProjectDetail() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [selectedFiles, setSelectedFiles] = useState({})

  useEffect(() => {
    loadProject()
  }, [projectId])

  const loadProject = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`/api/projects/${projectId}`)
      setProject(response.data)
    } catch (error) {
      toast.error('Failed to load project')
      navigate('/')
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (e, docType) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFiles(prev => ({
        ...prev,
        [docType]: file
      }))
    }
  }

  const handleUpload = async (docType) => {
    const file = selectedFiles[docType]
    if (!file) {
      toast.error('Please select a file')
      return
    }

    try {
      setLoading(true)
      const formData = new FormData()
      formData.append('file', file)

      await axios.post(`/api/projects/${projectId}/upload`, formData, {
        params: { document_type: docType },
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      toast.success('File uploaded successfully')
      setSelectedFiles(prev => ({ ...prev, [docType]: null }))
      setUploadedFiles(prev => [...prev, { name: file.name, type: docType }])
    } catch (error) {
      toast.error('Failed to upload file')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateAutomation = async () => {
    if (uploadedFiles.length === 0) {
      toast.error('Please upload at least one document')
      return
    }

    try {
      setGenerating(true)
      const response = await axios.post(`/api/projects/${projectId}/generate`)
      toast.success('Automation generation started!')
      loadProject()
    } catch (error) {
      toast.error('Failed to generate automation')
      console.error(error)
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader className="animate-spin text-primary-600" size={32} />
      </div>
    )
  }

  if (!project) {
    return <div>Project not found</div>
  }

  return (
    <div className="space-y-8">
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-2 text-primary-600 hover:text-primary-700 transition"
      >
        <ArrowLeft size={20} />
        Back to Projects
      </button>

      <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{project.project_name}</h1>
        <p className="text-gray-600 mb-4">{project.description || 'No description'}</p>
        <div className="flex gap-4 text-sm">
          <span className={`px-3 py-1 rounded-full text-white ${
            project.status === 'draft' ? 'bg-gray-500' :
            project.status === 'automation_generated' ? 'bg-success-500' :
            'bg-primary-500'
          }`}>
            {project.status}
          </span>
          {project.automation_framework && (
            <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-700">
              {project.automation_framework}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload Documents</h2>
          <div className="space-y-6">
            {['functional_specification', 'test_cases', 'expected_output'].map(docType => (
              <div key={docType} className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                <label className="block text-sm font-medium text-gray-700 mb-2 capitalize">
                  {docType.replace(/_/g, ' ')}
                </label>
                <input
                  type="file"
                  onChange={(e) => handleFileSelect(e, docType)}
                  accept=".docx,.xlsx,.xls,.pdf"
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                />
                <button
                  onClick={() => handleUpload(docType)}
                  disabled={loading || !selectedFiles[docType]}
                  className="mt-3 w-full flex items-center justify-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition disabled:opacity-50"
                >
                  <Upload size={18} />
                  Upload
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Uploaded Files</h2>
          {uploadedFiles.length === 0 ? (
            <p className="text-gray-500">No files uploaded yet</p>
          ) : (
            <ul className="space-y-3">
              {uploadedFiles.map((file, idx) => (
                <li key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{file.name}</p>
                    <p className="text-sm text-gray-500 capitalize">{file.type.replace(/_/g, ' ')}</p>
                  </div>
                  <Download size={18} className="text-primary-600" />
                </li>
              ))}
            </ul>
          )}

          <button
            onClick={handleGenerateAutomation}
            disabled={generating || uploadedFiles.length === 0}
            className="mt-8 w-full flex items-center justify-center gap-2 bg-success-500 text-white px-6 py-3 rounded-lg hover:bg-success-600 transition disabled:opacity-50 font-semibold"
          >
            {generating ? (
              <>
                <Loader className="animate-spin" size={20} />
                Generating...
              </>
            ) : (
              <>
                <Play size={20} />
                Generate Automation
              </>
            )}
          </button>
        </div>
      </div>

      {project.status === 'automation_generated' && (
        <div className="bg-success-50 border border-success-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-success-900 mb-2">Automation Generated Successfully!</h3>
          <p className="text-success-700">Your automation framework is ready for download and execution.</p>
        </div>
      )}
    </div>
  )
}

export default ProjectDetail
