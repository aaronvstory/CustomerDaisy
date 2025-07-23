import { Outlet } from 'react-router-dom'
import { Sidebar } from './sidebar'
import { Header } from './header'
import { useAppStore } from '@/lib/store'
import { cn } from '@/lib/utils'

export function AppLayout() {
  const { sidebarCollapsed } = useAppStore()

  return (
    <div className="h-screen flex bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main 
          className={cn(
            "flex-1 overflow-auto transition-all duration-300 ease-in-out",
            "bg-gradient-to-br from-background via-background to-muted/20"
          )}
        >
          <div className="container mx-auto p-6 animate-in">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}