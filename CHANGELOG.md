# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2026-01-15

### Fixed
- Added missing Django database migrations for all apps (users, schematics, scanning, storage)
- Fixed Django settings to use sensible defaults (USE_S3=False, CLAMAV_ENABLED=False) for development/testing
- Updated CI/CD pipeline configuration to properly run tests with environment variables
- Removed package-lock.json dependency from frontend CI/CD workflow
- Updated .env.example to reflect new default configuration values

### Changed
- AWS credentials now have defaults in settings.py to allow easier development setup
- ClamAV is now disabled by default for development environments
- S3 storage is now disabled by default for development environments

## [1.0.1] - 2026-01-15

### Security
- **CRITICAL**: Updated axios from 1.6.2 to 1.12.0 to fix multiple vulnerabilities:
  - DoS attack through lack of data size check
  - SSRF and credential leakage via absolute URL
  - Server-Side Request Forgery in Server Actions
- **CRITICAL**: Updated Next.js from 14.0.4 to 14.2.35 to fix multiple vulnerabilities:
  - Denial of Service with Server Components
  - Authorization bypass vulnerability
  - Cache poisoning
  - Server-Side Request Forgery in Server Actions
  - Authorization bypass in middleware
- **CRITICAL**: Updated Django from 4.2.8 to 4.2.26 to fix:
  - SQL injection in column aliases
  - SQL injection in HasKey(lhs, rhs) on Oracle
  - Denial-of-service attack in intcomma template filter
  - SQL injection via _connector keyword argument in QuerySet
  - Denial-of-service in HttpResponseRedirect on Windows
- **HIGH**: Updated cryptography from 41.0.7 to 42.0.4 to fix:
  - NULL pointer dereference with pkcs12.serialize_key_and_certificates
  - Bleichenbacher timing oracle attack vulnerability
- **HIGH**: Updated gunicorn from 21.2.0 to 22.0.0 to fix:
  - HTTP Request/Response Smuggling vulnerability
  - Request smuggling leading to endpoint restriction bypass
- **MEDIUM**: Updated Pillow from 10.1.0 to 10.3.0 to fix buffer overflow vulnerability
- **MEDIUM**: Updated python-multipart from 0.0.6 to 0.0.18 to fix:
  - Denial of service via deformation multipart/form-data boundary
  - Content-Type Header ReDoS vulnerability

## [1.0.0] - 2024-01-15

### Added

#### Backend
- Django 4.2 backend with REST API
- JWT-based authentication system
- User management with storage quotas
- Schematic upload with validation
- File type validation (.schematic, .schem, .litematica, .nbt)
- File size limits (configurable, default 100MB)
- SHA-256 hash verification for duplicate detection
- Virus scanning with ClamAV integration
- Celery task queue for async processing
- PostgreSQL database integration
- Redis caching and rate limiting
- S3/MinIO object storage support
- Search and filtering capabilities
- Tag-based organization
- Social features (likes, comments)
- Download tracking and statistics
- OpenAPI/Swagger documentation
- Health check endpoint
- Rate limiting (100 req/hour anonymous, 1000 req/hour authenticated)
- CORS configuration
- Security headers
- Admin interface

#### Frontend
- Next.js 14 with React frontend
- TypeScript support
- Modern, stylized UI (Stripe/Dribbble inspired)
- Responsive design (mobile, tablet, desktop)
- Tailwind CSS styling
- Framer Motion animations
- File upload interface with drag-and-drop
- Search and filtering UI
- User authentication pages
- Schematic browsing and discovery
- Trending schematics
- User profile and dashboard
- Like and comment features
- Real-time upload progress tracking

#### Infrastructure
- Docker containerization
- Docker Compose for local development
- Docker Compose production configuration
- Kubernetes deployment manifests
- NGINX reverse proxy configuration
- Development setup script
- Production deployment script
- CI/CD pipeline (GitHub Actions)

#### Documentation
- Comprehensive README with setup instructions
- API examples and usage guide
- Deployment guide for multiple platforms
- Architecture documentation
- Contributing guidelines
- Kubernetes deployment guide

#### Developer Experience
- ESLint and Prettier configuration
- Flake8 linting for Python
- Pytest configuration
- Code coverage setup
- Hot reload for development
- Environment variable management

### Security
- JWT token authentication with refresh
- Password hashing with bcrypt
- Virus scanning on all uploads
- Input validation and sanitization
- CORS protection
- CSRF protection
- Rate limiting to prevent abuse
- Secure file storage with access control
- HTTPS ready (production)

### Performance
- Redis caching for API responses
- Database query optimization with indexes
- Pagination for list endpoints
- CDN-ready architecture
- Async task processing with Celery
- Connection pooling
- Lazy loading in frontend
- Code splitting

## [Unreleased]

### Planned Features
- 3D schematic preview in browser
- Advanced search filters (dimensions, block types)
- User collections and playlists
- User follow system
- Real-time notifications (WebSockets)
- Email notifications
- Social sharing integrations
- API rate limiting tiers
- Premium storage plans
- Mobile app (React Native)
- In-browser schematic editor
- AI-powered recommendations
- Community forums
- Schematic versioning
- Batch operations
- Export to different formats
- Dark mode
- Internationalization (i18n)
- Analytics dashboard
- Moderation tools

### Known Issues
- 3D preview not yet implemented
- No WebSocket support for real-time features
- Limited schematic metadata extraction
- No batch upload support
- No schematic comparison tool

### Future Improvements
- GraphQL API option
- Improved search relevance
- Machine learning for schematic categorization
- Blockchain verification option
- Multi-region deployment
- Advanced caching strategies
- Performance monitoring dashboard
- A/B testing framework

## Development Notes

### Version 1.0.0 Development
- Initial release focusing on core functionality
- Emphasizes security, scalability, and modern architecture
- Built with production deployment in mind
- Comprehensive documentation for developers and users
- Clean, maintainable codebase following best practices

### Technology Stack
- **Backend:** Python 3.11, Django 4.2, Django REST Framework
- **Frontend:** Node.js 18, Next.js 14, React 18, TypeScript
- **Database:** PostgreSQL 15
- **Cache:** Redis 7
- **Storage:** S3-compatible (MinIO for development)
- **Task Queue:** Celery
- **Security:** ClamAV for virus scanning
- **Deployment:** Docker, Kubernetes
- **CI/CD:** GitHub Actions

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
