# 🌼 CustomerDaisy

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security: Environment Variables](https://img.shields.io/badge/security-environment%20variables-green.svg)](https://github.com/aaronvstory/CustomerDaisy/blob/main/SECURITY_SETUP.md)
[![Web Ready](https://img.shields.io/badge/web%20conversion-ready-brightgreen.svg)](https://github.com/aaronvstory/CustomerDaisy/blob/main/WEB_APPLICATION_CONVERSION_GUIDE.md)

**CustomerDaisy** is a comprehensive customer creation system that integrates with **DaisySMS** for phone verification, **Mail.tm** for temporary email creation, and **MapQuest** for real address generation. The system provides a rich console interface for creating and managing customer profiles with real-time SMS verification capabilities.

---

## ✨ Features

### 🔐 **Security-First Design**
- **Environment Variable Management**: Secure API key handling with `.env` files
- **Git-Protected Credentials**: Sensitive data never committed to version control
- **Zero Hardcoded Secrets**: All credentials loaded from environment variables

### 📱 **SMS Verification System**
- **Real-time Monitoring**: Live SMS code tracking with Rich console interface
- **Multi-verification Support**: Handle multiple phone verifications simultaneously
- **Automatic Code Detection**: Polls DaisySMS API and captures verification codes
- **Rate Limiting Compliance**: Respects API limits with intelligent polling

### 🌐 **Multi-API Integration**
- **DaisySMS**: Phone number rental and SMS verification
- **Mail.tm**: Temporary email account creation with domain management
- **MapQuest**: Real address generation and validation with geocoding

### 💾 **Robust Data Management**
- **SQLite Database**: Primary storage with full customer record management
- **JSON Backup**: Automatic backup and export functionality
- **Analytics Generation**: Geographic and usage analytics from stored data
- **Export Capabilities**: CSV, JSON, and TXT export formats

### 🎨 **Rich User Interface**
- **Interactive Console**: Beautiful Rich-powered interface with colors and tables
- **Progress Indicators**: Real-time progress tracking for long operations
- **Error Handling**: Graceful error recovery with user-friendly messages
- **Menu Navigation**: Intuitive menu system for all operations

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** installed on your system
- **UV package manager** (will be installed automatically if missing)
- **API Keys** for DaisySMS, MapQuest (see Environment Setup below)

### 1. Clone & Setup
```bash
git clone https://github.com/aaronvstory/CustomerDaisy.git
cd CustomerDaisy
./setup.bat  # Windows
```

### 2. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual API keys
# DAISYSMS_API_KEY=your_daisysms_api_key_here
# MAPQUEST_API_KEY=your_mapquest_api_key_here
# MAILTM_DEFAULT_PASSWORD=your_secure_password_here
```

### 3. Launch Application
```bash
./launch.bat  # Windows
# OR directly:
python main.py
```

---

## 📁 Project Structure

```
CustomerDaisy/
├── 📋 main.py                          # Main application entry point
├── 📁 src/                             # Core application modules
│   ├── 🗄️ customer_db.py              # Database management & analytics
│   ├── 📱 daisy_sms.py                 # DaisySMS API integration
│   ├── 📧 mail_tm.py                   # Mail.tm API integration
│   ├── 🗺️ mapquest_address.py          # MapQuest address services
│   ├── 📡 sms_monitor.py               # Real-time SMS monitoring
│   └── ⚙️ config_manager.py            # Configuration management
├── 🔒 .env.example                     # Environment template (safe to commit)
├── 🔒 .env                             # Your actual credentials (git-ignored)
├── ⚙️ config.ini                       # Application configuration
├── 📦 pyproject.toml                   # Dependencies & project metadata
├── 🧪 test_*.py                        # Comprehensive test suite
├── 📚 WEB_APPLICATION_CONVERSION_GUIDE.md  # Web conversion documentation
├── 🔐 SECURITY_SETUP.md                # Security implementation guide
└── 📖 CLAUDE.md                        # Development guidelines
```

---

## 🏗️ Architecture Overview

### **System Components**

#### **🎮 Main Application (`main.py`)**
- Rich console interface with interactive menus
- Customer creation workflow orchestration
- Real-time SMS verification monitoring
- Configuration management integration

#### **🗄️ Database Layer (`src/customer_db.py`)**
- SQLite database with JSON fallback
- Customer record management with analytics
- Geographic data processing and validation
- Export functionality for multiple formats

#### **🔌 API Integration Managers**
- **DaisySMS**: Phone verification lifecycle management
- **Mail.tm**: Temporary email account creation with domain caching
- **MapQuest**: Address generation, validation, and geocoding

#### **📡 Real-time Monitoring (`src/sms_monitor.py`)**
- Multi-verification tracking with Rich table display
- Live status updates and progress indicators
- Automatic code detection and clipboard integration

---

## 🌐 Web Application Ready

This desktop application is **designed for easy web conversion**. See our comprehensive [**Web Application Conversion Guide**](WEB_APPLICATION_CONVERSION_GUIDE.md) for:

- **📋 Complete conversion strategy** (FastAPI + React)
- **🏗️ Architecture mapping** (Desktop → Web components)
- **⚡ Real-time features** (WebSocket implementation)
- **📊 Technology stack recommendations**
- **🎯 10-week implementation timeline**

### **Key Conversion Benefits**
- ✅ **Multi-user Support**: Handle concurrent users
- ✅ **Cross-platform Access**: Browser-based interface
- ✅ **Real-time Updates**: WebSocket-powered live monitoring
- ✅ **Modern UI**: React-based interactive interface
- ✅ **API-First Design**: RESTful backend with OpenAPI docs

---

## 🔐 Security Features

### **Environment Variable Security**
All sensitive data is managed through environment variables:
- ✅ **No hardcoded API keys** in source code
- ✅ **Git-ignored `.env` files** protect credentials
- ✅ **Template-based setup** with `.env.example`
- ✅ **Fallback support** for system environment variables

### **Security Improvements Implemented**
- **🔒 100% credential protection** - All API keys moved to environment variables
- **🛡️ Git security** - Enhanced `.gitignore` prevents accidental commits
- **📋 Developer templates** - `.env.example` provides safe setup guide
- **⚙️ Configuration management** - Enhanced config manager with 40+ environment variables

See [**SECURITY_SETUP.md**](SECURITY_SETUP.md) for complete security implementation details.

---

## 🧪 Testing & Quality

### **Comprehensive Test Suite**
```bash
# Run all tests
python test_comprehensive_functionality.py

# Individual component tests
python test_database_integrity.py      # Database operations
python test_api_endpoints.py           # API integrations
python test_performance_validation.py  # Performance benchmarks
```

### **Test Coverage**
- ✅ **Unit Tests**: Individual component validation
- ✅ **Integration Tests**: Full workflow testing
- ✅ **Performance Tests**: Benchmark validation
- ✅ **Database Tests**: Data integrity verification

---

## 📊 Usage Examples

### **Customer Creation**
```python
# Example customer creation workflow
customer = CustomerRecord(
    full_name="John Doe",
    email="john.doe@temp-mail.com",
    primary_phone="+1234567890",
    address="123 Main St, City, State 12345"
)
```

### **SMS Verification Monitoring**
```python
# Real-time SMS monitoring
monitor = SMSMonitor()
monitor.add_verification(phone_number, verification_id)
monitor.start_monitoring()  # Live console updates
```

### **Database Analytics**
```python
# Generate customer analytics
analytics = db.generate_analytics()
print(f"Total customers: {analytics['total_customers']}")
print(f"Verification rate: {analytics['verification_success_rate']}")
```

---

## ⚙️ Configuration

### **Environment Variables**
Key environment variables (see `.env.example` for complete list):
```bash
# API Credentials
DAISYSMS_API_KEY=your_daisysms_key
MAPQUEST_API_KEY=your_mapquest_key
MAILTM_DEFAULT_PASSWORD=secure_password

# Database Configuration
DATABASE_PATH=data/customers.db
BACKUP_ENABLED=true
BACKUP_INTERVAL_HOURS=24

# Performance Settings
SMS_POLLING_INTERVAL=3
MAX_CONCURRENT_VERIFICATIONS=5
REQUEST_TIMEOUT=30
```

---

## 🔧 Development

### **Setup Development Environment**
```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync

# Run in development mode
python main.py
```

### **Adding New Features**
1. Follow the existing patterns in `src/` modules
2. Add tests in `test_*.py` files
3. Update configuration in `config.ini` and environment variables
4. Document changes in `CLAUDE.md`

### **Key Development Files**
- **`CLAUDE.md`**: Complete development guidelines and commands
- **`pyproject.toml`**: Dependencies and project metadata
- **`config.ini`**: Application configuration structure

---

## 🚨 Troubleshooting

### **Common Issues**

#### **API Connection Errors**
```bash
# Test DaisySMS connection
python -c "from src.daisy_sms import DaisySMSManager; # test connection"

# Verify environment variables loaded
python -c "import os; print('DAISYSMS_API_KEY' in os.environ)"
```

#### **Database Issues**
```bash
# Run database integrity test
python test_database_integrity.py

# Backup and restore database
python -c "from src.customer_db import CustomerDatabase; db.backup_database()"
```

#### **Environment Setup**
```bash
# Verify UV installation
uv --version

# Reinstall dependencies
uv sync --force

# Check Python version
python --version  # Requires 3.8+
```

### **Getting Help**
1. **Configuration Issues**: Check `config.ini` format and required sections
2. **API Problems**: Verify API keys and account balances
3. **Database Errors**: Use backup/restore functionality
4. **Development Questions**: See `CLAUDE.md` for detailed guidance

---

## 📈 Performance Metrics

### **System Capabilities**
- **⚡ SMS Verification**: 30-180 seconds per customer (API dependent)
- **🗄️ Database Operations**: Optimized for batch processing
- **🌐 API Rate Limits**: Compliant with all service providers
- **💾 Storage**: Efficient SQLite with JSON backup system

### **Benchmarks**
- **Customer Creation**: ~5-10 seconds per customer
- **Database Queries**: <100ms for standard operations
- **SMS Monitoring**: Real-time updates with 3-second polling
- **Export Operations**: 1000+ customers in <5 seconds

---

## 🤝 Contributing

### **Development Workflow**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Set up local `.env` with your API keys
4. Make changes and add tests
5. Run test suite: `python test_comprehensive_functionality.py`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### **Code Style**
- Follow existing patterns and conventions
- Add docstrings to new functions and classes
- Include type hints where appropriate
- Maintain security best practices (no hardcoded secrets)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **DaisySMS** - SMS verification services
- **Mail.tm** - Temporary email services
- **MapQuest** - Address validation and geocoding
- **Rich** - Beautiful terminal formatting
- **FastAPI** - Recommended for web conversion
- **UV** - Modern Python package management

---

## 📞 Support

For support and questions:
- 📖 **Documentation**: Check `CLAUDE.md` for detailed guidance
- 🐛 **Issues**: Open an issue on GitHub
- 🔐 **Security**: See `SECURITY_SETUP.md` for security implementation
- 🌐 **Web Conversion**: See `WEB_APPLICATION_CONVERSION_GUIDE.md` for conversion strategy

---

**CustomerDaisy - Comprehensive Customer Creation with Real-time SMS Verification 🌼**