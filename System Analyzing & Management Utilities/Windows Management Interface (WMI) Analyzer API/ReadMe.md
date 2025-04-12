# WMI API Documentation

## Overview

The Windows Management Instrumentation (WMI) API is a Flask-based web service that provides programmatic access to Windows system information and management capabilities through WMI. This API allows authorized users to query system information, manage services, monitor processes, and perform various administrative tasks on Windows systems.

## Features

- **System Information Collection**: Gather detailed information about hardware, software, network configuration, processes, services, and more
- **Service Management**: Start, stop, restart, and configure Windows services
- **Process Management**: List running processes and terminate them
- **User Authentication**: Role-based access control with JWT tokens and API keys
- **Comprehensive Logging**: Detailed request/response logging for auditing and troubleshooting
- **Rate Limiting**: Protection against excessive API usage
- **Database Integration**: SQLite database for user management and request tracking

## Prerequisites

Before using this API, ensure you have the following:

1. **Python 3.7+** installed
2. **Windows operating system** (WMI is Windows-specific)
3. **Administrative privileges** for certain operations
4. Required Python packages (install via `pip install -r requirements.txt`):
   ```
   flask
   flask-cors
   pyjwt
   wmi
   pywin32
   werkzeug
   ```

## Installation

1. Clone or download the repository containing the script
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The API can be configured through environment variables or by modifying the `Config` class in the script:

| Setting | Description | Default Value |
|---------|-------------|---------------|
| `SECRET_KEY` | Flask secret key for session security | Randomly generated 32-byte hex string |
| `JWT_SECRET_KEY` | Secret key for JWT token generation | Randomly generated 32-byte hex string |
| `JWT_ACCESS_TOKEN_EXPIRES` | JWT token expiration time in seconds | 3600 (1 hour) |
| `RATE_LIMIT_WINDOW` | Rate limit window in seconds | 60 (1 minute) |
| `RATE_LIMIT_MAX_REQUESTS` | Maximum requests per rate limit window | 60 |
| `DATABASE_PATH` | Path to SQLite database file | `wmi_api.db` in current directory |
| `LOG_PATH` | Directory for log files | `logs` in current directory |
| `CORS_ORIGINS` | Allowed CORS origins | `['http://localhost:3000', 'http://127.0.0.1:5000']` |

## Usage

### Starting the API Server

Run the script directly:

```bash
python wmi_api.py
```

Optional command-line arguments:
- `--host`: Host to bind to (default: 127.0.0.1)
- `--port`: Port to listen on (default: 5000)
- `--debug`: Enable debug mode

Example:
```bash
python wmi_api.py --host 0.0.0.0 --port 8080 --debug
```

### Initial Setup

On first run:
1. The database will be initialized with an admin user
2. An API key will be generated for the admin user
3. These credentials will be printed to the console

### Authentication

The API supports two authentication methods:

1. **JWT Token Authentication** (for interactive users):
   - Login at `/api/auth/login` with username/password
   - Use the returned token in the `Authorization: Bearer <token>` header

2. **API Key Authentication** (for programmatic access):
   - Include the API key in either:
     - `X-API-Key` header
     - `api_key` query parameter

### API Endpoints

#### Authentication

- **POST /api/auth/login**
  - Authenticate and receive a JWT token
  - Required JSON body: `{"username": "...", "password": "..."}`
  
- **POST /api/auth/register** (admin only)
  - Register a new user
  - Required JSON body: `{"username": "...", "password": "...", "email": "...", "role": "..."}`
  
- **POST /api/auth/reset-api-key**
  - Reset your API key

#### System Information

- **GET /api/wmi/system**
  - Get basic system information (OS, BIOS, computer system details)
  
- **GET /api/wmi/hardware**
  - Get hardware information (CPU, memory, disks, network adapters)
  
- **GET /api/wmi/processes**
  - Get list of running processes
  
- **DELETE /api/wmi/processes/<int:process_id>** (admin only)
  - Terminate a process by ID

#### Service Management

- **GET /api/wmi/services**
  - Get list of all services
  
