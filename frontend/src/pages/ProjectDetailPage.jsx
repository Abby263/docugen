import { useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsAPI, documentsAPI } from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'
import { useWebSocket } from '@/lib/websocket'
import toast from 'react-hot-toast'
import { formatDistanceToNow } from 'date-fns'
import {
  ArrowDownTrayIcon,
  EyeIcon,
  XCircleIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'

export default function ProjectDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user } = useAuthStore()

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: () => projectsAPI.get(id).then(res => res.data),
    refetchInterval: (data) => {
      // Refetch every 3 seconds if processing
      return data?.status === 'processing' ? 3000 : false
    },
  })

  // WebSocket for real-time updates
  const handleWebSocketMessage = useCallback((message) => {
    if (message.type === 'progress' && message.project_id === parseInt(id)) {
      queryClient.invalidateQueries(['project', id])
    } else if (message.type === 'completed' && message.project_id === parseInt(id)) {
      toast.success('Document generated successfully!')
      queryClient.invalidateQueries(['project', id])
    } else if (message.type === 'error' && message.project_id === parseInt(id)) {
      toast.error(`Generation failed: ${message.error}`)
      queryClient.invalidateQueries(['project', id])
    }
  }, [id, queryClient])

  useWebSocket(user?.id?.toString(), handleWebSocketMessage)

  const cancelMutation = useMutation({
    mutationFn: () => projectsAPI.cancel(id),
    onSuccess: () => {
      toast.success('Project cancelled')
      queryClient.invalidateQueries(['project', id])
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to cancel project')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => projectsAPI.delete(id),
    onSuccess: () => {
      toast.success('Project deleted')
      navigate('/dashboard/projects')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to delete project')
    },
  })

  const handleDownload = async () => {
    try {
      const response = await documentsAPI.download(id)
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${project.title}.${project.output_format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success('Download started')
    } catch (error) {
      toast.error('Failed to download document')
    }
  }

  const handlePreview = () => {
    navigate(`/dashboard/projects/${id}/preview`)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Project not found</p>
      </div>
    )
  }

  const StatusIcon = {
    pending: ClockIcon,
    processing: ClockIcon,
    completed: CheckCircleIcon,
    failed: ExclamationTriangleIcon,
    cancelled: XCircleIcon,
  }[project.status]

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">{project.title}</h1>
            {project.description && (
              <p className="mt-2 text-gray-600">{project.description}</p>
            )}
            <div className="flex items-center gap-2 mt-4">
              <StatusIcon className="h-5 w-5" />
              <span className={`px-3 py-1 text-sm font-semibold rounded-full ${project.status === 'completed' ? 'bg-green-100 text-green-800' :
                project.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                  project.status === 'failed' ? 'bg-red-100 text-red-800' :
                    project.status === 'cancelled' ? 'bg-gray-100 text-gray-800' :
                      'bg-yellow-100 text-yellow-800'
                }`}>
                {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
              </span>
            </div>
          </div>

          <div className="flex gap-2">
            {project.status === 'completed' && (
              <>
                <button onClick={handlePreview} className="btn btn-secondary flex items-center gap-2">
                  <EyeIcon className="h-5 w-5" />
                  Preview
                </button>
                <button onClick={handleDownload} className="btn btn-primary flex items-center gap-2">
                  <ArrowDownTrayIcon className="h-5 w-5" />
                  Download
                </button>
              </>
            )}
            {(project.status === 'pending' || project.status === 'processing') && (
              <button
                onClick={() => cancelMutation.mutate()}
                disabled={cancelMutation.isPending}
                className="btn btn-danger"
              >
                Cancel
              </button>
            )}
            {(project.status === 'failed' || project.status === 'cancelled' || project.status === 'completed') && (
              <button
                onClick={() => {
                  if (confirm('Are you sure you want to delete this project?')) {
                    deleteMutation.mutate()
                  }
                }}
                disabled={deleteMutation.isPending}
                className="btn btn-danger"
              >
                Delete
              </button>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        {project.status === 'processing' && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Progress</span>
              <span className="text-sm font-medium text-gray-700">{project.progress}%</span>
            </div>
            <div className="bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                style={{ width: `${project.progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Error Message */}
        {project.status === 'failed' && project.error_message && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{project.error_message}</p>
          </div>
        )}
      </div>

      {/* Details */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Project Information</h2>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Document Type</dt>
              <dd className="mt-1 text-sm text-gray-900 capitalize">{project.document_type}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Output Format</dt>
              <dd className="mt-1 text-sm text-gray-900 uppercase">{project.output_format}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Created</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {formatDistanceToNow(new Date(project.created_at), { addSuffix: true })}
              </dd>
            </div>
            {project.completed_at && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Completed</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {formatDistanceToNow(new Date(project.completed_at), { addSuffix: true })}
                </dd>
              </div>
            )}
          </dl>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Statistics</h2>
          <dl className="space-y-3">
            {project.search_results_count > 0 && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Search Results</dt>
                <dd className="mt-1 text-sm text-gray-900">{project.search_results_count}</dd>
              </div>
            )}
            {project.processing_time && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Processing Time</dt>
                <dd className="mt-1 text-sm text-gray-900">{project.processing_time.toFixed(2)}s</dd>
              </div>
            )}
            {project.output_size && (
              <div>
                <dt className="text-sm font-medium text-gray-500">File Size</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {(project.output_size / 1024).toFixed(2)} KB
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>

      {/* Query */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Research Query</h2>
        <p className="text-gray-700 whitespace-pre-wrap">{project.query}</p>
      </div>
    </div>
  )
}

