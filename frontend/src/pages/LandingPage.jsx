import { Link } from 'react-router-dom'
import { 
  DocumentTextIcon, 
  PresentationChartBarIcon, 
  SparklesIcon,
  CheckCircleIcon,
  RocketLaunchIcon,
  LightBulbIcon,
  BoltIcon
} from '@heroicons/react/24/outline'
import { motion } from 'framer-motion'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <header className="fixed w-full top-0 z-50 bg-gray-900/80 backdrop-blur-md border-b border-gray-800">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <SparklesIcon className="h-5 w-5 text-primary-400" />
            <h1 className="text-xl font-bold bg-gradient-to-r from-primary-400 to-purple-400 bg-clip-text text-transparent">
              DocuGen AI
            </h1>
          </div>
          <div className="flex gap-3">
            <Link to="/sign-in" className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-gray-100 transition-colors">
              Sign In
            </Link>
            <Link to="/sign-up" className="px-5 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-500 rounded-lg shadow-lg shadow-primary-600/30 hover:shadow-primary-600/40 transition-all">
              Get Started Free
            </Link>
          </div>
        </nav>
      </header>
      
      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-600/20 rounded-full filter blur-3xl opacity-30 animate-blob"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-600/20 rounded-full filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
          <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-pink-600/20 rounded-full filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
        </div>
        
        <div className="max-w-7xl mx-auto text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-full mb-6">
              <BoltIcon className="h-4 w-4 text-primary-400" />
              <span className="text-sm font-semibold text-gray-300">Powered by Advanced AI</span>
            </div>
            <h2 className="text-5xl md:text-6xl font-bold text-gray-100 mb-6 leading-tight">
              Create Professional
              <br />
              <span className="bg-gradient-to-r from-primary-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Documents in Seconds
              </span>
            </h2>
            <p className="text-xl text-gray-400 mb-10 max-w-3xl mx-auto leading-relaxed">
              Transform your ideas into polished reports, presentations, and documents with AI-powered generation. 
              Save hours of work while maintaining professional quality.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/sign-up" 
                className="px-8 py-3.5 text-base font-semibold text-white bg-primary-600 hover:bg-primary-500 rounded-lg shadow-xl shadow-primary-600/30 hover:shadow-primary-600/40 transition-all"
              >
                Start Creating for Free
              </Link>
              <Link 
                to="/sign-in" 
                className="px-8 py-3.5 text-base font-semibold text-gray-300 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg transition-all"
              >
                Watch Demo
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
      
      {/* Features */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gray-900">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-gray-100 mb-4">Everything you need to create</h3>
            <p className="text-xl text-gray-400">Powerful features designed for modern content creators</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            <motion.div 
              className="group p-6 bg-gradient-to-br from-blue-600/10 to-blue-600/5 border border-blue-500/20 rounded-xl hover:border-blue-500/40 transition-all duration-300"
              whileHover={{ y: -4 }}
            >
              <div className="h-12 w-12 bg-blue-600/20 border border-blue-500/30 rounded-lg flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                <DocumentTextIcon className="h-6 w-6 text-blue-400" />
              </div>
              <h4 className="text-xl font-bold mb-3 text-gray-100">Smart Documents</h4>
              <p className="text-gray-400 leading-relaxed">
                Generate comprehensive reports, analyses, and research documents with AI-powered insights and perfect formatting
              </p>
            </motion.div>
            
            <motion.div 
              className="group p-6 bg-gradient-to-br from-purple-600/10 to-purple-600/5 border border-purple-500/20 rounded-xl hover:border-purple-500/40 transition-all duration-300"
              whileHover={{ y: -4 }}
            >
              <div className="h-12 w-12 bg-purple-600/20 border border-purple-500/30 rounded-lg flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                <PresentationChartBarIcon className="h-6 w-6 text-purple-400" />
              </div>
              <h4 className="text-xl font-bold mb-3 text-gray-100">Beautiful Presentations</h4>
              <p className="text-gray-400 leading-relaxed">
                Create stunning presentations with professional designs, multi-slide navigation, and interactive elements
              </p>
            </motion.div>
            
            <motion.div 
              className="group p-6 bg-gradient-to-br from-pink-600/10 to-pink-600/5 border border-pink-500/20 rounded-xl hover:border-pink-500/40 transition-all duration-300"
              whileHover={{ y: -4 }}
            >
              <div className="h-12 w-12 bg-pink-600/20 border border-pink-500/30 rounded-lg flex items-center justify-center mb-5 group-hover:scale-105 transition-transform">
                <LightBulbIcon className="h-6 w-6 text-pink-400" />
              </div>
              <h4 className="text-xl font-bold mb-3 text-gray-100">AI Research</h4>
              <p className="text-gray-400 leading-relaxed">
                Advanced AI search that finds, analyzes, and synthesizes information from multiple sources automatically
              </p>
            </motion.div>
          </div>
        </div>
      </section>
      
      {/* Pricing */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gray-950">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-gray-100 mb-4">Simple, transparent pricing</h3>
            <p className="text-xl text-gray-400">Choose the plan that fits your needs</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {/* Free Tier */}
            <motion.div 
              className="bg-gray-900 border border-gray-800 rounded-xl shadow-lg p-8 hover:border-gray-700 transition-all"
              whileHover={{ y: -4 }}
            >
              <div className="mb-6">
                <h4 className="text-2xl font-bold mb-2 text-gray-100">Starter</h4>
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-bold text-gray-100">$0</span>
                  <span className="text-gray-400">/month</span>
                </div>
              </div>
              <ul className="space-y-4 mb-8">
                <li className="flex items-start gap-3">
                  <CheckCircleIcon className="h-5 w-5 text-green-400 flex-shrink-0" />
                  <span className="text-gray-300">5 documents per month</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircleIcon className="h-5 w-5 text-green-400 flex-shrink-0" />
                  <span className="text-gray-300">Basic templates</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircleIcon className="h-5 w-5 text-green-400 flex-shrink-0" />
                  <span className="text-gray-300">Community support</span>
                </li>
              </ul>
              <Link 
                to="/sign-up" 
                className="block w-full py-3 text-center font-semibold text-gray-300 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg transition-colors"
              >
                Get Started
              </Link>
            </motion.div>
            
            {/* Pro Tier */}
            <motion.div 
              className="bg-gradient-to-br from-primary-600/20 to-primary-700/20 border-2 border-primary-500/50 rounded-xl shadow-2xl shadow-primary-500/20 p-8 relative overflow-hidden"
              whileHover={{ y: -4 }}
            >
              <div className="absolute top-0 right-0 bg-yellow-500 text-yellow-950 px-3 py-1 rounded-bl-lg text-xs font-bold">
                POPULAR
              </div>
              <div className="mb-6">
                <h4 className="text-2xl font-bold mb-2 text-gray-100">Professional</h4>
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-bold text-gray-100">$29</span>
                  <span className="text-gray-400">/month</span>
                </div>
              </div>
              <ul className="space-y-4 mb-8">
                <li className="flex items-start gap-3">
                  <CheckCircleIcon className="h-5 w-5 text-primary-400 flex-shrink-0" />
                  <span className="text-gray-200">50 documents per month</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircleIcon className="h-5 w-5 text-primary-400 flex-shrink-0" />
                  <span className="text-gray-200">Premium templates</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircleIcon className="h-5 w-5 text-primary-400 flex-shrink-0" />
                  <span className="text-gray-200">Priority support</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircleIcon className="h-5 w-5 text-primary-400 flex-shrink-0" />
                  <span className="text-gray-200">All export formats</span>
                </li>
              </ul>
              <Link 
                to="/sign-up" 
                className="block w-full py-3 text-center font-semibold text-white bg-primary-600 hover:bg-primary-500 rounded-lg shadow-lg shadow-primary-600/30 transition-colors"
              >
                Start Free Trial
              </Link>
            </motion.div>
            
            {/* Enterprise Tier */}
            <motion.div 
              className="bg-gray-900 border border-gray-800 rounded-xl shadow-lg p-8 hover:border-gray-700 transition-all"
              whileHover={{ y: -4 }}
            >
              <div className="mb-6">
                <h4 className="text-2xl font-bold mb-2 text-gray-100">Enterprise</h4>
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-bold text-gray-100">Custom</span>
                </div>
              </div>
              <ul className="space-y-4 mb-8">
                <li className="flex items-start gap-3">
                  <CheckCircleIcon className="h-5 w-5 text-green-400 flex-shrink-0" />
                  <span className="text-gray-300">Unlimited documents</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircleIcon className="h-5 w-5 text-green-400 flex-shrink-0" />
                  <span className="text-gray-300">Custom integrations</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircleIcon className="h-5 w-5 text-green-400 flex-shrink-0" />
                  <span className="text-gray-300">Dedicated support</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircleIcon className="h-5 w-5 text-green-400 flex-shrink-0" />
                  <span className="text-gray-300">SLA guarantee</span>
                </li>
              </ul>
              <a 
                href="mailto:contact@example.com" 
                className="block w-full py-3 text-center font-semibold text-gray-300 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg transition-colors"
              >
                Contact Sales
              </a>
            </motion.div>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 bg-black border-t border-gray-800">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <SparklesIcon className="h-5 w-5 text-primary-400" />
            <span className="text-lg font-bold text-gray-200">DocuGen AI</span>
          </div>
          <p className="text-gray-500 text-sm">&copy; 2025 DocuGen AI. All rights reserved.</p>
        </div>
      </footer>
      
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
