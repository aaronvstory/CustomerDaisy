import { createContext, useContext, useEffect, useState } from 'react'
import { User } from '@supabase/supabase-js'
import { supabase } from './supabase'
import { toast } from 'sonner'

interface AuthContextType {
  user: User | null
  userRole: 'admin' | 'user' | null
  loading: boolean
  signIn: (username: string, password: string) => Promise<boolean>
  signUp: (username: string, password: string, role?: 'admin' | 'user') => Promise<boolean>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [userRole, setUserRole] = useState<'admin' | 'user' | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null)
      if (session?.user) {
        fetchUserRole(session.user.id)
      }
      setLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        setUser(session?.user ?? null)
        if (session?.user) {
          await fetchUserRole(session.user.id)
        } else {
          setUserRole(null)
        }
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  const fetchUserRole = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('users')
        .select('role')
        .eq('id', userId)
        .single()

      if (error) throw error
      setUserRole(data.role)
    } catch (error) {
      console.error('Error fetching user role:', error)
      setUserRole('user') // Default to user role
    }
  }

  const signIn = async (username: string, password: string): Promise<boolean> => {
    try {
      // First, get the user by username to get their email
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('id')
        .eq('username', username)
        .single()

      if (userError || !userData) {
        toast.error('Invalid username or password')
        return false
      }

      // Use the user ID as email for Supabase auth (workaround)
      const email = `${userData.id}@customerdaisy.app`
      
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) {
        toast.error('Invalid username or password')
        return false
      }

      toast.success('Signed in successfully')
      return true
    } catch (error) {
      toast.error('Sign in failed')
      return false
    }
  }

  const signUp = async (username: string, password: string, role: 'admin' | 'user' = 'user'): Promise<boolean> => {
    try {
      // Check if username already exists
      const { data: existingUser } = await supabase
        .from('users')
        .select('id')
        .eq('username', username)
        .single()

      if (existingUser) {
        toast.error('Username already exists')
        return false
      }

      // Create user in our users table first
      const { data: newUser, error: userError } = await supabase
        .from('users')
        .insert({
          username,
          password_hash: password, // In production, this should be hashed
          role,
        })
        .select()
        .single()

      if (userError) throw userError

      // Create auth user with user ID as email
      const email = `${newUser.id}@customerdaisy.app`
      const { error: authError } = await supabase.auth.signUp({
        email,
        password,
      })

      if (authError) {
        // Clean up user record if auth fails
        await supabase.from('users').delete().eq('id', newUser.id)
        throw authError
      }

      toast.success('Account created successfully')
      return true
    } catch (error) {
      toast.error('Sign up failed')
      return false
    }
  }

  const signOut = async () => {
    try {
      const { error } = await supabase.auth.signOut()
      if (error) throw error
      toast.success('Signed out successfully')
    } catch (error) {
      toast.error('Sign out failed')
    }
  }

  return (
    <AuthContext.Provider value={{
      user,
      userRole,
      loading,
      signIn,
      signUp,
      signOut,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}