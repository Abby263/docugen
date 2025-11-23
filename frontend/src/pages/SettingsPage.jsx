import { useAuthStore } from '@/stores/authStore'
import { CheckCircleIcon } from '@heroicons/react/24/outline'

export default function SettingsPage() {
  const { user } = useAuthStore()
  
  const subscriptionTiers = [
    {
      name: 'Free',
      price: '$0',
      period: '/mo',
      features: [
        '5 documents per month',
        'Basic templates',
        'Community support',
        'HTML & Markdown export',
      ],
      current: user?.subscription_tier === 'free',
    },
    {
      name: 'Pro',
      price: '$29',
      period: '/mo',
      features: [
        '50 documents per month',
        'Advanced templates',
        'Priority support',
        'All export formats',
        'API access',
        'Custom branding',
      ],
      current: user?.subscription_tier === 'pro',
      popular: true,
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      features: [
        'Unlimited documents',
        'Custom integrations',
        'Dedicated support',
        'SLA guarantee',
        'Advanced analytics',
        'Team collaboration',
      ],
      current: user?.subscription_tier === 'enterprise',
    },
  ]
  
  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-100">Settings</h1>
        <p className="mt-2 text-gray-400">Manage your account and subscription</p>
      </div>
      
      {/* Profile Section */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-100 mb-6">Profile Information</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Username</label>
            <p className="text-gray-200">{user?.username}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Email</label>
            <p className="text-gray-200">{user?.email}</p>
          </div>
          {user?.full_name && (
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Full Name</label>
              <p className="text-gray-200">{user.full_name}</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Subscription Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-100 mb-6">Subscription Plans</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {subscriptionTiers.map((tier) => (
            <div
              key={tier.name}
              className={`card relative ${
                tier.popular ? 'border-2 border-primary-500 shadow-lg shadow-primary-500/20' : ''
              }`}
            >
              {tier.popular && (
                <div className="absolute top-0 right-0 bg-primary-500 text-white px-3 py-1 text-xs font-semibold rounded-bl-lg">
                  Popular
                </div>
              )}
              {tier.current && (
                <div className="absolute top-0 left-0 bg-green-500 text-white px-3 py-1 text-xs font-semibold rounded-tr-lg">
                  Current Plan
                </div>
              )}
              <div className="mt-4">
                <h3 className="text-xl font-bold text-gray-100">{tier.name}</h3>
                <div className="mt-4 flex items-baseline">
                  <span className="text-4xl font-bold text-gray-100">{tier.price}</span>
                  <span className="text-gray-400 ml-1">{tier.period}</span>
                </div>
                <ul className="mt-6 space-y-3">
                  {tier.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <CheckCircleIcon className="h-4 w-4 text-green-400 mr-2 flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>
                <button
                  disabled={tier.current}
                  className={`w-full mt-6 btn ${
                    tier.current
                      ? 'btn-secondary opacity-50 cursor-not-allowed'
                      : tier.popular
                      ? 'btn-primary'
                      : 'btn-secondary'
                  }`}
                >
                  {tier.current ? 'Current Plan' : tier.name === 'Enterprise' ? 'Contact Sales' : 'Upgrade'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* API Keys (Pro/Enterprise only) */}
      {(user?.subscription_tier === 'pro' || user?.subscription_tier === 'enterprise') && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-100 mb-4">API Access</h2>
          <p className="text-gray-400 mb-4">
            API access allows you to integrate DocuGen AI with your applications.
          </p>
          <button className="btn btn-primary">Generate API Key</button>
        </div>
      )}
      
      {/* Danger Zone */}
      <div className="card border-red-500/30">
        <h2 className="text-xl font-semibold text-red-400 mb-4">Danger Zone</h2>
        <p className="text-gray-400 mb-4">
          Permanently delete your account and all associated data.
        </p>
        <button className="btn btn-danger">Delete Account</button>
      </div>
    </div>
  )
}

