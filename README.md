# 🌸 CustomerDaisy - Premium SaaS Platform

A modern, production-ready web application for comprehensive customer profile management with SMS verification, temporary email generation, and address validation.

## ✨ Features

### 🔐 **Authentication & User Management**
- Secure login/register with Supabase Auth
- Role-based access control (Admin/User)
- Admin dashboard for user creation and management
- API key assignment system

### 👥 **Customer Profile Management**
- Multi-step customer creation wizard
- Real-time form validation
- Advanced search and filtering
- Bulk operations support
- Beautiful customer profile cards

### 📱 **Third-Party Integrations**
- **DaisySMS**: Phone number rental and SMS verification
- **Mail.tm**: Temporary email generation
- **MapQuest**: Address validation and geocoding
- Real-time SMS monitoring dashboard

### 🎨 **Premium Design System**
- Three beautiful themes (Light/Dark/Grey)
- Smooth theme transitions
- shadcn/ui components exclusively
- Mobile-first responsive design
- Professional micro-interactions

### 📊 **Analytics & Reporting**
- Comprehensive dashboard with metrics
- Real-time activity feed
- Performance monitoring
- Export functionality (CSV, JSON, TXT)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Supabase account (free tier)

### 1. Clone and Install
```bash
git clone <repository-url>
cd customerdaisy
npm install
```

### 2. Supabase Setup
1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Go to Settings > API to get your project URL and anon key
3. Create a `.env.local` file:

```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Database Setup
1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and run the migration from `supabase/migrations/create_schema.sql`

### 4. Launch Application
```bash
npm run dev
```

Visit `http://localhost:5173` and sign in with:
- **Admin**: username `admin`, password `admin123`
- **User**: username `user`, password `user123`

## 🏗️ Architecture

### Frontend Stack
- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **shadcn/ui** for components
- **React Router** for navigation
- **Zustand** for state management
- **React Hook Form** for forms
- **Zod** for validation

### Backend & Database
- **Supabase** for database and authentication
- **PostgreSQL** with Row Level Security
- **Real-time subscriptions** for live updates
- **Serverless functions** for API integrations

### Design System
- **CSS Custom Properties** for theming
- **Smooth transitions** between themes
- **Mobile-first** responsive design
- **Accessibility** compliant
- **Professional animations** and micro-interactions

## 📱 User Roles & Permissions

### 👤 **Regular Users**
- Create and manage their own customer profiles
- Access SMS verification monitoring
- Export their customer data
- Use assigned API keys for integrations

### 🛡️ **Administrators**
- All user permissions plus:
- Create and manage user accounts
- Configure API keys for services
- Assign API keys to users
- Access system-wide analytics
- Manage database and settings

## 🔧 Configuration

### API Keys Setup (Admin Only)
1. Sign in as admin
2. Navigate to **Admin > API Keys**
3. Add API keys for:
   - **DaisySMS**: For SMS verification services
   - **Mail.tm**: For temporary email generation
   - **MapQuest**: For address validation

### User Management
1. Navigate to **Admin > User Management**
2. Create new users with appropriate roles
3. Assign API keys to users as needed

## 🎨 Themes

The application supports three beautiful themes:

- **Light Theme**: Clean, bright interface
- **Dark Theme**: Modern dark interface
- **Grey Theme**: Professional monochrome interface

Themes can be switched instantly with smooth CSS transitions.

## 📊 Dashboard Features

### User Dashboard
- Customer statistics overview
- Recent activity feed
- Quick action shortcuts
- Performance metrics

### Admin Dashboard
- System-wide analytics
- User activity monitoring
- API usage statistics
- Health status indicators

## 🔒 Security Features

- **Row Level Security** on all database tables
- **Role-based access control** throughout the application
- **Secure API key storage** and assignment
- **Input validation** and sanitization
- **Environment variable** configuration

## 🚀 Deployment

### Netlify Deployment
1. Connect your repository to Netlify
2. Set environment variables in Netlify dashboard
3. Deploy with zero configuration

### Vercel Deployment
1. Connect your repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically

### Environment Variables
```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 🧪 Development

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Project Structure
```
src/
├── components/          # Reusable UI components
│   ├── ui/             # shadcn/ui components
│   ├── auth/           # Authentication components
│   ├── customers/      # Customer-related components
│   ├── dashboard/      # Dashboard components
│   └── layout/         # Layout components
├── lib/                # Utilities and configurations
│   ├── auth.tsx        # Authentication context
│   ├── store.ts        # Global state management
│   ├── supabase.ts     # Supabase client
│   └── utils.ts        # Utility functions
├── pages/              # Page components
│   ├── admin/          # Admin-only pages
│   ├── dashboard.tsx   # Main dashboard
│   ├── customers.tsx   # Customer management
│   └── ...
└── supabase/
    └── migrations/     # Database migrations
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation
- Open an issue on GitHub
- Contact the development team

---

**CustomerDaisy - Premium Customer Management Platform** 🌸