import { useQuery } from '@tanstack/react-query'
import { analyticsAPI } from '@/lib/api'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export default function AnalyticsPage() {
  const { data: dashboardStats, isLoading: dashboardLoading } = useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: () => analyticsAPI.dashboard().then(res => res.data),
  })
  
  const { data: usageStats, isLoading: usageLoading } = useQuery({
    queryKey: ['analytics-usage'],
    queryFn: () => analyticsAPI.usage().then(res => res.data),
  })
  
  if (dashboardLoading || usageLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    )
  }
  
  // Prepare data for charts
  const projectsByStatusData = Object.entries(dashboardStats?.projects_by_status || {}).map(
    ([name, value]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), value })
  )
  
  const projectsByTypeData = Object.entries(dashboardStats?.projects_by_type || {}).map(
    ([name, value]) => ({ name: name.charAt(0).toUpperCase() + name.slice(1), value })
  )
  
  const recentActivityData = Object.entries(dashboardStats?.recent_activity || {}).map(
    ([date, count]) => ({ date, count })
  )
  
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-100">Analytics</h1>
        <p className="mt-2 text-gray-400">Insights into your document generation activity</p>
      </div>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <p className="text-sm font-medium text-gray-400">Total Documents</p>
          <p className="text-3xl font-bold text-gray-100 mt-2">
            {dashboardStats?.summary?.total_projects || 0}
          </p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-400">Completed</p>
          <p className="text-3xl font-bold text-green-400 mt-2">
            {dashboardStats?.summary?.completed_projects || 0}
          </p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-400">Search Results</p>
          <p className="text-3xl font-bold text-blue-400 mt-2">
            {usageStats?.total_search_results || 0}
          </p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-400">Total Time</p>
          <p className="text-3xl font-bold text-purple-400 mt-2">
            {usageStats?.total_processing_time?.toFixed(0) || 0}s
          </p>
        </div>
      </div>
      
      {/* Recent Activity Chart */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-100 mb-6">Recent Activity (Last 7 Days)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={recentActivityData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="date" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#f3f4f6' }} />
            <Legend wrapperStyle={{ color: '#9ca3af' }} />
            <Line type="monotone" dataKey="count" stroke="#0ea5e9" strokeWidth={2} name="Projects Created" />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      <div className="grid md:grid-cols-2 gap-6">
        {/* Projects by Status */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-100 mb-6">Projects by Status</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={projectsByStatusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {projectsByStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#f3f4f6' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        
        {/* Projects by Type */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-100 mb-6">Projects by Type</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={projectsByTypeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#f3f4f6' }} />
              <Bar dataKey="value" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Monthly Usage Trend */}
      {usageStats?.usage_by_month && usageStats.usage_by_month.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-100 mb-6">Monthly Usage Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={usageStats.usage_by_month}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="month" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', color: '#f3f4f6' }} />
              <Legend wrapperStyle={{ color: '#9ca3af' }} />
              <Bar dataKey="count" fill="#10b981" name="Documents Created" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

