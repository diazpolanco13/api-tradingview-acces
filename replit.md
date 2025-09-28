# Overview

This project is a RESTful API service for managing TradingView script access management. It's designed for vendors to manage user access to their TradingView publications programmatically. The API provides endpoints for username validation, checking current access levels, and modifying user permissions for TradingView Pine scripts.

The service requires a Premium TradingView subscription to function properly and is intended to be deployed on Replit with appropriate security measures.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Framework
- **Flask**: Lightweight web framework providing RESTful API endpoints
- **Python**: Core language for all backend logic and TradingView integration

## Authentication & Security
- **Admin Token Authentication**: Secure admin panel access using environment-based token authentication
- **Session Management**: TradingView session cookie management stored in Replit database
- **Header-based Security**: Admin operations require X-Admin-Token header (never query parameters)

## Data Storage
- **Replit Database**: Simple key-value store for persisting TradingView session cookies
- **Environment Variables**: Configuration storage for credentials and admin tokens

## External Integration
- **TradingView API**: Custom integration with TradingView's internal endpoints for:
  - Username validation (`username_hint`)
  - User access management (`pine_perm` endpoints)
  - Account balance checking (`tvcoins`)
  - Session authentication (`accounts/signin`)

## Core Components

### Session Management (`tradingview.py`)
Handles TradingView authentication by managing session cookies stored in the database. Automatically validates stored cookies and provides fallback error handling when manual cookie updates are required.

### API Endpoints (`server.py`)
- **Public Endpoint**: `/validate/<username>` - Username validation without authentication
- **Protected Endpoints**: All access management operations require admin token
- **Admin Panel**: Web interface for cookie management and system administration

### Configuration (`config.py`)
Centralized URL configuration for all TradingView API endpoints, making the system maintainable and allowing for easy endpoint updates.

### Helper Functions (`helper.py`)
Date manipulation utilities for extending user access periods using relativedelta for accurate calendar arithmetic.

## Deployment Architecture
- **Replit Platform**: Cloud hosting with built-in database and environment management
- **Auto-scaling**: Replit handles server scaling and availability
- **Environment Configuration**: Simple setup requiring only TradingView credentials

## Security Considerations
- Admin token generation with secure random values
- Session cookie validation and automatic refresh detection
- Protected admin endpoints with proper authentication headers
- Error handling that doesn't expose sensitive information

# Recent Updates

## September 28, 2025 - Web Navigation System Implemented
- **Session-Based Authentication**: Implemented Flask session authentication alongside existing token system
- **Web Routes**: Added navigable routes (/dashboard, /clients, /indicators, /access) with automatic login protection
- **Unified Authentication**: APIs now accept both session cookies and token headers for maximum flexibility
- **Complete Templates**: Full HTML interfaces for all administrative functions with responsive design
- **Seamless Navigation**: After login, users can navigate directly between sections without re-authentication
- **Security Improvements**: Protected routes automatically redirect to login with return URLs
- **Production Ready**: All authentication flows tested and verified working

## September 28, 2025 - Replit Environment Setup Completed
- **Production Ready**: Successfully imported from GitHub and configured for Replit environment
- **Poetry Dependencies**: All Python packages installed via Poetry (Flask, requests, urllib3, python-dateutil)
- **Flask Server**: Properly configured for Replit proxy with 0.0.0.0:5000 binding
- **Admin Panel**: Fully functional web interface with token authentication
- **API Endpoints**: All REST endpoints tested and working (/validate/, /access/)
- **Deployment Configuration**: VM deployment configured for production
- **Data Directory**: Created for cookie storage with proper file permissions
- **Workflow Configuration**: Optimized Poetry-based Flask server startup

## December 27, 2025 - Panel de Administración Implementado
- **Panel Web Seguro**: Interfaz web completa para gestionar cookies de TradingView con autenticación por token
- **Información de Perfil**: Sistema obtiene automáticamente imagen de perfil, username, balance y estado de partner
- **Seguridad Robusta**: Autenticación por token X-Admin-Token con generación automática de tokens seguros
- **Detección de Expiración**: Verificación automática del estado de cookies con notificaciones en tiempo real
- **Frontend Completo**: Panel administrativo profesional con login seguro y gestión de cookies

## Funcionalidades del Panel
- **Login Seguro**: Requiere token de administrador antes del acceso
- **Estado en Tiempo Real**: Muestra balance, username, imagen de perfil y estado de partner
- **Gestión de Cookies**: Actualización manual cuando sea necesario con validación automática
- **API Protegida**: Todos los endpoints administrativos requieren autenticación por header

# External Dependencies

## Core Web Framework
- **Flask**: Web application framework for API endpoints and admin panel
- **Werkzeug**: WSGI utilities and HTTP request/response handling

## TradingView Integration
- **requests**: HTTP client for TradingView API communication
- **urllib3**: Lower-level HTTP utilities for multipart form encoding

## Date & Time Processing
- **python-dateutil**: Advanced date parsing and relativedelta calculations for access period extensions

## Hosting Platform
- **Replit**: Cloud hosting platform providing:
  - Built-in key-value database
  - Environment variable management
  - Automatic HTTPS and domain provisioning
  - Zero-configuration deployment

## Authentication & Security
- **secrets**: Cryptographically secure random token generation for admin authentication