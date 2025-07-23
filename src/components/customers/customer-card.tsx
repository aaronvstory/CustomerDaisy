import { useState } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { 
  MoreHorizontal, 
  Phone, 
  Mail, 
  MapPin, 
  Edit, 
  Trash2, 
  MessageSquare,
  CheckCircle,
  Clock,
  XCircle,
  Copy,
  ExternalLink
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

interface Customer {
  id: string
  first_name: string
  last_name: string
  email: string
  phone: string | null
  address: string | null
  city: string | null
  state: string | null
  zip: string | null
  verification_status: 'pending' | 'verified' | 'failed'
  sms_code: string | null
  created_at: string
  updated_at: string
}

interface CustomerCardProps {
  customer: Customer
  onEdit?: (customer: Customer) => void
  onDelete?: (customer: Customer) => void
  onStartVerification?: (customer: Customer) => void
}

export function CustomerCard({ customer, onEdit, onDelete, onStartVerification }: CustomerCardProps) {
  const [showDetails, setShowDetails] = useState(false)

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'verified':
        return <CheckCircle className="h-3 w-3" />
      case 'pending':
        return <Clock className="h-3 w-3" />
      case 'failed':
        return <XCircle className="h-3 w-3" />
      default:
        return <Clock className="h-3 w-3" />
    }
  }

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text)
    toast.success(`${label} copied to clipboard`)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <>
      <Card className="hover-lift transition-all duration-200 group">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <Avatar className="h-10 w-10 ring-2 ring-brand-100">
                <AvatarFallback className="bg-brand-100 text-brand-700 font-semibold">
                  {getInitials(customer.first_name, customer.last_name)}
                </AvatarFallback>
              </Avatar>
              <div>
                <h3 className="font-semibold text-base">
                  {customer.first_name} {customer.last_name}
                </h3>
                <p className="text-sm text-muted-foreground">{customer.email}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Badge 
                variant="outline" 
                className={cn("text-xs font-medium", getStatusColor(customer.verification_status))}
              >
                {getStatusIcon(customer.verification_status)}
                <span className="ml-1 capitalize">{customer.verification_status}</span>
              </Badge>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem onClick={() => setShowDetails(true)}>
                    <ExternalLink className="mr-2 h-4 w-4" />
                    View Details
                  </DropdownMenuItem>
                  {onEdit && (
                    <DropdownMenuItem onClick={() => onEdit(customer)}>
                      <Edit className="mr-2 h-4 w-4" />
                      Edit Customer
                    </DropdownMenuItem>
                  )}
                  {onStartVerification && customer.verification_status === 'pending' && (
                    <DropdownMenuItem onClick={() => onStartVerification(customer)}>
                      <MessageSquare className="mr-2 h-4 w-4" />
                      Start Verification
                    </DropdownMenuItem>
                  )}
                  {onDelete && (
                    <DropdownMenuItem 
                      onClick={() => onDelete(customer)}
                      className="text-destructive focus:text-destructive"
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete Customer
                    </DropdownMenuItem>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-3">
          {/* Contact Info */}
          <div className="space-y-2">
            {customer.phone && (
              <div className="flex items-center gap-2 text-sm">
                <Phone className="h-4 w-4 text-muted-foreground" />
                <span className="flex-1">{customer.phone}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0"
                  onClick={() => copyToClipboard(customer.phone!, 'Phone number')}
                >
                  <Copy className="h-3 w-3" />
                </Button>
              </div>
            )}
            
            <div className="flex items-center gap-2 text-sm">
              <Mail className="h-4 w-4 text-muted-foreground" />
              <span className="flex-1 truncate">{customer.email}</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0"
                onClick={() => copyToClipboard(customer.email, 'Email')}
              >
                <Copy className="h-3 w-3" />
              </Button>
            </div>

            {(customer.city || customer.state) && (
              <div className="flex items-center gap-2 text-sm">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <span className="flex-1 truncate">
                  {[customer.city, customer.state].filter(Boolean).join(', ')}
                </span>
              </div>
            )}
          </div>

          {/* SMS Code */}
          {customer.sms_code && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium text-green-800">SMS Code</span>
                </div>
                <div className="flex items-center gap-2">
                  <code className="text-sm font-mono bg-green-100 px-2 py-1 rounded text-green-800">
                    {customer.sms_code}
                  </code>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0"
                    onClick={() => copyToClipboard(customer.sms_code!, 'SMS code')}
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Created Date */}
          <div className="text-xs text-muted-foreground">
            Created {formatDate(customer.created_at)}
          </div>
        </CardContent>
      </Card>

      {/* Details Dialog */}
      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-3">
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-brand-100 text-brand-700">
                  {getInitials(customer.first_name, customer.last_name)}
                </AvatarFallback>
              </Avatar>
              {customer.first_name} {customer.last_name}
            </DialogTitle>
            <DialogDescription>
              Customer details and verification information
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Status */}
            <div className="flex items-center gap-2">
              <Badge 
                variant="outline" 
                className={cn("text-sm", getStatusColor(customer.verification_status))}
              >
                {getStatusIcon(customer.verification_status)}
                <span className="ml-2 capitalize">{customer.verification_status}</span>
              </Badge>
            </div>

            {/* Contact Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide">
                  Contact Information
                </h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-2 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">{customer.email}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                      onClick={() => copyToClipboard(customer.email, 'Email')}
                    >
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                  
                  {customer.phone && (
                    <div className="flex items-center justify-between p-2 rounded-lg bg-muted/50">
                      <div className="flex items-center gap-2">
                        <Phone className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">{customer.phone}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0"
                        onClick={() => copyToClipboard(customer.phone!, 'Phone')}
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>

              {/* Address Information */}
              {(customer.address || customer.city || customer.state) && (
                <div className="space-y-3">
                  <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide">
                    Address Information
                  </h4>
                  <div className="p-3 rounded-lg bg-muted/50 space-y-1">
                    {customer.address && (
                      <p className="text-sm">{customer.address}</p>
                    )}
                    <p className="text-sm">
                      {[customer.city, customer.state, customer.zip].filter(Boolean).join(', ')}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* SMS Code */}
            {customer.sms_code && (
              <div className="space-y-3">
                <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wide">
                  Verification Code
                </h4>
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <MessageSquare className="h-5 w-5 text-green-600" />
                      <span className="font-medium text-green-800">SMS Code Received</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <code className="text-lg font-mono bg-green-100 px-3 py-1 rounded text-green-800">
                        {customer.sms_code}
                      </code>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0"
                        onClick={() => copyToClipboard(customer.sms_code!, 'SMS code')}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Timestamps */}
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
              <div>
                <p className="text-xs text-muted-foreground">Created</p>
                <p className="text-sm font-medium">{formatDate(customer.created_at)}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Updated</p>
                <p className="text-sm font-medium">{formatDate(customer.updated_at)}</p>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}