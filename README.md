# SchematicShop

**Private Repository** - A cloud-native, highly scalable web application for hosting Minecraft schematic and litematica files. Built with modern microservices architecture, featuring automatic virus scanning, file validation, and a sleek, stylized UI.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Django](https://img.shields.io/badge/django-4.2-green.svg)
![Next.js](https://img.shields.io/badge/next.js-14.0-black.svg)

## 🚀 Features

### Core Functionality
- **File Upload & Validation**: Upload Minecraft schematics with comprehensive validation
  - Supported formats: `.schematic`, `.schem`, `.litematic`, `.nbt`
  - File size limits and type validation
  - Automatic virus scanning with ClamAV
  - SHA-256 hash verification for duplicate detection

- **User Management**: Secure authentication and user profiles
  - JWT-based authentication
  - User storage quotas and usage tracking
  - Profile customization with avatars and bios

- **Search & Discovery**: Powerful search and filtering capabilities
  - Full-text search across titles, descriptions, and tags
  - Category-based filtering
  - Trending and popular schematics
  - Tag-based organization

- **Social Features**:
  - Like and favorite schematics
  - Comments and discussions
  - User profiles and activity feeds
  - Download and view counters

### Technical Features
- **Cloud-Native Architecture**: Built for scalability
  - Microservices-ready Django backend
  - Object storage (S3/MinIO) for file storage
  - Redis for caching and rate limiting
  - PostgreSQL for metadata storage
  - Celery for asynchronous task processing

- **Security & Performance**:
  - Automatic virus scanning on upload
  - Rate limiting to prevent abuse
  - CDN-ready for global content delivery
  - CORS configuration for secure API access
  - Environment-based configuration

- **Modern UI/UX**:
  - Sleek, Stripe/Dribbble-inspired design
  - Responsive layout for all devices
  - Smooth animations with Framer Motion
  - Real-time upload progress tracking
  - 3D preview capabilities (coming soon)

## 🏗️ Architecture

### Backend (Django + DRF)
```
backend/
├── schematicshop/          # Main project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # URL routing
│   ├── celery.py           # Celery configuration
│   └── wsgi.py             # WSGI application
├── apps/
│   ├── users/              # User management
│   ├── schematics/         # Schematic CRUD operations
│   ├── storage/            # Storage backends
│   └── scanning/           # Virus scanning
└── manage.py
```

### Frontend (Next.js + React)
```
frontend/
├── src/
│   ├── pages/              # Next.js pages
│   ├── components/         # React components
│   ├── lib/                # Utilities and API client
│   └── styles/             # Global styles
├── public/                 # Static assets
└── package.json
```

### Infrastructure
- **PostgreSQL**: Relational database for metadata
- **Redis**: Caching and task queue
- **MinIO/S3**: Object storage for files
- **ClamAV**: Virus scanning
- **Docker**: Containerization
- **Docker Compose**: Local development orchestration

## 📋 Prerequisites

- Docker and Docker Compose (recommended)
- OR:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 15+
  - Redis 7+
  - MinIO or S3-compatible storage
  - ClamAV (optional, for virus scanning)

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**:
```bash
git clone https://github.com/aomarai/schematicshop.git
cd schematicshop
```

2. **Start all services**:
```bash
docker-compose up -d
```

This will start:
- Backend API on http://localhost:8000
- Frontend on http://localhost:3000
- PostgreSQL on localhost:5432
- Redis on localhost:6379
- MinIO on http://localhost:9000 (console: http://localhost:9001)
- ClamAV on localhost:3310

3. **Run migrations**:
```bash
docker-compose exec backend python manage.py migrate
```

4. **Create a superuser**:
```bash
docker-compose exec backend python manage.py createsuperuser
```

5. **Access the application**:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- Admin: http://localhost:8000/admin
- API Docs: http://localhost:8000/api/docs/

### Manual Setup

#### Backend Setup

1. **Create virtual environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r ../requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run migrations**:
```bash
python manage.py migrate
```

5. **Create superuser**:
```bash
python manage.py createsuperuser
```

6. **Start development server**:
```bash
python manage.py runserver
```

7. **Start Celery worker** (in another terminal):
```bash
celery -A schematicshop worker -l info
```

#### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Configure environment**:
```bash
cp .env.example .env.local
# Edit .env.local with your API URL
```

3. **Start development server**:
```bash
npm run dev
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Django
DEBUG=1
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=*

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Object Storage
USE_S3=1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=schematics
AWS_S3_ENDPOINT_URL=http://localhost:9000

# ClamAV
CLAMAV_ENABLED=1
CLAMAV_HOST=localhost
CLAMAV_PORT=3310

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/docs/
- OpenAPI Schema: http://localhost:8000/api/schema/

### Key Endpoints

#### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/me/` - Get current user profile

#### Schematics
- `GET /api/schematics/` - List schematics
- `POST /api/schematics/` - Upload schematic
- `GET /api/schematics/{id}/` - Get schematic details
- `PUT /api/schematics/{id}/` - Update schematic
- `DELETE /api/schematics/{id}/` - Delete schematic
- `POST /api/schematics/{id}/download/` - Download schematic
- `POST /api/schematics/{id}/like/` - Like schematic
- `GET /api/schematics/trending/` - Get trending schematics

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚢 Deployment

### Docker Production Build

1. **Build images**:
```bash
docker-compose -f docker-compose.prod.yml build
```

2. **Deploy to your infrastructure** (Kubernetes, AWS ECS, etc.)

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (to be created based on your cloud provider).

## 🔒 Security

- **Authentication**: JWT-based authentication with refresh tokens
- **File Validation**: Extension and MIME type validation
- **Virus Scanning**: Automatic ClamAV scanning on upload
- **Rate Limiting**: Protection against abuse
- **CORS**: Configured for secure cross-origin requests
- **HTTPS**: Recommended for production (configure in reverse proxy)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Django](https://www.djangoproject.com/) and [Django REST Framework](https://www.django-rest-framework.org/)
- Frontend powered by [Next.js](https://nextjs.org/) and [React](https://react.dev/)
- UI inspired by [Stripe](https://stripe.com/) and [Dribbble](https://dribbble.com/)
- Icons from [Lucide](https://lucide.dev/)
- Animations with [Framer Motion](https://www.framer.com/motion/)

## 📧 Support

For support, email support@schematicshop.example or open an issue in the GitHub repository.

## 🗺️ Roadmap

- [ ] 3D schematic preview in browser
- [ ] Advanced search filters (dimensions, block types)
- [ ] Collections and playlists
- [ ] User follow system
- [ ] API rate limiting tiers
- [ ] Premium storage plans
- [ ] Mobile app (React Native)
- [ ] In-browser schematic editor
- [ ] AI-powered schematic recommendations
- [ ] Community forums