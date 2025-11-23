import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { ClerkProvider } from '@clerk/clerk-react'
import App from './App'
import './index.css'

// Import Clerk publishable key
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
  throw new Error("Missing Clerk Publishable Key. Please add VITE_CLERK_PUBLISHABLE_KEY to your .env file")
}

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ClerkProvider 
      publishableKey={PUBLISHABLE_KEY}
      appearance={{
        layout: {
          socialButtonsVariant: 'iconButton',
          socialButtonsPlacement: 'bottom',
        },
        variables: {
          colorPrimary: '#0284c7',
          colorBackground: '#111827',
          colorInputBackground: '#1f2937',
          colorInputText: '#f3f4f6',
          colorText: '#f3f4f6',
          colorTextSecondary: '#9ca3af',
          colorDanger: '#ef4444',
          colorSuccess: '#10b981',
          colorWarning: '#f59e0b',
          colorNeutral: '#6b7280',
          borderRadius: '0.5rem',
        },
        elements: {
          formButtonPrimary: 'bg-primary-600 hover:bg-primary-500',
          card: 'bg-gray-900 border-gray-800',
          headerTitle: 'text-gray-100',
          headerSubtitle: 'text-gray-400',
          socialButtonsBlockButton: 'border-gray-700 hover:bg-gray-800',
          formFieldLabel: 'text-gray-300',
          formFieldInput: 'bg-gray-800 border-gray-700 text-gray-100',
          footerActionLink: 'text-primary-400 hover:text-primary-300',
        },
      }}
    >
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
                background: '#1f2937',
                color: '#f3f4f6',
                border: '1px solid #374151',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 4000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </BrowserRouter>
    </QueryClientProvider>
    </ClerkProvider>
  </React.StrictMode>,
)

