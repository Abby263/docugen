import { Outlet, Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import {
  HomeIcon,
  DocumentTextIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  PlusIcon,
  Bars3Icon,
  XMarkIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import { UserButton, useUser } from '@clerk/clerk-react'
import clsx from 'clsx'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Projects', href: '/dashboard/projects', icon: DocumentTextIcon },
  { name: 'Analytics', href: '/dashboard/analytics', icon: ChartBarIcon },
  { name: 'Settings', href: '/dashboard/settings', icon: Cog6ToothIcon },
]

export default function DashboardLayout() {
  const location = useLocation()
  const { user } = useUser()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  
  return (
    <div className="min-h-screen bg-gray-950">
      {/* Mobile sidebar */}
      <div className={clsx(
        'fixed inset-0 z-50 lg:hidden',
        sidebarOpen ? 'block' : 'hidden'
      )}>
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-gray-900 shadow-2xl border-r border-gray-800">
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-800">
            <div className="flex items-center gap-2">
              <SparklesIcon className="h-5 w-5 text-primary-400" />
              <h1 className="text-lg font-bold text-gray-100">DocuGen AI</h1>
            </div>
            <button onClick={() => setSidebarOpen(false)} className="text-gray-400 hover:text-gray-200">
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
          <nav className="flex-1 px-3 py-6 space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={clsx(
                  'flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all',
                  location.pathname === item.href
                    ? 'bg-primary-600/10 text-primary-400 border border-primary-500/20'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                )}
              >
                <item.icon className="h-4 w-4 mr-3" />
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>
      
      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-1 min-h-0 bg-gray-900 border-r border-gray-800">
          <div className="flex items-center gap-2 h-16 px-6 border-b border-gray-800">
            <SparklesIcon className="h-5 w-5 text-primary-400" />
            <h1 className="text-xl font-bold text-gray-100">DocuGen AI</h1>
          </div>
          <nav className="flex-1 px-3 py-6 space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={clsx(
                  'flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all',
                  location.pathname === item.href
                    ? 'bg-primary-600/10 text-primary-400 border border-primary-500/20'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                )}
              >
                <item.icon className="h-4 w-4 mr-3" />
                {item.name}
              </Link>
            ))}
          </nav>
          <div className="p-4 border-t border-gray-800">
            <div className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg border border-gray-700/50">
              <UserButton 
                appearance={{
                  elements: {
                    avatarBox: "h-9 w-9",
                    userButtonPopoverCard: "bg-gray-900 border border-gray-800",
                    userButtonPopoverActionButton: "text-gray-200 hover:bg-gray-800",
                  }
                }}
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-200 truncate">
                  {user?.firstName || user?.username || 'User'}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {user?.primaryEmailAddress?.emailAddress || ''}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-40 flex h-16 items-center gap-x-4 border-b border-gray-800 bg-gray-900/80 backdrop-blur-md px-4 sm:px-6 lg:px-8">
          <button
            className="lg:hidden p-2 rounded-lg hover:bg-gray-800 text-gray-400"
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className="h-5 w-5" />
          </button>
          
          <div className="flex flex-1 gap-x-4 justify-end">
            <Link
              to="/dashboard/projects/new"
              className="flex items-center gap-2 px-5 py-2 text-sm font-semibold text-white bg-primary-600 hover:bg-primary-500 rounded-lg shadow-lg shadow-primary-600/20 hover:shadow-primary-600/30 transition-all"
            >
              <PlusIcon className="h-4 w-4" />
              New Project
            </Link>
          </div>
        </div>
        
        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
