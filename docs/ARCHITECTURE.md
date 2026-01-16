# Architecture Documentation

## System Overview

SchematicShop is a cloud-native, microservices-ready platform for hosting Minecraft schematic files. The architecture is designed for high availability, scalability, and security.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Users                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer / CDN                       │
│                   (NGINX / CloudFront)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│   Frontend (Next.js)     │    │   Backend API (Django)   │
│   - React Components     │    │   - REST API             │
│   - State Management     │    │   - Authentication       │
│   - API Client           │    │   - Business Logic       │
└──────────────────────────┘    └──────────────────────────┘
                                            │
                          ┌─────────────────┼─────────────────┐
                          ▼                 ▼                 ▼
                ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
                │  PostgreSQL  │  │    Redis     │  │    Celery    │
                │  (Metadata)  │  │   (Cache)    │  │  (Tasks)     │
                └──────────────┘  └──────────────┘  └──────────────┘
                          │
                          ▼
                ┌──────────────────────────────────┐
                │   Object Storage (S3/MinIO)      │
                │   - Schematic Files              │
                │   - User Uploads                 │
                └──────────────────────────────────┘
                          │
                          ▼
                ┌──────────────────────────────────┐
                │   ClamAV (Virus Scanning)        │
                └──────────────────────────────────┘
```

## Component Details

### Frontend (Next.js + React)

**Technology Stack:**
- Next.js 14 (React framework with SSR/SSG)
- TypeScript for type safety
- Tailwind CSS for styling
- Framer Motion for animations
- React Query for data fetching
- Axios for API communication

**Responsibilities:**
- Server-side rendering for SEO
- User interface and interactions
- Client-side state management
- Form validation
- File upload with progress tracking
- 3D schematic preview (future)

**Key Features:**
- Responsive design (mobile, tablet, desktop)
- Real-time upload progress
- Search and filtering
- User authentication UI
- File management dashboard

### Backend API (Django + DRF)

**Technology Stack:**
- Django 4.2 (Python web framework)
- Django REST Framework (API)
- JWT authentication
- Celery for async tasks
- PostgreSQL database
- Redis for caching

**Responsibilities:**
- RESTful API endpoints
- User authentication & authorization
- File upload validation
- Database operations
- Business logic
- Task scheduling

**Key Features:**
- JWT token-based authentication
- Rate limiting
- File validation (type, size, hash)
- Automatic virus scanning
- Search and filtering
- User storage quotas
- API documentation (Swagger/OpenAPI)

### Database Layer

#### PostgreSQL
**Purpose:** Primary data store for metadata

**Schema Design:**
- Users (authentication, profiles, quotas)
- Schematics (metadata, relationships)
- Tags (categorization)
- Comments (social features)
- Likes (social features)

**Optimizations:**
- Indexed fields for fast queries
- Foreign key relationships
- JSON fields for flexible metadata
- UUID primary keys for distributed systems

#### Redis
**Purpose:** Caching and task queue

**Use Cases:**
- API response caching
- Session storage
- Rate limiting counters
- Celery message broker
- Real-time features (future)

### Task Queue (Celery)

**Purpose:** Asynchronous background processing

**Tasks:**
- Virus scanning on upload
- Thumbnail generation (future)
- Email notifications (future)
- Batch operations
- Scheduled maintenance

**Configuration:**
- Redis as message broker
- Result backend
- Task routing
- Retry policies
- Monitoring

### Object Storage (S3/MinIO)

**Purpose:** Scalable file storage

**Features:**
- Schematic file storage
- Public/private access control
- CDN integration
- Versioning (optional)
- Lifecycle policies

**Implementation:**
- django-storages for S3 integration
- Presigned URLs for secure downloads
- Multipart uploads for large files
- Metadata tagging

### Security Layer (ClamAV)

**Purpose:** Virus and malware scanning

**Process:**
1. File uploaded to temporary storage
2. Celery task triggered
3. ClamAV scans file
4. Results stored in database
5. Clean files moved to permanent storage
6. Infected files quarantined/deleted

## Data Flow

### File Upload Flow

```
1. User uploads file via frontend
   ↓
2. Frontend validates (size, type)
   ↓
3. POST /api/schematics/ with multipart/form-data
   ↓
4. Backend validates file
   ↓
5. Calculate SHA-256 hash
   ↓
6. Check for duplicates
   ↓
7. Store file in object storage
   ↓
8. Create database record (status: pending)
   ↓
9. Trigger Celery task for virus scan
   ↓
10. Update user storage quota
   ↓
11. Return schematic metadata to user
   ↓
12. [Async] ClamAV scans file
   ↓
13. [Async] Update scan status in database
   ↓
