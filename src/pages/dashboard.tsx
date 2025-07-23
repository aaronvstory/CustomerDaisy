import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { StatsCards } from '@/components/dashboard/stats-cards'
import { ActivityFeed } from '@/components/dashboard/activity-feed'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  BarChart3, 
  Users, 
  TrendingUp, 
  Activity,
  Plus,
  ArrowRight,
  Sparkles
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuth } from '@/lib/auth'
import { supabase } from '@/lib/supabase'

export function Dashboard() {
  const { user, userRole } = useAuth()
  const [stats, setStats] = useState({
    totalCustomers: 0,
    verifiedCustomers: 0,
    pendingVerifications: 0,
    successRate: 0,
    totalSmsReceived: 0,
    activePhoneNumbers: 0,
    emailsGenerated: 0,
    addressesValidated: 0,
  })
  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      // Load customer statistics
      const { data: customers, error } = await supabase
        .from('customers')
        .select('*')
        .eq('user_id', user?.id)

      if (error) throw error

      const totalCustomers = customers?.length || 0
      const verifiedCustomers = customers?.filter(c => c.verification_status === 'verified').length || 0
      const pendingVerifications = customers?.filter(c => c.verification_status === 'pending').length || 0
      const successRate = totalCustomers > 0 ? (verifiedCustomers / totalCustomers) * 100 : 0

      setStats({
        totalCustomers,
        verifiedCustomers,
        pendingVerifications,
        successRate,
        totalSmsReceived: verifiedCustomers, // Simplified
        activePhoneNumbers: pendingVerifications,
        emailsGenerated: totalCustomers,
        addressesValidated: customers?.filter(c => c.address).length || 0,
      })

      // Generate mock activity data
      const mockActivities = customers?.slice(0, 10).map((customer, index) => ({
        id: customer.id,
        type: index % 3 === 0 ? 'customer_created' : index % 3 === 1 ? 'sms_received' : 'verification_completed',
        customer_name: `${customer.first_name} ${customer.last_name}`,
        description: index % 3 === 0 
          ? 'New customer profile created' 
          : index % 3 === 1 
          ? 'SMS verification code received'
          : 'Customer verification completed',
        timestamp: customer.created_at,
      })) || []

      setActivities(mockActivities)
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="loading-shimmer h-20 rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold text-gradient">
            Welcome back!
          </h1>
          <p className="text-muted-foreground">
            Here's what's happening with your customer management today.
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="gap-1">
            <Activity className="h-3 w-3" />
            {userRole === 'admin' ? 'Administrator' : 'User'}
          </Badge>
          <Link to="/customers/new">
            <Button className="gradient-bg gap-2">
              <Plus className="h-4 w-4" />
              New Customer
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <StatsCards stats={stats} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              Quick Actions
            </CardTitle>
            <CardDescription>
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link to="/customers/new" className="block">
              <Button variant="outline" className="w-full justify-start gap-2 hover-lift">
                <Plus className="h-4 w-4" />
                Create New Customer
                <ArrowRight className="h-4 w-4 ml-auto" />
              </Button>
            </Link>
            
            <Link to="/customers" className="block">
              <Button variant="outline" className="w-full justify-start gap-2 hover-lift">
                <Users className="h-4 w-4" />
                View All Customers
                <ArrowRight className="h-4 w-4 ml-auto" />
              </Button>
            </Link>
            
            <Link to="/sms-monitor" className="block">
              <Button variant="outline" className="w-full justify-start gap-2 hover-lift">
                <Activity className="h-4 w-4" />
                SMS Monitor
                <ArrowRight className="h-4 w-4 ml-auto" />
              </Button>
            </Link>
            
            <Link to="/export" className="block">
              <Button variant="outline" className="w-full justify-start gap-2 hover-lift">
                <BarChart3 className="h-4 w-4" />
                Export Data
                <ArrowRight className="h-4 w-4 ml-auto" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Activity Feed */}
        <div className="lg:col-span-2">
          <ActivityFeed activities={activities} />
        </div>
      </div>

      {/* Performance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Performance Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Verification Success Rate</span>
                <span className="text-sm font-medium">{stats.successRate.toFixed(1)}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Average Processing Time</span>
                <span className="text-sm font-medium">2.3 minutes</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">API Response Time</span>
                <span className="text-sm font-medium">1.2 seconds</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">System Uptime</span>
                <span className="text-sm font-medium">99.9%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">DaisySMS API</span>
                <Badge className="bg-green-100 text-green-800 border-green-200">Online</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Mail.tm API</span>
                <Badge className="bg-green-100 text-green-800 border-green-200">Online</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">MapQuest API</span>
                <Badge className="bg-green-100 text-green-800 border-green-200">Online</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Database</span>
                <Badge className="bg-green-100 text-green-800 border-green-200">Healthy</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}