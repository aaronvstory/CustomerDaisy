import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'sonner'
import { AuthProvider, useAuth } from './lib/auth'
import { useAppStore } from './lib/store'
import { LoginForm } from './components/auth/login-form'
import { AppLayout } from './components/layout/app-layout'
import { Dashboard } from './pages/dashboard'
import { Customers } from './pages/customers'
import { CreateCustomer } from './pages/create-customer'
import { SmsMonitor } from './pages/sms-monitor'
import { AdminUsers } from './pages/admin/users'
import { AdminApiKeys } from './pages/admin/api-keys'
import { useEffect } from 'react'

function ProtectedRoute({ children, adminOnly = false }: { children: React.ReactNode, adminOnly?: boolean }) {
  const { user, userRole, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (adminOnly && userRole !== 'admin') {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

function AppContent() {
  const { user, loading } = useAuth()
  const { theme } = useAppStore()

  useEffect(() => {
    // Apply theme to document
    document.documentElement.className = theme === 'light' ? '' : theme
  }, [theme])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading CustomerDaisy...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return <LoginForm />
  }

  return (
    <Routes>
      <Route path="/login" element={<Navigate to="/dashboard" replace />} />
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        <Route path="customers" element={
          <ProtectedRoute>
            <Customers />
          </ProtectedRoute>
        } />
        <Route path="customers/new" element={
          <ProtectedRoute>
            <CreateCustomer />
          </ProtectedRoute>
        } />
        <Route path="sms-monitor" element={
          <ProtectedRoute>
            <SmsMonitor />
          </ProtectedRoute>
        } />
        <Route path="admin/users" element={
          <ProtectedRoute adminOnly>
            <AdminUsers />
          </ProtectedRoute>
        } />
        <Route path="admin/api-keys" element={
          <ProtectedRoute adminOnly>
            <AdminApiKeys />
          </ProtectedRoute>
        } />
        <Route path="export" element={
          <ProtectedRoute>
            <div className="text-center py-12">
              <h2 className="text-2xl font-bold mb-4">Export Data</h2>
              <p className="text-muted-foreground">Export functionality coming soon...</p>
            </div>
          </ProtectedRoute>
        } />
        <Route path="import" element={
          <ProtectedRoute>
            <div className="text-center py-12">
              <h2 className="text-2xl font-bold mb-4">Import Data</h2>
              <p className="text-muted-foreground">Import functionality coming soon...</p>
            </div>
          </ProtectedRoute>
        } />
        <Route path="admin/settings" element={
          <ProtectedRoute adminOnly>
            <div className="text-center py-12">
              <h2 className="text-2xl font-bold mb-4">System Settings</h2>
              <p className="text-muted-foreground">Settings panel coming soon...</p>
            </div>
          </ProtectedRoute>
        } />
        <Route path="admin/database" element={
          <ProtectedRoute adminOnly>
            <div className="text-center py-12">
              <h2 className="text-2xl font-bold mb-4">Database Management</h2>
              <p className="text-muted-foreground">Database tools coming soon...</p>
            </div>
          </ProtectedRoute>
        } />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
        <Toaster 
          position="top-right" 
          toastOptions={{
            style: {
              background: 'hsl(var(--card))',
              color: 'hsl(var(--card-foreground))',
              border: '1px solid hsl(var(--border))',
            },
          }}
        />
      </Router>
    </AuthProvider>
  )
}

export default App