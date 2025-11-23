import { useEffect } from 'react'
import { useAuth } from '@clerk/clerk-react'
import { setClerkToken } from '@/lib/api'

export default function ClerkTokenProvider({ children }) {
  const { getToken, isLoaded } = useAuth()
  
  useEffect(() => {
    const updateToken = async () => {
      if (isLoaded) {
        try {
          const token = await getToken()
          setClerkToken(token)
        } catch (error) {
          console.error('Failed to get Clerk token:', error)
          setClerkToken(null)
        }
      }
    }
    
    updateToken()
    
    // Update token every 50 minutes (tokens expire after 60 minutes)
    const interval = setInterval(updateToken, 50 * 60 * 1000)
    
    return () => clearInterval(interval)
  }, [getToken, isLoaded])
  
  return children
}

