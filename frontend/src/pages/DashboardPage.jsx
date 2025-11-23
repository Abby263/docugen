import { useQuery } from '@tanstack/react-query'
import { analyticsAPI, projectsAPI } from '@/lib/api'
import { Link } from 'react-router-dom'
import { 
  DocumentTextIcon, 
  ClockIcon, 
  CheckCircleIcon,
  ArrowTrendingUpIcon,
  SparklesIcon 
} from '@heroicons/react/24/outline'
import { formatDistanceToNow } from 'date-fns'
import { motion } from 'framer-motion'

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => analyticsAPI.dashboard().then(res => res.data),
  })
  
  const { data: recentProjects, isLoading: projectsLoading } = useQuery({
    queryKey: ['recent-projects'],
    queryFn: () => projectsAPI.list({ limit: 5 }).then(res => res.data),
  })
  
  if (statsLoading || projectsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="relative">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
          <SparklesIcon className="h-5 w-5 text-primary-500 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
        </div>
      </div>
    )
  }
  
  const summary = stats?.summary || {}
  const subscription = stats?.subscription || {}
  
  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-100 to-gray-300 bg-clip-text text-transparent">
          Welcome back!
        </h1>
        <p className="mt-2 text-lg text-gray-400">Here's what's happening with your projects today.</p>
      </motion.div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div 
          className="bg-gradient-to-br from-blue-600/20 to-blue-600/10 border border-blue-500/20 rounded-xl p-6 shadow-lg shadow-blue-500/10 hover:shadow-blue-500/20 transition-all"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          whileHover={{ y: -2 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">Total Projects</p>
              <p className="text-3xl font-bold mt-2 text-gray-100">{summary.total_projects || 0}</p>
            </div>
            <DocumentTextIcon className="h-8 w-8 text-blue-400 opacity-70" />
          </div>
        </motion.div>
        
        <motion.div 
          className="bg-gradient-to-br from-green-600/20 to-green-600/10 border border-green-500/20 rounded-xl p-6 shadow-lg shadow-green-500/10 hover:shadow-green-500/20 transition-all"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          whileHover={{ y: -2 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">Completed</p>
              <p className="text-3xl font-bold mt-2 text-gray-100">{summary.completed_projects || 0}</p>
            </div>
            <CheckCircleIcon className="h-8 w-8 text-green-400 opacity-70" />
          </div>
        </motion.div>
        
        <motion.div 
          className="bg-gradient-to-br from-purple-600/20 to-purple-600/10 border border-purple-500/20 rounded-xl p-6 shadow-lg shadow-purple-500/10 hover:shadow-purple-500/20 transition-all"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          whileHover={{ y: -2 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">This Month</p>
              <p className="text-3xl font-bold mt-2 text-gray-100">{summary.projects_this_month || 0}</p>
            </div>
            <ArrowTrendingUpIcon className="h-8 w-8 text-purple-400 opacity-70" />
          </div>
        </motion.div>
        
        <motion.div 
          className="bg-gradient-to-br from-orange-600/20 to-orange-600/10 border border-orange-500/20 rounded-xl p-6 shadow-lg shadow-orange-500/10 hover:shadow-orange-500/20 transition-all"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          whileHover={{ y: -2 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">Avg. Time</p>
              <p className="text-3xl font-bold mt-2 text-gray-100">{summary.avg_processing_time || 0}s</p>
            </div>
            <ClockIcon className="h-8 w-8 text-orange-400 opacity-70" />
          </div>
        </motion.div>
      </div>
      
      {/* Subscription Info */}
      <motion.div 
        className="bg-gradient-to-r from-primary-600/20 via-purple-600/20 to-pink-600/20 border border-primary-500/30 rounded-xl p-8 shadow-xl"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <SparklesIcon className="h-5 w-5 text-primary-400" />
              <h3 className="text-2xl font-bold text-gray-100">
                {subscription.tier?.charAt(0).toUpperCase() + subscription.tier?.slice(1)} Plan
              </h3>
            </div>
            <p className="text-lg text-gray-300 mb-4">
              {subscription.documents_used || 0} / {subscription.monthly_limit === 999999 ? '∞' : subscription.monthly_limit} documents used this month
            </p>
            <div className="bg-gray-800 rounded-full h-2.5 overflow-hidden">
              <motion.div 
                className="bg-gradient-to-r from-primary-500 to-purple-500 h-2.5 rounded-full"
                initial={{ width: 0 }}
                animate={{ 
                  width: `${Math.min(100, (subscription.documents_used / subscription.monthly_limit) * 100)}%` 
                }}
                transition={{ delay: 0.7, duration: 1 }}
              />
            </div>
          </div>
          {subscription.tier === 'free' && (
            <Link 
              to="/dashboard/settings" 
              className="px-8 py-3 bg-primary-600 hover:bg-primary-500 text-white font-semibold rounded-lg shadow-lg shadow-primary-600/30 hover:shadow-primary-600/40 transition-all text-center"
            >
              Upgrade to Pro
            </Link>
          )}
        </div>
      </motion.div>
      
      {/* Recent Projects */}
      <motion.div 
        className="bg-gray-900 border border-gray-800 rounded-xl shadow-lg p-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-100">Recent Projects</h2>
          <Link to="/dashboard/projects" className="text-primary-400 hover:text-primary-300 font-semibold flex items-center gap-1 group text-sm">
            View all 
            <span className="transform group-hover:translate-x-1 transition-transform">→</span>
          </Link>
        </div>
        
        {recentProjects && recentProjects.length > 0 ? (
          <div className="space-y-3">
            {recentProjects.map((project, idx) => (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 + idx * 0.1 }}
              >
                <Link
                  to={`/dashboard/projects/${project.id}`}
                  className="block p-4 border border-gray-800 bg-gray-900/50 rounded-lg hover:border-primary-500/50 hover:bg-gray-800/50 transition-all group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-base text-gray-200 group-hover:text-primary-400 transition-colors">
                        {project.title}
                      </h3>
                      <p className="text-sm text-gray-500 mt-1 capitalize">{project.document_type}</p>
                      <p className="text-xs text-gray-600 mt-2 flex items-center gap-1">
                        <ClockIcon className="h-3 w-3" />
                        Created {formatDistanceToNow(new Date(project.created_at), { addSuffix: true })}
                      </p>
                    </div>
                    <div className="ml-4">
                      <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                        project.status === 'completed' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                        project.status === 'processing' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                        project.status === 'failed' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                        'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                      }`}>
                        {project.status}
                      </span>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center h-14 w-14 bg-gray-800 border border-gray-700 rounded-full mb-4">
              <DocumentTextIcon className="h-6 w-6 text-gray-500" />
            </div>
            <p className="text-gray-300 text-lg mb-2">No projects yet</p>
            <p className="text-gray-500 text-sm mb-6">Get started by creating your first project</p>
            <Link 
              to="/dashboard/projects/new" 
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-500 text-white font-semibold rounded-lg shadow-lg shadow-primary-600/30 transition-all"
            >
              <SparklesIcon className="h-4 w-4" />
              Create Your First Project
            </Link>
          </div>
        )}
      </motion.div>
    </div>
  )
}
