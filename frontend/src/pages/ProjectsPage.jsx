import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { projectsAPI } from '@/lib/api'
import { Link } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import { DocumentTextIcon, FunnelIcon } from '@heroicons/react/24/outline'

export default function ProjectsPage() {
  const [statusFilter, setStatusFilter] = useState('')
  
  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects', statusFilter],
    queryFn: () => projectsAPI.list({ status: statusFilter || undefined }).then(res => res.data),
  })
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-100">Projects</h1>
          <p className="mt-2 text-gray-400">Manage all your document generation projects</p>
        </div>
        <Link to="/dashboard/projects/new" className="btn btn-primary">
          New Project
        </Link>
      </div>
      
      {/* Filters */}
      <div className="card">
        <div className="flex items-center gap-4">
          <FunnelIcon className="h-4 w-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input max-w-xs"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>
      
      {/* Projects List */}
      {projects && projects.length > 0 ? (
        <div className="grid gap-4">
          {projects.map((project) => (
            <Link
              key={project.id}
              to={`/dashboard/projects/${project.id}`}
              className="card hover:border-primary-500/50 hover:bg-gray-800/50 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-start gap-4">
                    <DocumentTextIcon className="h-6 w-6 text-primary-400 flex-shrink-0 mt-1" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-200">{project.title}</h3>
                      {project.description && (
                        <p className="text-sm text-gray-400 mt-1">{project.description}</p>
                      )}
                      <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                        <span className="capitalize">{project.document_type}</span>
                        <span>•</span>
                        <span>Created {formatDistanceToNow(new Date(project.created_at), { addSuffix: true })}</span>
                        {project.completed_at && (
                          <>
                            <span>•</span>
                            <span>Completed {formatDistanceToNow(new Date(project.completed_at), { addSuffix: true })}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="ml-4 flex flex-col items-end gap-2">
                  <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                    project.status === 'completed' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                    project.status === 'processing' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                    project.status === 'failed' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                    project.status === 'cancelled' ? 'bg-gray-500/20 text-gray-400 border border-gray-500/30' :
                    'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                  }`}>
                    {project.status}
                  </span>
                  {project.status === 'processing' && (
                    <div className="text-xs text-gray-400">
                      {project.progress}%
                    </div>
                  )}
                </div>
              </div>
              {project.status === 'processing' && (
                <div className="mt-4 bg-gray-800 rounded-full h-2">
                  <div 
                    className="bg-primary-500 h-2 rounded-full transition-all"
                    style={{ width: `${project.progress}%` }}
                  />
                </div>
              )}
            </Link>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <DocumentTextIcon className="h-12 w-12 text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-200 mb-2">No projects found</h3>
          <p className="text-gray-400 mb-6">
            {statusFilter ? 'Try changing the filter' : 'Get started by creating your first project'}
          </p>
          <Link to="/dashboard/projects/new" className="btn btn-primary">
            Create Project
          </Link>
        </div>
      )}
    </div>
  )
}

