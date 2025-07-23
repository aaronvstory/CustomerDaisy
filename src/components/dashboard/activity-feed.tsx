import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { 
  UserPlus, 
  MessageSquare, 
  CheckCircle, 
  XCircle, 
  Phone,
  Mail,
  MapPin,
  Clock
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

interface ActivityItem {
  id: string
  type: 'customer_created' | 'sms_received' | 'verification_completed' | 'verification_failed' | 'phone_rented' | 'email_created' | 'address_validated'
  customer_name: string
  description: string
  timestamp: string
  metadata?: Record<string, any>
}

interface ActivityFeedProps {
  activities: ActivityItem[]
}

export function ActivityFeed({ activities }: ActivityFeedProps) {
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'customer_created':
        return <UserPlus className="h-4 w-4" />
      case 'sms_received':
        return <MessageSquare className="h-4 w-4" />
      case 'verification_completed':
        return <CheckCircle className="h-4 w-4" />
      case 'verification_failed':
        return <XCircle className="h-4 w-4" />
      case 'phone_rented':
        return <Phone className="h-4 w-4" />
      case 'email_created':
        return <Mail className="h-4 w-4" />
      case 'address_validated':
        return <MapPin className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'customer_created':
        return 'text-blue-600 bg-blue-50'
      case 'sms_received':
        return 'text-purple-600 bg-purple-50'
      case 'verification_completed':
        return 'text-green-600 bg-green-50'
      case 'verification_failed':
        return 'text-red-600 bg-red-50'
      case 'phone_rented':
        return 'text-indigo-600 bg-indigo-50'
      case 'email_created':
        return 'text-cyan-600 bg-cyan-50'
      case 'address_validated':
        return 'text-emerald-600 bg-emerald-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const getActivityBadge = (type: string) => {
    switch (type) {
      case 'verification_completed':
        return <Badge className="bg-green-100 text-green-800 border-green-200">Success</Badge>
      case 'verification_failed':
        return <Badge className="bg-red-100 text-red-800 border-red-200">Failed</Badge>
      case 'customer_created':
        return <Badge className="bg-blue-100 text-blue-800 border-blue-200">New</Badge>
      default:
        return null
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Recent Activity
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No recent activity</p>
            </div>
          ) : (
            activities.map((activity) => (
              <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors">
                <div className={`h-8 w-8 rounded-full flex items-center justify-center ${getActivityColor(activity.type)}`}>
                  {getActivityIcon(activity.type)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium truncate">
                      {activity.customer_name}
                    </p>
                    {getActivityBadge(activity.type)}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {activity.description}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}