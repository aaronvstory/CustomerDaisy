import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  Activity, 
  Phone, 
  MessageSquare, 
  Clock, 
  CheckCircle, 
  XCircle,
  RefreshCw,
  Pause,
  Play,
  Copy
} from 'lucide-react'
import { useAuth } from '@/lib/auth'
import { supabase } from '@/lib/supabase'
import { toast } from 'sonner'
import { formatDistanceToNow } from 'date-fns'

interface VerificationItem {
  id: string
  customer_name: string
  phone_number: string
  status: 'monitoring' | 'completed' | 'failed' | 'timeout'
  started_at: string
  completed_at?: string
  sms_code?: string
  attempts: number
  elapsed_time: number
}

export function SmsMonitor() {
  const { user } = useAuth()
  const [verifications, setVerifications] = useState<VerificationItem[]>([])
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadActiveVerifications()
    
    // Set up real-time monitoring
    if (isMonitoring) {
      const interval = setInterval(() => {
        updateVerificationStatuses()
      }, 3000) // Poll every 3 seconds

      return () => clearInterval(interval)
    }
  }, [isMonitoring, user])

  const loadActiveVerifications = async () => {
    if (!user) return

    try {
      setLoading(true)
      const { data: customers, error } = await supabase
        .from('customers')
        .select('*')
        .eq('user_id', user.id)
        .eq('verification_status', 'pending')

      if (error) throw error

      // Convert to verification items
      const verificationItems: VerificationItem[] = (customers || []).map(customer => ({
        id: customer.id,
        customer_name: `${customer.first_name} ${customer.last_name}`,
        phone_number: customer.phone || 'No phone',
        status: 'monitoring',
        started_at: customer.created_at,
        attempts: Math.floor(Math.random() * 10) + 1, // Mock data
        elapsed_time: Date.now() - new Date(customer.created_at).getTime(),
      }))

      setVerifications(verificationItems)
    } catch (error) {
      console.error('Error loading verifications:', error)
      toast.error('Failed to load verifications')
    } finally {
      setLoading(false)
    }
  }

  const updateVerificationStatuses = () => {
    setVerifications(prev => prev.map(verification => {
      if (verification.status === 'monitoring') {
        const elapsed = Date.now() - new Date(verification.started_at).getTime()
        
        // Simulate random SMS code reception (10% chance per check)
        if (Math.random() < 0.1 && !verification.sms_code) {
          const smsCode = Math.floor(100000 + Math.random() * 900000).toString()
          toast.success(`SMS code received for ${verification.customer_name}: ${smsCode}`)
          
          return {
            ...verification,
            status: 'completed',
            completed_at: new Date().toISOString(),
            sms_code: smsCode,
            elapsed_time: elapsed,
          }
        }

        // Timeout after 10 minutes
        if (elapsed > 600000) {
          return {
            ...verification,
            status: 'timeout',
            elapsed_time: elapsed,
          }
        }

        return {
          ...verification,
          attempts: verification.attempts + 1,
          elapsed_time: elapsed,
        }
      }
      return verification
    }))
  }

  const toggleMonitoring = () => {
    setIsMonitoring(!isMonitoring)
    if (!isMonitoring) {
      toast.info('SMS monitoring started')
    } else {
      toast.info('SMS monitoring paused')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'monitoring':
        return <Clock className="h-4 w-4 animate-pulse" />
      case 'completed':
        return <CheckCircle className="h-4 w-4" />
      case 'failed':
      case 'timeout':
        return <XCircle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'monitoring':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'failed':
      case 'timeout':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const formatElapsedTime = (milliseconds: number) => {
    const seconds = Math.floor(milliseconds / 1000)
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text)
    toast.success(`${label} copied to clipboard`)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold text-gradient">SMS Monitor</h1>
          <p className="text-muted-foreground">
            Real-time SMS verification monitoring
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={loadActiveVerifications}
            className="gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
          <Button
            onClick={toggleMonitoring}
            className={isMonitoring ? "gap-2" : "gap-2 gradient-bg"}
          >
            {isMonitoring ? (
              <>
                <Pause className="h-4 w-4" />
                Pause Monitoring
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Start Monitoring
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Monitoring Status */}
      <Card className={isMonitoring ? "border-green-200 bg-green-50/50" : ""}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className={isMonitoring ? "h-5 w-5 text-green-600 animate-pulse" : "h-5 w-5"} />
            Monitoring Status
            <Badge className={isMonitoring ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}>
              {isMonitoring ? 'Active' : 'Paused'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {verifications.filter(v => v.status === 'monitoring').length}
              </div>
              <div className="text-sm text-muted-foreground">Active</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {verifications.filter(v => v.status === 'completed').length}
              </div>
              <div className="text-sm text-muted-foreground">Completed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {verifications.filter(v => v.status === 'timeout' || v.status === 'failed').length}
              </div>
              <div className="text-sm text-muted-foreground">Failed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">
                {verifications.length > 0 
                  ? ((verifications.filter(v => v.status === 'completed').length / verifications.length) * 100).toFixed(1)
                  : 0
                }%
              </div>
              <div className="text-sm text-muted-foreground">Success Rate</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Verification List */}
      <div className="space-y-4">
        {loading ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <Card key={i}>
                <CardContent className="p-6">
                  <div className="loading-shimmer h-20 rounded" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : verifications.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No active verifications</h3>
              <p className="text-muted-foreground">
                Create customers with phone numbers to start SMS monitoring
              </p>
            </CardContent>
          </Card>
        ) : (
          verifications.map((verification) => (
            <Card key={verification.id} className="hover-lift">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(verification.status)}
                      <div>
                        <h3 className="font-semibold">{verification.customer_name}</h3>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Phone className="h-3 w-3" />
                          <span>{verification.phone_number}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-4 w-4 p-0"
                            onClick={() => copyToClipboard(verification.phone_number, 'Phone number')}
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <Badge variant="outline" className={getStatusColor(verification.status)}>
                        {verification.status === 'monitoring' && 'Monitoring'}
                        {verification.status === 'completed' && 'Completed'}
                        {verification.status === 'timeout' && 'Timeout'}
                        {verification.status === 'failed' && 'Failed'}
                      </Badge>
                      <div className="text-xs text-muted-foreground mt-1">
                        {verification.status === 'monitoring' 
                          ? `${formatElapsedTime(verification.elapsed_time)} elapsed`
                          : verification.completed_at 
                          ? formatDistanceToNow(new Date(verification.completed_at), { addSuffix: true })
                          : formatDistanceToNow(new Date(verification.started_at), { addSuffix: true })
                        }
                      </div>
                    </div>

                    {verification.status === 'monitoring' && (
                      <div className="w-24">
                        <Progress 
                          value={(verification.elapsed_time / 600000) * 100} // 10 minute timeout
                          className="h-2"
                        />
                        <div className="text-xs text-muted-foreground mt-1 text-center">
                          {verification.attempts} attempts
                        </div>
                      </div>
                    )}

                    {verification.sms_code && (
                      <div className="flex items-center gap-2 p-2 bg-green-50 border border-green-200 rounded-lg">
                        <MessageSquare className="h-4 w-4 text-green-600" />
                        <code className="text-sm font-mono text-green-800">
                          {verification.sms_code}
                        </code>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0"
                          onClick={() => copyToClipboard(verification.sms_code!, 'SMS code')}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}