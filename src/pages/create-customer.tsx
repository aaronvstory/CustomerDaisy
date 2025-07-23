import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CustomerFormComponent } from '@/components/customers/customer-form'
import { useAuth } from '@/lib/auth'
import { supabase } from '@/lib/supabase'
import { toast } from 'sonner'

interface CustomerFormData {
  first_name: string
  last_name: string
  email: string
  phone?: string
  address?: string
  city?: string
  state?: string
  zip?: string
}

export function CreateCustomer() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (data: CustomerFormData) => {
    if (!user) {
      toast.error('You must be logged in to create customers')
      return
    }

    setLoading(true)
    try {
      // Simulate API integrations
      toast.info('Creating temporary email account...')
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      toast.info('Renting phone number for SMS verification...')
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      toast.info('Validating address with MapQuest...')
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Create customer in database
      const { data: customer, error } = await supabase
        .from('customers')
        .insert({
          user_id: user.id,
          first_name: data.first_name,
          last_name: data.last_name,
          email: data.email,
          phone: data.phone || null,
          address: data.address || null,
          city: data.city || null,
          state: data.state || null,
          zip: data.zip || null,
          verification_status: 'pending',
        })
        .select()
        .single()

      if (error) throw error

      toast.success('Customer created successfully!')
      navigate('/customers')
    } catch (error) {
      console.error('Error creating customer:', error)
      toast.error('Failed to create customer')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold text-gradient">Create New Customer</h1>
          <p className="text-muted-foreground">
            Generate a complete customer profile with SMS verification
          </p>
        </div>
      </div>

      <CustomerFormComponent onSubmit={handleSubmit} loading={loading} />
    </div>
  )
}