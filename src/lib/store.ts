import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Theme = 'light' | 'dark' | 'grey'

interface AppState {
  theme: Theme
  setTheme: (theme: Theme) => void
  sidebarCollapsed: boolean
  setSidebarCollapsed: (collapsed: boolean) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      theme: 'light',
      setTheme: (theme) => {
        set({ theme })
        // Apply theme to document
        document.documentElement.className = theme === 'light' ? '' : theme
      },
      sidebarCollapsed: false,
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
    }),
    {
      name: 'customerdaisy-app-state',
    }
  )
)

interface Customer {
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

interface CustomerState {
  customers: Customer[]
  loading: boolean
  selectedCustomer: Customer | null
  setCustomers: (customers: Customer[]) => void
  setLoading: (loading: boolean) => void
  setSelectedCustomer: (customer: Customer | null) => void
  addCustomer: (customer: Customer) => void
  updateCustomer: (id: string, updates: Partial<Customer>) => void
  deleteCustomer: (id: string) => void
}

export const useCustomerStore = create<CustomerState>((set) => ({
  customers: [],
  loading: false,
  selectedCustomer: null,
  setCustomers: (customers) => set({ customers }),
  setLoading: (loading) => set({ loading }),
  setSelectedCustomer: (customer) => set({ selectedCustomer: customer }),
  addCustomer: (customer) => set((state) => ({ 
    customers: [...state.customers, customer] 
  })),
  updateCustomer: (id, updates) => set((state) => ({
    customers: state.customers.map(c => 
      c.id === id ? { ...c, ...updates } : c
    )
  })),
  deleteCustomer: (id) => set((state) => ({
    customers: state.customers.filter(c => c.id !== id)
  })),
}))