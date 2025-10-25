# LOB Data API - FastAPI Crypto Data Service

A production-ready **FastAPI** service for accessing **Limit Order Book (LOB) data** from Binance with advanced user management, authentication, and real-time cryptocurrency data processing.

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![ClickHouse](https://img.shields.io/badge/ClickHouse-FFCC01?style=for-the-badge&logo=clickhouse&logoColor=black)

## 🚀 Features

### 🔐 Authentication & Authorization
- **JWT-based authentication** with secure token management
- **Role-based access control** (Admin/User roles)
- **Secure password hashing** using PBKDF2
- **User registration** with secret key protection
- **Token expiration** and validation

### 📊 Crypto Data Processing
- **Real-time cryptocurrency data** from Binance LOB (Limit Order Book)
- **Symbol availability** filtering for active trading pairs
- **Historical data access** with configurable limits
- **High-performance queries** using ClickHouse
- **Data aggregation** and filtering capabilities

### 👥 User Management
- **Admin dashboard** for user management
- **Role management** (promote/demote users)
- **User activity tracking** and deactivation
- **API usage monitoring** with detailed logs

### 🛡️ Security & Monitoring
- **Request logging middleware** for all API calls
- **API usage analytics** and statistics
- **IP tracking** and user agent logging
- **Automatic token validation**
- **Secure secret management** with environment variables

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │◄──►│   SQLite DB      │    │   ClickHouse    │
│   (Docker)      │    │   (Users/Logs)   │    │   (Crypto Data) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌────────┴────────┐              │
         └─────────────►│  API Logging    │◄─────────────┘
                        │  & Analytics    │
                        └─────────────────┘
```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend Framework** | FastAPI | High-performance API with automatic docs |
| **Database** | SQLite | User management and application data |
| **Analytics DB** | ClickHouse | High-performance crypto data storage |
| **Authentication** | JWT Tokens | Secure user authentication |
| **Password Hashing** | PBKDF2 | Secure password storage |
| **Containerization** | Docker | Consistent deployment environment |
| **API Documentation** | Swagger UI | Interactive API documentation |

## 📦 Installation & Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- ClickHouse database (external)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/lob-api.git
   cd lob-api
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # Application Settings
   SECRET_KEY=your-super-secure-jwt-secret-key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REGISTRATION_ENABLED=True
   REGISTRATION_SECRET=your-registration-secret
   ADMIN_SECRET=your-admin-secret

   # ClickHouse Database
   CLICKHOUSE_HOST=your-clickhouse-server.com
   CLICKHOUSE_PORT=8123
   CLICKHOUSE_USER=default
   CLICKHOUSE_PASSWORD=your-password
   CLICKHOUSE_DATABASE=cryptodata
   ```

3. **Build and start the service**
   ```bash
   docker-compose up -d --build
   ```

4. **Verify the service is running**
   ```bash
   curl http://localhost:8000/health
   ```

### Manual Installation (Development)

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate  # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export SECRET_KEY="your-secret-key"
   export CLICKHOUSE_HOST="your-host"
   # ... set other variables
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT token signing key | **Required** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `REGISTRATION_ENABLED` | Enable user registration | False |
| `REGISTRATION_SECRET` | Secret key for registration | **Required if enabled** |
| `ADMIN_SECRET` | Secret key for admin creation | **Required** |
| `CLICKHOUSE_HOST` | ClickHouse server host | **Required** |
| `CLICKHOUSE_USER` | ClickHouse username | default |
| `CLICKHOUSE_PASSWORD` | ClickHouse password | **Required** |
| `CLICKHOUSE_DATABASE` | ClickHouse database name | cryptodata |

## 📚 API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/token` | Get JWT access token |
| `POST` | `/auth/register` | Register new user |
| `GET` | `/auth/me` | Get current user info |

#### Crypto Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/crypto/symbols` | Get available trading symbols |
| `GET` | `/crypto/data/{symbol}` | Get symbol data with pagination |

#### Administration
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| `GET` | `/admin/users` | List all users | Admin |
| `PUT` | `/admin/users/{id}/role` | Update user role | Admin |
| `GET` | `/admin/logs` | View API logs | Admin |
| `GET` | `/admin/stats` | System statistics | Admin |

## 🎯 Usage Examples

### 1. User Registration
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "X-Registration-Secret: your-registration-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### 2. Get Access Token
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securepassword123"
```

### 3. Access Crypto Data
```bash
curl -X GET "http://localhost:8000/crypto/symbols" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 4. Admin - Get System Stats
```bash
curl -X GET "http://localhost:8000/admin/stats" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

## 📁 Project Structure

```
lob-api/
├── app/
│   ├── api/
│   │   └── endpoints/          # API route handlers
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── admin.py       # Admin management endpoints
│   │       └── crypto.py      # Crypto data endpoints
│   ├── core/                  # Core application configuration
│   │   ├── config.py          # Settings and environment
│   │   └── security.py        # Auth utilities
│   ├── db/                    # Database layer
│   │   ├── models/            # SQLAlchemy models
│   │   └── clickhouse.py      # ClickHouse client
│   ├── middleware/            # Custom middleware
│   │   └── logging.py         # Request logging
│   ├── models/                # Pydantic models
│   │   ├── user.py            # User schemas
│   │   └── token.py           # Token schemas
│   ├── repositories/          # Data access layer
│   │   └── crypto_repository.py
│   ├── services/              # Business logic
│   │   ├── auth.py            # Authentication service
│   │   ├── user_service.py    # User management
│   │   └── crypto_service.py  # Crypto data processing
│   └── main.py               # FastAPI application
├── data/                     # SQLite database storage
├── logs/                     # Application logs
├── docker-compose.yml        # Docker composition
├── Dockerfile               # Container definition
├── requirements.txt         # Python dependencies
└── run.py                  # Application entry point
```

## 🔒 Security Features

- **JWT Authentication** with configurable expiration
- **Password Hashing** using industry-standard PBKDF2
- **Role-based Access Control** (RBAC)
- **Request Logging** for security auditing
- **Environment-based Secrets** management
- **CORS Protection** with configurable origins
- **Input Validation** using Pydantic models

## 📊 Performance Optimizations

- **Async/Await** throughout the application
- **Connection Pooling** for ClickHouse
- **Efficient Query Building** for large datasets
- **Structured Logging** with configurable levels
- **Docker Optimization** with layered builds

## 🐳 Docker Deployment

### Production Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose logs -f lob-api

# Scale services
docker-compose up -d --scale lob-api=3
```

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/db-status

# ClickHouse status
curl http://localhost:8000/clickhouse-health
```

## 📈 Monitoring & Logs

### Access Logs
```bash
# Docker logs
docker-compose logs -f lob-api

# Application logs
tail -f logs/app.log
```

### API Metrics
The admin dashboard provides:
- User activity statistics
- API endpoint usage
- System performance metrics
- Error rates and monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---

**Built with ❤️ using FastAPI, Docker, and ClickHouse**

*This project demonstrates enterprise-grade API development with proper authentication, authorization, and data processing capabilities.*
