import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { authAPI } from '@/lib/api'
import toast from 'react-hot-toast'
import { SparklesIcon, CheckCircleIcon } from '@heroicons/react/24/outline'
import { motion } from 'framer-motion'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
  })
  
  const registerMutation = useMutation({
    mutationFn: authAPI.register,
    onSuccess: () => {
      toast.success('Registration successful! Please sign in.')
      navigate('/login')
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Registration failed')
    },
  })
  
  const handleSubmit = (e) => {
    e.preventDefault()
    registerMutation.mutate(formData)
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-600/20 rounded-full filter blur-3xl opacity-30 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-600/20 rounded-full filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-pink-600/20 rounded-full filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
      </div>
      
      <div className="max-w-6xl w-full relative z-10 grid lg:grid-cols-2 gap-8 items-center">
        {/* Benefits Section */}
        <motion.div 
          className="hidden lg:block"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-10 shadow-xl">
            <div className="flex items-center gap-2 mb-6">
              <SparklesIcon className="h-7 w-7 text-primary-400" />
              <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-400 to-purple-400 bg-clip-text text-transparent">
                DocuGen AI
              </h1>
            </div>
            <h2 className="text-2xl font-bold text-gray-100 mb-4">
              Start creating amazing documents today
            </h2>
            <p className="text-gray-400 mb-8">
              Join thousands of users who trust us to generate professional documents, presentations, and reports.
            </p>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircleIcon className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-gray-200">AI-Powered Generation</h3>
                  <p className="text-sm text-gray-400">Create professional documents in seconds</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircleIcon className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-gray-200">Multiple Formats</h3>
                  <p className="text-sm text-gray-400">Export to HTML, Markdown, PDF, and more</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircleIcon className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-gray-200">Free to Start</h3>
                  <p className="text-sm text-gray-400">5 documents per month, no credit card required</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
        
        {/* Registration Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="bg-gray-900 border border-gray-800 rounded-xl shadow-2xl p-8">
            <div className="text-center mb-8 lg:hidden">
              <div className="flex items-center justify-center gap-2 mb-4">
                <SparklesIcon className="h-7 w-7 text-primary-400" />
                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-400 to-purple-400 bg-clip-text text-transparent">
                  DocuGen AI
                </h1>
              </div>
            </div>
            
            <h2 className="text-2xl font-bold text-gray-100 mb-2">Create your account</h2>
            <p className="text-sm text-gray-400 mb-6">
              Already have an account?{' '}
              <Link to="/login" className="font-semibold text-primary-400 hover:text-primary-300 transition-colors">
                Sign in
              </Link>
            </p>
            
            {/* Social Sign Up Buttons */}
            <div className="space-y-3 mb-6">
              <button
                type="button"
                onClick={() => toast('Google OAuth coming soon!', { icon: 'ℹ️' })}
                className="w-full flex items-center justify-center gap-3 px-4 py-2.5 bg-white hover:bg-gray-100 text-gray-900 rounded-lg font-medium transition-all border border-gray-300"
              >
                <svg className="h-5 w-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Sign up with Google
              </button>
              
              <button
                type="button"
                onClick={() => toast('GitHub OAuth coming soon!', { icon: '🔧' })}
                className="w-full flex items-center justify-center gap-3 px-4 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-100 rounded-lg font-medium transition-all border border-gray-700"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd"/>
                </svg>
                Sign up with GitHub
              </button>
              
              <button
                type="button"
                onClick(() => toast('Microsoft OAuth coming soon!', { icon: '🔧' })}
                className="w-full flex items-center justify-center gap-3 px-4 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-100 rounded-lg font-medium transition-all border border-gray-700"
              >
                <svg className="h-5 w-5" viewBox="0 0 23 23">
                  <path fill="#f3f3f3" d="M0 0h23v23H0z"/>
                  <path fill="#f35325" d="M1 1h10v10H1z"/>
                  <path fill="#81bc06" d="M12 1h10v10H12z"/>
                  <path fill="#05a6f0" d="M1 12h10v10H1z"/>
                  <path fill="#ffba08" d="M12 12h10v10H12z"/>
                </svg>
                Sign up with Microsoft
              </button>
            </div>
            
            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-700"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-900 text-gray-400">Or sign up with email</span>
              </div>
            </div>
            
            <form className="space-y-4" onSubmit={handleSubmit}>
              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-gray-300 mb-2">
                  Email address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>
              
              <div>
                <label htmlFor="username" className="block text-sm font-semibold text-gray-300 mb-2">
                  Username
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
                  placeholder="johndoe"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                />
              </div>
              
              <div>
                <label htmlFor="full_name" className="block text-sm font-semibold text-gray-300 mb-2">
                  Full name
                </label>
                <input
                  id="full_name"
                  name="full_name"
                  type="text"
                  className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
                  placeholder="John Doe"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                />
              </div>
              
              <div>
                <label htmlFor="password" className="block text-sm font-semibold text-gray-300 mb-2">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  minLength="6"
                  className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
                  placeholder="Minimum 6 characters"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
              </div>
              
              <button
                type="submit"
                disabled={registerMutation.isPending}
                className="w-full py-3 px-4 text-white bg-primary-600 hover:bg-primary-500 rounded-lg font-semibold shadow-lg shadow-primary-600/30 hover:shadow-primary-600/40 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {registerMutation.isPending ? 'Creating account...' : 'Create account'}
              </button>
            </form>
            
            <div className="mt-6 text-center">
              <Link to="/" className="text-sm text-gray-400 hover:text-gray-200 transition-colors">
                ← Back to home
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
      
      <style>{`
        @keyframes blob {
          0% { transform: translate(0px, 0px) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
          100% { transform: translate(0px, 0px) scale(1); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  )
}
