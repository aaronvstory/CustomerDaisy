import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/lib/auth'
import { useAppStore } from '@/lib/store'
import {
  Users,
  UserPlus,
  BarChart3,
  Settings,
  Key,
  ChevronLeft,
  ChevronRight,
  Flower2,
  Shield,
  Database,
  Download,
  Upload,
  Activity,
} from 'lucide-react'

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: BarChart3,
    roles: ['admin', 'user'],
  },
  {
    name: 'Customers',
    href: '/customers',
    icon: Users,
    roles: ['admin', 'user'],
  },
  {
    name: 'Create Customer',
    href: '/customers/new',
    icon: UserPlus,
    roles: ['admin', 'user'],
  },
  {
    name: 'SMS Monitor',
    href: '/sms-monitor',
    icon: Activity,
    roles: ['admin', 'user'],
  },
  {
    name: 'Export Data',
    href: '/export',
    icon: Download,
    roles: ['admin', 'user'],
  },
  {
    name: 'Import Data',
    href: '/import',
    icon: Upload,
    roles: ['admin', 'user'],
  },
]

const adminNavigation = [
  {
    name: 'User Management',
    href: '/admin/users',
    icon: Shield,
    badge: 'Admin',
  },
  {
    name: 'API Keys',
    href: '/admin/api-keys',
    icon: Key,
    badge: 'Admin',
  },
  {
    name: 'System Settings',
    href: '/admin/settings',
    icon: Settings,
    badge: 'Admin',
  },
  {
    name: 'Database',
    href: '/admin/database',
    icon: Database,
    badge: 'Admin',
  },
]

export function Sidebar() {
  const location = useLocation()
  const { userRole } = useAuth()
  const { sidebarCollapsed, setSidebarCollapsed } = useAppStore()

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return location.pathname === '/dashboard' || location.pathname === '/'
    }
    return location.pathname.startsWith(href)
  }

  return (
    <div
      className={cn(
        "flex flex-col h-full bg-card border-r border-border transition-all duration-300 ease-in-out",
        sidebarCollapsed ? "w-16" : "w-64"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className={cn(
          "flex items-center gap-2 transition-opacity duration-200",
          sidebarCollapsed ? "opacity-0" : "opacity-100"
        )}>
          <Flower2 className="h-6 w-6 text-brand-600" />
          <span className="font-bold text-lg text-gradient">CustomerDaisy</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="h-8 w-8 p-0"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        <div className="space-y-1">
          {navigation
            .filter(item => item.roles.includes(userRole || 'user'))
            .map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover-lift",
                  isActive(item.href)
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                )}
              >
                <item.icon className="h-4 w-4 flex-shrink-0" />
                {!sidebarCollapsed && (
                  <span className="truncate">{item.name}</span>
                )}
              </Link>
            ))}
        </div>

        {/* Admin Section */}
        {userRole === 'admin' && (
          <>
            <div className="pt-4">
              {!sidebarCollapsed && (
                <h3 className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  Administration
                </h3>
              )}
              <div className="space-y-1">
                {adminNavigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover-lift",
                      isActive(item.href)
                        ? "bg-primary text-primary-foreground shadow-sm"
                        : "text-muted-foreground hover:text-foreground hover:bg-accent"
                    )}
                  >
                    <item.icon className="h-4 w-4 flex-shrink-0" />
                    {!sidebarCollapsed && (
                      <>
                        <span className="truncate flex-1">{item.name}</span>
                        <Badge variant="secondary" className="text-xs">
                          {item.badge}
                        </Badge>
                      </>
                    )}
                  </Link>
                ))}
              </div>
            </div>
          </>
        )}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        {!sidebarCollapsed && (
          <div className="text-xs text-muted-foreground text-center">
            CustomerDaisy v2.0
          </div>
        )}
      </div>
    </div>
  )
}