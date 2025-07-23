import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { CustomerCard } from '@/components/customers/customer-card'
import { 
  Plus, 
  Search, 
  Filter, 
  Download, 
  Users,
  SortAsc,
  SortDesc,
  Grid,
  List
} from 'lucide-react'
import { useAuth } from '@/lib/auth'
import { supabase } from '@/lib/supabase'
import { toast } from 'sonner'

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

export function Customers() {
  const { user } = useAuth()
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [sortBy, setSortBy] = useState<string>('created_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  useEffect(() => {
    loadCustomers()
  }, [user])

  const loadCustomers = async () => {
    if (!user) return

    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('customers')
        .select('*')
        .eq('user_id', user.id)
        .order(sortBy, { ascending: sortOrder === 'asc' })

      if (error) throw error
      setCustomers(data || [])
    } catch (error) {
      console.error('Error loading customers:', error)
      toast.error('Failed to load customers')
    } finally {
      setLoading(false)
    }
  }

  const filteredCustomers = customers.filter(customer => {
    const matchesSearch = 
      customer.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      customer.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      customer.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (customer.phone && customer.phone.includes(searchTerm))

    const matchesStatus = statusFilter === 'all' || customer.verification_status === statusFilter

    return matchesSearch && matchesStatus
  })

  const handleDeleteCustomer = async (customer: Customer) => {
    if (!confirm(`Are you sure you want to delete ${customer.first_name} ${customer.last_name}?`)) {
      return
    }

    try {
      const { error } = await supabase
        .from('customers')
        .delete()
        .eq('id', customer.id)

      if (error) throw error

      setCustomers(customers.filter(c => c.id !== customer.id))
      toast.success('Customer deleted successfully')
    } catch (error) {
      console.error('Error deleting customer:', error)
      toast.error('Failed to delete customer')
    }
  }

  const handleStartVerification = (customer: Customer) => {
    toast.info(`Starting SMS verification for ${customer.first_name} ${customer.last_name}`)
    // TODO: Implement SMS verification logic
  }

  const getStatusCounts = () => {
    return {
      all: customers.length,
      pending: customers.filter(c => c.verification_status === 'pending').length,
      verified: customers.filter(c => c.verification_status === 'verified').length,
      failed: customers.filter(c => c.verification_status === 'failed').length,
    }
  }

  const statusCounts = getStatusCounts()

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="loading-shimmer h-8 w-48 rounded" />
          <div className="loading-shimmer h-10 w-32 rounded" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="loading-shimmer h-64 rounded-lg" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold text-gradient">Customers</h1>
          <p className="text-muted-foreground">
            Manage your customer profiles and verifications
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Link to="/customers/new">
            <Button className="gradient-bg gap-2">
              <Plus className="h-4 w-4" />
              New Customer
            </Button>
          </Link>
          <Button variant="outline" className="gap-2">
            <Download className="h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search customers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status ({statusCounts.all})</SelectItem>
            <SelectItem value="pending">Pending ({statusCounts.pending})</SelectItem>
            <SelectItem value="verified">Verified ({statusCounts.verified})</SelectItem>
            <SelectItem value="failed">Failed ({statusCounts.failed})</SelectItem>
          </SelectContent>
        </Select>

        <Select value={sortBy} onValueChange={setSortBy}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="created_at">Date Created</SelectItem>
            <SelectItem value="first_name">First Name</SelectItem>
            <SelectItem value="last_name">Last Name</SelectItem>
            <SelectItem value="verification_status">Status</SelectItem>
          </SelectContent>
        </Select>

        <Button
          variant="outline"
          size="sm"
          onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          className="gap-2"
        >
          {sortOrder === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />}
        </Button>

        <div className="flex items-center border rounded-lg p-1">
          <Button
            variant={viewMode === 'grid' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('grid')}
            className="h-8 w-8 p-0"
          >
            <Grid className="h-4 w-4" />
          </Button>
          <Button
            variant={viewMode === 'list' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('list')}
            className="h-8 w-8 p-0"
          >
            <List className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Status Summary */}
      <div className="flex items-center gap-4 p-4 bg-muted/50 rounded-lg">
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium">
            {filteredCustomers.length} of {customers.length} customers
          </span>
        </div>
        {statusFilter !== 'all' && (
          <Badge variant="outline" className="capitalize">
            {statusFilter} only
          </Badge>
        )}
        {searchTerm && (
          <Badge variant="outline">
            Search: "{searchTerm}"
          </Badge>
        )}
      </div>

      {/* Customer Grid/List */}
      {filteredCustomers.length === 0 ? (
        <div className="text-center py-12">
          <Users className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No customers found</h3>
          <p className="text-muted-foreground mb-4">
            {customers.length === 0 
              ? "Get started by creating your first customer profile"
              : "Try adjusting your search or filter criteria"
            }
          </p>
          <Link to="/customers/new">
            <Button className="gradient-bg">
              <Plus className="mr-2 h-4 w-4" />
              Create First Customer
            </Button>
          </Link>
        </div>
      ) : (
        <div className={
          viewMode === 'grid' 
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            : "space-y-4"
        }>
          {filteredCustomers.map((customer) => (
            <CustomerCard
              key={customer.id}
              customer={customer}
              onDelete={handleDeleteCustomer}
              onStartVerification={handleStartVerification}
            />
          ))}
        </div>
      )}
    </div>
  )
}