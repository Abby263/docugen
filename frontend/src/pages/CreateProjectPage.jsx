import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { projectsAPI } from '@/lib/api'
import toast from 'react-hot-toast'

const documentTypes = [
  { value: 'report', label: 'General Report', description: 'Comprehensive overview of any topic' },
  { value: 'analysis', label: 'Analysis', description: 'In-depth analytical report' },
  { value: 'research', label: 'Research', description: 'Academic research document' },
  { value: 'daily', label: 'Daily Brief', description: 'Quick daily summary' },
  { value: 'ppt', label: 'Presentation', description: 'Multi-slide HTML presentation' },
]

const outputFormats = [
  { value: 'html', label: 'HTML', description: 'Web-friendly format' },
  { value: 'markdown', label: 'Markdown', description: 'Plain text format' },
]

export default function CreateProjectPage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    title: '',
    query: '',
    document_type: 'report',
    description: '',
    output_format: 'html',
    generate_images: false,
  })

  const createMutation = useMutation({
    mutationFn: projectsAPI.create,
    onSuccess: (response) => {
      toast.success('Project created! Generation started.')
      navigate(`/dashboard/projects/${response.data.id}`)
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to create project')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()

    if (!formData.title.trim() || !formData.query.trim()) {
      toast.error('Please fill in all required fields')
      return
    }

    createMutation.mutate(formData)
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-100">Create New Project</h1>
        <p className="mt-2 text-gray-400">Generate a document or presentation with AI</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Project Title */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Project Details</h2>
          <div className="space-y-4">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-300 mb-1">
                Project Title *
              </label>
              <input
                id="title"
                type="text"
                required
                className="input"
                placeholder="e.g., AI in Healthcare 2024"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-1">
                Description (Optional)
              </label>
              <textarea
                id="description"
                rows="3"
                className="input"
                placeholder="Brief description of what you want to generate..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>
          </div>

          {/* Generate Images Toggle */}
          <div className="pt-4">
            <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700">
              <div>
                <h3 className="text-sm font-medium text-gray-100">Generate Images</h3>
                <p className="text-xs text-gray-400 mt-1">
                  Automatically search and insert relevant images into the document
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={formData.generate_images}
                  onChange={(e) => setFormData({ ...formData, generate_images: e.target.checked })}
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Query */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Search Query</h2>
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-300 mb-1">
              What do you want to research? *
            </label>
            <textarea
              id="query"
              rows="4"
              required
              className="input"
              placeholder="Enter your research query in detail. The more specific, the better the results. For example: 'Latest developments in artificial intelligence for healthcare diagnostics, including machine learning applications and FDA approvals'"
              value={formData.query}
              onChange={(e) => setFormData({ ...formData, query: e.target.value })}
            />
            <p className="mt-2 text-sm text-gray-500">
              Tip: Be specific and include key topics you want covered
            </p>
          </div>
        </div>

        {/* Document Type */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Document Type</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {documentTypes.map((type) => (
              <label
                key={type.value}
                className={`relative flex cursor-pointer rounded-lg border p-4 transition-all focus:outline-none ${formData.document_type === type.value
                    ? 'border-primary-500 bg-primary-600/10'
                    : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                  }`}
              >
                <input
                  type="radio"
                  name="document_type"
                  value={type.value}
                  checked={formData.document_type === type.value}
                  onChange={(e) => setFormData({ ...formData, document_type: e.target.value })}
                  className="sr-only"
                />
                <div className="flex flex-1">
                  <div className="flex flex-col">
                    <span className="block text-sm font-medium text-gray-200">{type.label}</span>
                    <span className="mt-1 flex items-center text-sm text-gray-400">
                      {type.description}
                    </span>
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Output Format */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">Output Format</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {outputFormats.map((format) => (
              <label
                key={format.value}
                className={`relative flex cursor-pointer rounded-lg border p-4 transition-all focus:outline-none ${formData.output_format === format.value
                    ? 'border-primary-500 bg-primary-600/10'
                    : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                  }`}
              >
                <input
                  type="radio"
                  name="output_format"
                  value={format.value}
                  checked={formData.output_format === format.value}
                  onChange={(e) => setFormData({ ...formData, output_format: e.target.value })}
                  className="sr-only"
                />
                <div className="flex flex-1">
                  <div className="flex flex-col">
                    <span className="block text-sm font-medium text-gray-200">{format.label}</span>
                    <span className="mt-1 flex items-center text-sm text-gray-400">
                      {format.description}
                    </span>
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => navigate('/dashboard/projects')}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="btn btn-primary"
          >
            {createMutation.isPending ? 'Creating...' : 'Create Project'}
          </button>
        </div>
      </form>
    </div>
  )
}

