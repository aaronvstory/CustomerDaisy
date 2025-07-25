# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CustomerDaisy is a customer creation system that integrates with DaisySMS for phone verification, Mail.tm for email creation, and MapQuest for real address generation. The system provides a rich console interface for creating and managing customer profiles with SMS verification capabilities.

## Development Commands

### Setup and Launch
- **Initial Setup**: `setup.bat` - Sets up UV environment and installs dependencies
- **Launch Application**: `launch.bat` - Starts the main application with environment setup
- **Direct Python Launch**: `python main.py` - Direct execution (requires manual env setup)

### Testing
- **Run All Tests**: `python test_comprehensive_functionality.py` - Comprehensive functionality tests
- **Database Tests**: `python test_database_integrity.py` - Database integrity tests  
- **API Tests**: `python test_api_endpoints.py` - API endpoint validation
- **Performance Tests**: `python test_performance_validation.py` - Performance benchmarks
- **Individual Tests**: `python test_<component>.py` - Component-specific tests
- **Test Location**: All tests are in `archive/tests/` directory

### Dependencies
- **Install/Update Dependencies**: `uv sync` - Manages project dependencies via pyproject.toml
- **Add New Dependency**: `uv add <package>` - Add package to project
- **Python Version**: Requires Python >= 3.8
- **Key Dependencies**: rich (terminal UI), faker (data generation), requests (API calls), questionary (interactive menus)

## Architecture Overview

### Core Components

**Main Application (`main.py`)**
- `CustomerDaisyApp` - Main application class with menu system
- Rich console interface with banners, tables, and interactive prompts
- Configuration management integration
- Error handling and logging setup

**Database Layer (`src/customer_db.py`)**
- `CustomerDatabase` - SQLite database management with JSON fallback
- `CustomerRecord` - Data class for customer representation
- Analytics generation and export functionality
- Address validation and geographic analytics

**API Integrations**
- `DaisySMSManager` (`src/daisy_sms.py`) - DaisySMS API for phone verification
- `MailTmManager` (`src/mail_tm.py`) - Mail.tm API for email creation
- `MapQuestAddressManager` (`src/mapquest_address.py`) - Real address generation and validation

**Monitoring and Configuration**
- `SMSMonitor` (`src/sms_monitor.py`) - Real-time SMS code monitoring
- `ConfigManager` (`src/config_manager.py`) - Configuration file management

### Data Flow

1. **Customer Creation**: Generate personal data → Create email account → Rent phone number → Save to database
2. **SMS Verification**: Monitor DaisySMS API → Receive codes → Update customer records → Log activities
3. **Address Processing**: MapQuest API validation → Geographic data enrichment → Analytics generation

### Configuration Structure

Configuration is managed through `config.ini` with sections:
- `DAISYSMS` - API credentials and service settings
- `MAPQUEST` - Address validation API settings  
- `MAILTM` - Email service configuration
- `DATABASE` - Data storage and backup settings
- `CUSTOMER_GENERATION` - Faker data generation preferences
- `LOGGING`, `PERFORMANCE`, `UI`, `NOTIFICATIONS` - Application settings

## Development Guidelines

### Error Handling
- Use rich console for user-friendly error messages
- Log exceptions with full tracebacks to log files
- Implement graceful degradation when APIs are unavailable
- Validate API keys and connection status before operations

### API Integration Patterns
- All API managers use session-based requests with timeouts
- Implement caching for frequently accessed data (balance, domain lists)
- Rate limiting compliance (DaisySMS: 1 request per 3 seconds)
- Retry logic with exponential backoff for transient failures

### Database Operations
- SQLite as primary storage with JSON backup/export capabilities
- Atomic transactions for customer operations
- Analytics generation from stored data
- Export functionality for CSV, JSON, and TXT formats

### Testing Strategy
- Component-level unit tests for each manager class
- Integration tests for full customer creation workflows
- Performance validation for bulk operations
- Database integrity checks and migration testing

### UI/UX Patterns
- Rich library for beautiful console interfaces
- Banner-based information display with color coding
- Interactive prompts with validation and choices
- Progress indicators for long-running operations
- Graceful fallbacks when Rich is unavailable

## Common Issues and Solutions

### API Configuration
- **DaisySMS errors**: Check API key validity and account balance
- **MapQuest failures**: Verify API key and quota limits
- **Mail.tm issues**: Domain availability and rate limiting

### Database Issues
- **SQLite locks**: Ensure proper connection closing
- **Data integrity**: Use backup/restore functionality
- **Performance**: Index optimization for search operations

### Development Environment
- **UV dependency issues**: Use `uv sync` to rebuild environment
- **Import errors**: Ensure `src/` is in Python path for tests
- **Configuration issues**: Validate `config.ini` format and required sections
- **Windows-specific**: Uses `.bat` files for setup and launch; ensure Windows environment for full compatibility

## Key Files to Understand

- `main.py` - Application entry point and user interface
- `src/customer_db.py` - Data persistence and analytics
- `src/daisy_sms.py` - Phone verification implementation
- `src/sms_monitor.py` - Real-time SMS monitoring with queue management
- `config.ini` - Application configuration (contains API keys)
- `pyproject.toml` - Dependency management and project metadata
- `setup.bat` / `launch.bat` - Windows batch files for environment setup and application launch

## Performance Considerations

- SMS verification can take 30-180 seconds per customer
- MapQuest API has rate limits - implement caching for repeated lookups  
- Database operations are optimized for batch processing
- Rich console rendering may impact performance in resource-constrained environments
- Log file rotation configured to prevent disk space issues