14. [Async] Notify user if infected
```

### File Download Flow

```
1. User requests download
   ↓
2. GET /api/schematics/{id}/
   ↓
3. Check permissions (public or owner)
   ↓
4. Check scan status (must be clean)
   ↓
5. Increment download counter
   ↓
6. Generate presigned URL (if S3)
   ↓
7. Return download URL
   ↓
8. User downloads directly from storage
```

### Authentication Flow

```
1. User submits credentials
   ↓
2. POST /api/auth/login/
   ↓
3. Django validates credentials
   ↓
4. Generate JWT tokens (access + refresh)
   ↓
5. Return tokens to client
   ↓
6. Client stores tokens (localStorage)
   ↓
7. Include access token in API requests
   ↓
8. Backend validates token on each request
   ↓
9. Refresh token when access expires
```

## Scalability

### Horizontal Scaling

**Frontend:**
- Stateless Next.js instances
- Can scale to N replicas
- Load balanced

**Backend:**
- Stateless Django instances
- Can scale to N replicas
- Shared database and cache

**Celery Workers:**
- Multiple workers for parallel processing
- Task distribution via Redis
- Different workers for different task types

### Vertical Scaling

**Database:**
- Increase instance size
- Read replicas for queries
- Connection pooling

**Redis:**
- Increase memory
- Redis Cluster for distribution
- Sentinel for high availability

### Caching Strategy

**Levels:**
1. CDN (static assets, public files)
2. Redis (API responses, sessions)
3. Database query cache
4. Application-level caching

**Cache Invalidation:**
- Time-based expiration
- Event-driven invalidation
- Manual purge on updates

## Security

### Authentication & Authorization
- JWT tokens with expiration
- Refresh token rotation
- Role-based access control (future)

### Input Validation
- File type whitelisting
- File size limits
- Content validation
- XSS prevention
- SQL injection prevention (ORM)

### Data Protection
- HTTPS only in production
- Encrypted passwords (bcrypt)
- Secure session management
- CORS configuration
- CSRF protection

### File Security
- Virus scanning (ClamAV)
- Quarantine infected files
- Hash verification
- Access control lists

### Rate Limiting
- Per-user limits
- Per-endpoint limits
- DDoS protection
- Graceful degradation

## Monitoring & Observability

### Metrics
- Request rate and latency
- Error rates
- Database performance
- Cache hit rates
- Storage usage
- Celery task queue length

### Logging
- Application logs (Django)
- Access logs (NGINX)
- Error logs (Sentry integration ready)
- Audit logs (user actions)

### Health Checks
- `/api/health/` endpoint
- Database connectivity
- Redis connectivity
- Storage accessibility

### Alerting
- Critical errors
- High latency
- Storage quota warnings
- Failed tasks

## Disaster Recovery

### Backup Strategy
- Database: Daily automated backups
- Files: S3 versioning and backup
- Configuration: Version controlled

### Recovery Procedures
1. Restore database from backup
2. Restore files from S3
3. Redeploy application
4. Verify data integrity

### High Availability
- Multi-zone deployment (K8s)
- Database replication
- Redis Sentinel
- Load balancer health checks
- Auto-scaling policies

## Performance Optimization

### Frontend
- Code splitting
- Image optimization
- Lazy loading
- Service worker (future)
- Static generation for public pages

### Backend
- Database query optimization
- Connection pooling
- Query result caching
- Pagination
- Async operations

### Storage
- CDN for file delivery
- Compression
- Efficient file formats
- Thumbnail generation

## Future Enhancements

### Short Term
- 3D schematic preview in browser
- Advanced search filters
- User collections
- Social features (follow, share)

### Medium Term
- Real-time notifications (WebSockets)
- In-browser schematic editor
- Mobile app
- GraphQL API

### Long Term
- AI-powered recommendations
- Collaborative editing
- Blockchain verification (optional)
- Multi-region deployment

## Technology Choices Rationale

**Django:** Mature, secure, batteries-included framework with excellent ORM and ecosystem

**Next.js:** Modern React framework with SSR/SSG, great DX, and performance

**PostgreSQL:** Robust relational database with JSON support and excellent performance

**Redis:** Fast in-memory store, perfect for caching and task queues

**S3/MinIO:** Scalable object storage, industry standard, cost-effective

**ClamAV:** Open-source, reliable virus scanning

**Docker:** Consistent environments, easy deployment, container orchestration ready

**Kubernetes:** Production-grade orchestration, auto-scaling, self-healing

## Conclusion

This architecture provides a solid foundation for a scalable, secure, and maintainable Minecraft schematic hosting platform. The microservices-ready design allows for independent scaling of components, while the use of industry-standard technologies ensures reliability and community support.
