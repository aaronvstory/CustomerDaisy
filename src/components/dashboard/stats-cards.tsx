import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Users, 
  UserCheck, 
  Clock, 
  TrendingUp, 
  Phone, 
  Mail,
  MapPin,
  Activity
} from 'lucide-react'

interface StatsCardsProps {
  stats: {
    totalCustomers: number
    verifiedCustomers: number
    pendingVerifications: number
    successRate: number
    totalSmsReceived: number
    activePhoneNumbers: number
    emailsGenerated: number
    addressesValidated: number
  }
}

export function StatsCards({ stats }: StatsCardsProps) {
  const cards = [
    {
      title: 'Total Customers',
      value: stats.totalCustomers.toLocaleString(),
      icon: Users,
      description: 'All customer profiles',
      trend: '+12% from last month',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Verified Customers',
      value: stats.verifiedCustomers.toLocaleString(),
      icon: UserCheck,
      description: 'SMS verified profiles',
      trend: `${stats.successRate.toFixed(1)}% success rate`,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Pending Verifications',
      value: stats.pendingVerifications.toLocaleString(),
      icon: Clock,
      description: 'Awaiting SMS codes',
      trend: 'Real-time monitoring',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      title: 'SMS Received',
      value: stats.totalSmsReceived.toLocaleString(),
      icon: Phone,
      description: 'Total verification codes',
      trend: '+8% this week',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Active Numbers',
      value: stats.activePhoneNumbers.toLocaleString(),
      icon: Activity,
      description: 'Rented phone numbers',
      trend: 'DaisySMS integration',
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
    },
    {
      title: 'Emails Generated',
      value: stats.emailsGenerated.toLocaleString(),
      icon: Mail,
      description: 'Temporary email accounts',
      trend: 'Mail.tm integration',
      color: 'text-cyan-600',
      bgColor: 'bg-cyan-50',
    },
    {
      title: 'Addresses Validated',
      value: stats.addressesValidated.toLocaleString(),
      icon: MapPin,
      description: 'MapQuest validations',
      trend: '99.2% accuracy',
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
    },
    {
      title: 'Success Rate',
      value: `${stats.successRate.toFixed(1)}%`,
      icon: TrendingUp,
      description: 'Overall verification rate',
      trend: '+2.1% improvement',
      color: 'text-rose-600',
      bgColor: 'bg-rose-50',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <Card key={card.title} className="hover-lift transition-all duration-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {card.title}
            </CardTitle>
            <div className={`h-8 w-8 rounded-lg ${card.bgColor} flex items-center justify-center`}>
              <card.icon className={`h-4 w-4 ${card.color}`} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="text-2xl font-bold">{card.value}</div>
              <p className="text-xs text-muted-foreground">{card.description}</p>
              <Badge variant="secondary" className="text-xs">
                {card.trend}
              </Badge>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}