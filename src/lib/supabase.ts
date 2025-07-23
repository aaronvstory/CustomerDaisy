import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type Database = {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          username: string
          password_hash: string
          role: 'admin' | 'user'
          created_at: string
          theme_preference: 'light' | 'dark' | 'grey'
        }
        Insert: {
          id?: string
          username: string
          password_hash: string
          role?: 'admin' | 'user'
          created_at?: string
          theme_preference?: 'light' | 'dark' | 'grey'
        }
        Update: {
          id?: string
          username?: string
          password_hash?: string
          role?: 'admin' | 'user'
          created_at?: string
          theme_preference?: 'light' | 'dark' | 'grey'
        }
      }
      customers: {
        Row: {
          id: string
          user_id: string
          first_name: string
          last_name: string
          phone: string | null
          email: string
          address: string | null
          city: string | null
          state: string | null
          zip: string | null
          verification_status: 'pending' | 'verified' | 'failed'
          sms_code: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          first_name: string
          last_name: string
          phone?: string | null
          email: string
          address?: string | null
          city?: string | null
          state?: string | null
          zip?: string | null
          verification_status?: 'pending' | 'verified' | 'failed'
          sms_code?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          first_name?: string
          last_name?: string
          phone?: string | null
          email?: string
          address?: string | null
          city?: string | null
          state?: string | null
          zip?: string | null
          verification_status?: 'pending' | 'verified' | 'failed'
          sms_code?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      api_keys: {
        Row: {
          id: string
          service_name: 'daisysms' | 'mailtm' | 'mapquest'
          key_value: string
          created_by_admin: string
          created_at: string
        }
        Insert: {
          id?: string
          service_name: 'daisysms' | 'mailtm' | 'mapquest'
          key_value: string
          created_by_admin: string
          created_at?: string
        }
        Update: {
          id?: string
          service_name?: 'daisysms' | 'mailtm' | 'mapquest'
          key_value?: string
          created_by_admin?: string
          created_at?: string
        }
      }
      user_api_assignments: {
        Row: {
          id: string
          user_id: string
          api_key_id: string
          assigned_at: string
          assigned_by_admin: string
        }
        Insert: {
          id?: string
          user_id: string
          api_key_id: string
          assigned_at?: string
          assigned_by_admin: string
        }
        Update: {
          id?: string
          user_id?: string
          api_key_id?: string
          assigned_at?: string
          assigned_by_admin?: string
        }
      }
    }
  }
}