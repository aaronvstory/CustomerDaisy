import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { 
  Plus, 
  Key, 
  Phone, 
  Mail, 
  MapPin,
  Edit,
  Trash2,
  Eye,
  EyeOff,
  Copy,
  Users
} from 'lucide-react'
import { useAuth } from '@/lib/auth'
import { supabase } from '@/lib/supabase'
import { toast } from 'sonner'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const apiKeySchema = z.object({
  service_name: z.enum(['daisysms', 'mailtm', 'mapquest']),
  key_value: z.string().min(1, 'API key is required'),
})

type ApiKeyForm = z.infer<typeof apiKeySchema>

interface ApiKey {
  id: string
  service_name: 'daisysms' | 'mailtm' | 'mapquest'
  key_value: string
  created_by_admin: string
  created_at: string
}

export function AdminApiKeys() {
  const { user } = useAuth()
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [creating, setCreating] = useState(false)
  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set())

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
  } = useForm<ApiKeyForm>({
    resolver: zodResolver(apiKeySchema),
  })

  useEffect(() => {
    loadApiKeys()
  }, [])

  const loadApiKeys = async () => {
    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('api_keys')
        .select('*')
        .order('created_at', { ascending: false })

      if (error) throw error
      setApiKeys(data || [])
    } catch (error) {
      console.error('Error loading API keys:', error)
      toast.error('Failed to load API keys')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateApiKey = async (data: ApiKeyForm) => {
    if (!user) return

    setCreating(true)
    try {
      const { data: apiKey, error } = await supabase
        .from('api_keys')
        .insert({
          service_name: data.service_name,
          key_value: data.key_value,
          created_by_admin: user.id,
        })
        .select()
        .single()

      if (error) throw error

      setApiKeys([apiKey, ...apiKeys])
      setShowCreateDialog(false)
      reset()
      toast.success('API key created successfully')
    } catch (error) {
      console.error('Error creating API key:', error)
      toast.error('Failed to create API key')
    } finally {
      setCreating(false)
    }
  }

  const handleDeleteApiKey = async (keyId: string, serviceName: string) => {
    if (!confirm(`Are you sure you want to delete the ${serviceName} API key?`)) {
      return
    }

    try {
      const { error } = await supabase
        .from('api_keys')
        .delete()
        .eq('id', keyId)

      if (error) throw error

      setApiKeys(apiKeys.filter(k => k.id !== keyId))
      toast.success('API key deleted successfully')
    } catch (error) {
      console.error('Error deleting API key:', error)
      toast.error('Failed to delete API key')
    }
  }

  const toggleKeyVisibility = (keyId: string) => {
    const newVisible = new Set(visibleKeys)
    if (newVisible.has(keyId)) {
      newVisible.delete(keyId)
    } else {
      newVisible.add(keyId)
    }
    setVisibleKeys(newVisible)
  }

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text)
    toast.success(`${label} copied to clipboard`)
  }

  const getServiceIcon = (service: string) => {
    switch (service) {
      case 'daisysms':
        return <Phone className="h-4 w-4" />
      case 'mailtm':
        return <Mail className="h-4 w-4" />
      case 'mapquest':
        return <MapPin className="h-4 w-4" />
      default:
        return <Key className="h-4 w-4" />
    }
  }

  const getServiceName = (service: string) => {
    switch (service) {
      case 'daisysms':
        return 'DaisySMS'
      case 'mailtm':
        return 'Mail.tm'
      case 'mapquest':
        return 'MapQuest'
      default:
        return service
    }
  }

  const maskApiKey = (key: string) => {
    if (key.length <= 8) return '*'.repeat(key.length)
    return key.slice(0, 4) + '*'.repeat(key.length - 8) + key.slice(-4)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold text-gradient">API Key Management</h1>
          <p className="text-muted-foreground">
            Manage API keys for third-party service integrations
          </p>
        </div>
        
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button className="gradient-bg gap-2">
              <Plus className="h-4 w-4" />
              Add API Key
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New API Key</DialogTitle>
              <DialogDescription>
                Add an API key for third-party service integration.
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleSubmit(handleCreateApiKey)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="service_name">Service</Label>
                <Select onValueChange={(value) => setValue('service_name', value as any)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select service" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daisysms">
                      <div className="flex items-center gap-2">
                        <Phone className="h-4 w-4" />
                        DaisySMS
                      </div>
                    </SelectItem>
                    <SelectItem value="mailtm">
                      <div className="flex items-center gap-2">
                        <Mail className="h-4 w-4" />
                        Mail.tm
                      </div>
                    </SelectItem>
                    <SelectItem value="mapquest">
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4" />
                        MapQuest
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
                {errors.service_name && (
                  <p className="text-sm text-destructive">{errors.service_name.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="key_value">API Key</Label>
                <Input
                  id="key_value"
                  type="password"
                  placeholder="Enter API key"
                  {...register('key_value')}
                />
                {errors.key_value && (
                  <p className="text-sm text-destructive">{errors.key_value.message}</p>
                )}
              </div>

              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowCreateDialog(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={creating} className="gradient-bg">
                  {creating ? 'Adding...' : 'Add API Key'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* API Keys Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            API Keys ({apiKeys.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="loading-shimmer h-16 rounded" />
              ))}
            </div>
          ) : apiKeys.length === 0 ? (
            <div className="text-center py-8">
              <Key className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No API keys configured</h3>
              <p className="text-muted-foreground mb-4">
                Add API keys to enable third-party service integrations
              </p>
              <Button onClick={() => setShowCreateDialog(true)} className="gradient-bg">
                <Plus className="mr-2 h-4 w-4" />
                Add First API Key
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Service</TableHead>
                  <TableHead>API Key</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-[150px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {apiKeys.map((apiKey) => (
                  <TableRow key={apiKey.id}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getServiceIcon(apiKey.service_name)}
                        <span className="font-medium">{getServiceName(apiKey.service_name)}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <code className="text-sm bg-muted px-2 py-1 rounded font-mono">
                          {visibleKeys.has(apiKey.id) ? apiKey.key_value : maskApiKey(apiKey.key_value)}
                        </code>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0"
                          onClick={() => toggleKeyVisibility(apiKey.id)}
                        >
                          {visibleKeys.has(apiKey.id) ? (
                            <EyeOff className="h-3 w-3" />
                          ) : (
                            <Eye className="h-3 w-3" />
                          )}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0"
                          onClick={() => copyToClipboard(apiKey.key_value, 'API key')}
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(apiKey.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Badge className="bg-green-100 text-green-800 border-green-200">
                        Active
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          <Users className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                          onClick={() => handleDeleteApiKey(apiKey.id, apiKey.service_name)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Service Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {['daisysms', 'mailtm', 'mapquest'].map((service) => {
          const hasKey = apiKeys.some(k => k.service_name === service)
          return (
            <Card key={service} className={hasKey ? "border-green-200 bg-green-50/50" : "border-yellow-200 bg-yellow-50/50"}>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  {getServiceIcon(service)}
                  {getServiceName(service)}
                  <Badge className={hasKey ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}>
                    {hasKey ? 'Configured' : 'Missing'}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    {service === 'daisysms' && 'SMS verification and phone number rental'}
                    {service === 'mailtm' && 'Temporary email account generation'}
                    {service === 'mapquest' && 'Address validation and geocoding'}
                  </p>
                  {hasKey ? (
                    <div className="text-xs text-green-700">
                      ✓ API key configured and ready to use
                    </div>
                  ) : (
                    <div className="text-xs text-yellow-700">
                      ⚠ API key required for this service
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}