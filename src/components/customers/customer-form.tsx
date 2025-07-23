import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { 
  Loader2, 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  CheckCircle, 
  ArrowRight,
  Sparkles,
  Shield,
  Globe
} from 'lucide-react'
import { toast } from 'sonner'

const customerSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  email: z.string().email('Invalid email address'),
  phone: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  zip: z.string().optional(),
})

type CustomerForm = z.infer<typeof customerSchema>

interface CustomerFormProps {
  onSubmit: (data: CustomerForm) => Promise<void>
  loading?: boolean
  initialData?: Partial<CustomerForm>
}

const steps = [
  { id: 1, name: 'Personal Info', icon: User },
  { id: 2, name: 'Contact Details', icon: Mail },
  { id: 3, name: 'Address Info', icon: MapPin },
  { id: 4, name: 'Review & Create', icon: CheckCircle },
]

export function CustomerFormComponent({ onSubmit, loading = false, initialData }: CustomerFormProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [isGenerating, setIsGenerating] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
    trigger,
  } = useForm<CustomerForm>({
    resolver: zodResolver(customerSchema),
    defaultValues: initialData,
  })

  const watchedValues = watch()

  const generateRandomData = async () => {
    setIsGenerating(true)
    try {
      // Simulate API call to generate random customer data
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const firstNames = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Chris', 'Jessica']
      const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
      const domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
      
      const firstName = firstNames[Math.floor(Math.random() * firstNames.length)]
      const lastName = lastNames[Math.floor(Math.random() * lastNames.length)]
      const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}${Math.floor(Math.random() * 1000)}@${domains[Math.floor(Math.random() * domains.length)]}`
      
      setValue('first_name', firstName)
      setValue('last_name', lastName)
      setValue('email', email)
      setValue('phone', `+1${Math.floor(Math.random() * 9000000000) + 1000000000}`)
      
      toast.success('Random customer data generated!')
    } finally {
      setIsGenerating(false)
    }
  }

  const nextStep = async () => {
    const fieldsToValidate = getFieldsForStep(currentStep)
    const isValid = await trigger(fieldsToValidate)
    
    if (isValid && currentStep < steps.length) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const getFieldsForStep = (step: number): (keyof CustomerForm)[] => {
    switch (step) {
      case 1:
        return ['first_name', 'last_name']
      case 2:
        return ['email', 'phone']
      case 3:
        return ['address', 'city', 'state', 'zip']
      default:
        return []
    }
  }

  const isStepComplete = (step: number) => {
    const fields = getFieldsForStep(step)
    return fields.every(field => {
      const value = watchedValues[field]
      return value && value.toString().trim() !== ''
    })
  }

  const progress = (currentStep / steps.length) * 100

  const onFormSubmit = async (data: CustomerForm) => {
    await onSubmit(data)
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Progress Header */}
      <Card className="glass-effect">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl font-bold">Create New Customer</CardTitle>
              <CardDescription>
                Step {currentStep} of {steps.length}: {steps[currentStep - 1].name}
              </CardDescription>
            </div>
            <Button
              variant="outline"
              onClick={generateRandomData}
              disabled={isGenerating}
              className="gap-2"
            >
              {isGenerating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
              Generate Random
            </Button>
          </div>
          
          <div className="space-y-4">
            <Progress value={progress} className="h-2" />
            
            <div className="flex items-center justify-between">
              {steps.map((step, index) => (
                <div key={step.id} className="flex items-center">
                  <div className={`flex items-center gap-2 ${
                    step.id <= currentStep ? 'text-primary' : 'text-muted-foreground'
                  }`}>
                    <div className={`h-8 w-8 rounded-full flex items-center justify-center border-2 transition-colors ${
                      step.id < currentStep 
                        ? 'bg-primary border-primary text-primary-foreground' 
                        : step.id === currentStep
                        ? 'border-primary text-primary'
                        : 'border-muted-foreground/30'
                    }`}>
                      {step.id < currentStep ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : (
                        <step.icon className="h-4 w-4" />
                      )}
                    </div>
                    <span className="text-sm font-medium hidden sm:block">{step.name}</span>
                  </div>
                  {index < steps.length - 1 && (
                    <ArrowRight className="h-4 w-4 mx-4 text-muted-foreground" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Form Content */}
      <form onSubmit={handleSubmit(onFormSubmit)}>
        <Card>
          <CardContent className="p-6">
            {/* Step 1: Personal Info */}
            {currentStep === 1 && (
              <div className="space-y-6 animate-in">
                <div className="flex items-center gap-2 mb-4">
                  <User className="h-5 w-5 text-brand-600" />
                  <h3 className="text-lg font-semibold">Personal Information</h3>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="first_name">First Name *</Label>
                    <Input
                      id="first_name"
                      placeholder="Enter first name"
                      {...register('first_name')}
                      className="focus-ring"
                    />
                    {errors.first_name && (
                      <p className="text-sm text-destructive">{errors.first_name.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="last_name">Last Name *</Label>
                    <Input
                      id="last_name"
                      placeholder="Enter last name"
                      {...register('last_name')}
                      className="focus-ring"
                    />
                    {errors.last_name && (
                      <p className="text-sm text-destructive">{errors.last_name.message}</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Step 2: Contact Details */}
            {currentStep === 2 && (
              <div className="space-y-6 animate-in">
                <div className="flex items-center gap-2 mb-4">
                  <Mail className="h-5 w-5 text-brand-600" />
                  <h3 className="text-lg font-semibold">Contact Details</h3>
                </div>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address *</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter email address"
                      {...register('email')}
                      className="focus-ring"
                    />
                    {errors.email && (
                      <p className="text-sm text-destructive">{errors.email.message}</p>
                    )}
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Shield className="h-3 w-3" />
                      <span>Temporary email will be generated automatically</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="Enter phone number"
                      {...register('phone')}
                      className="focus-ring"
                    />
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Phone className="h-3 w-3" />
                      <span>Phone number will be rented for SMS verification</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Address Info */}
            {currentStep === 3 && (
              <div className="space-y-6 animate-in">
                <div className="flex items-center gap-2 mb-4">
                  <MapPin className="h-5 w-5 text-brand-600" />
                  <h3 className="text-lg font-semibold">Address Information</h3>
                </div>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="address">Street Address</Label>
                    <Textarea
                      id="address"
                      placeholder="Enter street address"
                      {...register('address')}
                      className="focus-ring resize-none"
                      rows={2}
                    />
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Globe className="h-3 w-3" />
                      <span>Address will be validated using MapQuest API</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="city">City</Label>
                      <Input
                        id="city"
                        placeholder="Enter city"
                        {...register('city')}
                        className="focus-ring"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="state">State</Label>
                      <Input
                        id="state"
                        placeholder="Enter state"
                        {...register('state')}
                        className="focus-ring"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="zip">ZIP Code</Label>
                      <Input
                        id="zip"
                        placeholder="Enter ZIP code"
                        {...register('zip')}
                        className="focus-ring"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: Review */}
            {currentStep === 4 && (
              <div className="space-y-6 animate-in">
                <div className="flex items-center gap-2 mb-4">
                  <CheckCircle className="h-5 w-5 text-brand-600" />
                  <h3 className="text-lg font-semibold">Review & Create</h3>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h4 className="font-medium text-muted-foreground">Personal Information</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">Name:</span>
                          <span className="text-sm font-medium">
                            {watchedValues.first_name} {watchedValues.last_name}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h4 className="font-medium text-muted-foreground">Contact Information</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm text-muted-foreground">Email:</span>
                          <span className="text-sm font-medium">{watchedValues.email}</span>
                        </div>
                        {watchedValues.phone && (
                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Phone:</span>
                            <span className="text-sm font-medium">{watchedValues.phone}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {(watchedValues.address || watchedValues.city || watchedValues.state) && (
                    <>
                      <Separator />
                      <div className="space-y-4">
                        <h4 className="font-medium text-muted-foreground">Address Information</h4>
                        <div className="p-4 bg-muted/50 rounded-lg">
                          {watchedValues.address && (
                            <p className="text-sm">{watchedValues.address}</p>
                          )}
                          <p className="text-sm">
                            {[watchedValues.city, watchedValues.state, watchedValues.zip]
                              .filter(Boolean)
                              .join(', ')}
                          </p>
                        </div>
                      </div>
                    </>
                  )}

                  <div className="p-4 bg-brand-50 border border-brand-200 rounded-lg">
                    <div className="flex items-start gap-3">
                      <Sparkles className="h-5 w-5 text-brand-600 mt-0.5" />
                      <div className="space-y-1">
                        <p className="text-sm font-medium text-brand-800">
                          What happens next?
                        </p>
                        <ul className="text-xs text-brand-700 space-y-1">
                          <li>• Temporary email account will be created</li>
                          <li>• Phone number will be rented for SMS verification</li>
                          <li>• Address will be validated using MapQuest</li>
                          <li>• Customer profile will be saved to database</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Navigation */}
            <div className="flex items-center justify-between pt-6 border-t border-border">
              <Button
                type="button"
                variant="outline"
                onClick={prevStep}
                disabled={currentStep === 1}
              >
                Previous
              </Button>

              <div className="flex items-center gap-2">
                {steps.map((step) => (
                  <div
                    key={step.id}
                    className={`h-2 w-8 rounded-full transition-colors ${
                      step.id <= currentStep ? 'bg-primary' : 'bg-muted'
                    }`}
                  />
                ))}
              </div>

              {currentStep < steps.length ? (
                <Button type="button" onClick={nextStep}>
                  Next
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              ) : (
                <Button type="submit" disabled={loading} className="gradient-bg">
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create Customer'
                  )}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}