- **POST /api/wmi/services/<service_name>/start** (admin only)
  - Start a service
  
- **POST /api/wmi/services/<service_name>/stop** (admin only)
  - Stop a service
  
- **POST /api/wmi/services/<service_name>/restart** (admin only)
  - Restart a service
  
- **PUT /api/wmi/services/<service_name>/startup** (admin only)
  - Change service startup mode
  - Required JSON body: `{"start_mode": "Auto|Manual|Disabled"}`

#### Custom Data Collection

- **POST /api/wmi/collect**
  - Collect specific WMI information
  - Required JSON body: `{"categories": ["system", "hardware", ...]}`
  
- **GET /api/wmi/collect-all** (admin only)
  - Collect all available WMI information

#### User Management (admin only)

- **GET /api/users**
  - List all users
  
- **DELETE /api/users/<int:user_id>**
  - Delete a user
  
- **PUT /api/users/<int:user_id>/role**
  - Update user role
  - Required JSON body: `{"role": "admin|user|readonly"}`

#### Utility

- **GET /api/health**
  - Health check endpoint
  
- **POST /api/shutdown** (admin only)
  - Gracefully shutdown the server

## Example Usage

### 1. Authenticating and Getting System Info

```bash
# Login to get JWT token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<admin-password>"}'

# Use token to get system info
curl http://localhost:5000/api/wmi/system \
  -H "Authorization: Bearer <token>"
```

### 2. Using API Key to Get Hardware Info

```bash
curl http://localhost:5000/api/wmi/hardware \
  -H "X-API-Key: <api-key>"
```

### 3. Managing Services

```bash
# Get list of services
curl http://localhost:5000/api/wmi/services \
  -H "X-API-Key: <api-key>"

# Restart a service (requires admin privileges)
curl -X POST http://localhost:5000/api/wmi/services/Spooler/restart \
  -H "X-API-Key: <admin-api-key>"
```

### 4. Custom Data Collection

```bash
# Collect specific information
curl -X POST http://localhost:5000/api/wmi/collect \
  -H "X-API-Key: <api-key>" \
  -H "Content-Type: application/json" \
  -d '{"categories": ["system", "network"]}'
```

## Security Considerations

1. **Run as Administrator**: Some WMI operations require administrative privileges
2. **Secure Storage**: Keep API keys and JWT tokens secure
3. **HTTPS**: Always use HTTPS in production environments
4. **Rate Limiting**: The API enforces rate limiting (60 requests/minute by default)
5. **Input Validation**: All input is sanitized to prevent injection attacks

## Logging

The API maintains detailed logs in the `logs` directory:
- `wmi_api.log`: API request/response logs
- `wmi_info_<timestamp>.log`: WMI operation logs

## Database Schema

The SQLite database contains the following tables:

1. **users**:
   - id, username, password_hash, email, role, api_key, created_at

2. **request_logs**:
   - id, user_id, endpoint, method, status_code, ip_address, request_time

3. **rate_limits**:
   - id, user_id, ip_address, request_count, window_start

## Error Handling

The API returns appropriate HTTP status codes with JSON error messages:

- 400: Bad request (invalid input)
- 401: Unauthorized (authentication failed)
- 403: Forbidden (insufficient permissions)
- 404: Not found
- 429: Too many requests (rate limit exceeded)
- 500: Internal server error

## Troubleshooting

1. **WMI Connection Issues**:
   - Ensure WMI service is running (`winmgmt`)
   - Verify you have administrative privileges
   - Check Windows Firewall settings

2. **Database Issues**:
   - Delete the database file to reset (loses all user data)
   - Verify write permissions in the working directory

3. **Authentication Problems**:
   - Check the logs for detailed error messages
   - Verify the admin credentials printed during first run

## License

This project is provided as-is without warranty. Use at your own risk in production environments.

## Support

For issues or feature requests, please contact the maintainers or open an issue in the repository.

---

This documentation provides comprehensive information about the WMI API's functionality, setup, and usage. The API offers powerful Windows management capabilities through a secure, well-structured web interface suitable for both interactive and programmatic use.