# Deployment Guide

This guide covers deploying SchematicShop to various platforms.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Compose Production](#docker-compose-production)
3. [Kubernetes](#kubernetes)
4. [AWS](#aws)
5. [Google Cloud Platform](#google-cloud-platform)
6. [Azure](#azure)

## Local Development

The easiest way to get started:

```bash
# Clone the repository
git clone https://github.com/aomarai/schematicshop.git
cd schematicshop

# Run the setup script
./setup-dev.sh

# Or manually:
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Admin: http://localhost:8000/admin

## Docker Compose Production

### Prerequisites
- Docker and Docker Compose
- Domain name pointed to your server
- SSL certificates (or use Let's Encrypt)

### Steps

1. **Clone and configure**:
```bash
git clone https://github.com/aomarai/schematicshop.git
cd schematicshop
cp .env.prod.example .env.prod
```

2. **Edit `.env.prod`** with your production values:
   - Set strong passwords
   - Configure S3/object storage
   - Set proper domain names
   - Add SSL certificates

3. **Deploy**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

4. **Run migrations**:
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --noinput
```

5. **Configure SSL** (if using Let's Encrypt):
```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Update nginx.conf with certificate paths
# Restart nginx
docker-compose restart nginx
```

## Kubernetes

### Prerequisites
- Kubernetes cluster (1.24+)
- kubectl configured
- Helm (optional, recommended)

### Deploy to Kubernetes

1. **Update configuration**:
```bash
# Edit k8s/deployment.yaml
# Update domain names and secrets
```

2. **Deploy**:
```bash
kubectl apply -f k8s/database.yaml
kubectl apply -f k8s/deployment.yaml
```

3. **Run migrations**:
```bash
kubectl exec -it deployment/backend -n schematicshop -- python manage.py migrate
kubectl exec -it deployment/backend -n schematicshop -- python manage.py createsuperuser
```

4. **Configure Ingress**:
   - Install NGINX Ingress Controller
   - Install cert-manager for SSL
   - Update ingress hostnames in `k8s/deployment.yaml`

See [k8s/README.md](k8s/README.md) for detailed instructions.

## AWS

### Architecture
- ECS/EKS for containers
- RDS for PostgreSQL
- ElastiCache for Redis
- S3 for file storage
- CloudFront for CDN
- Application Load Balancer

### Option 1: ECS with Fargate

1. **Set up infrastructure**:
```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier schematicshop-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 20

# Create ElastiCache cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id schematicshop-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1

# Create S3 bucket
aws s3 mb s3://schematicshop-files
```

2. **Build and push images**:
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URL

# Build and push
docker build -t YOUR_ECR_URL/schematicshop-backend:latest -f backend/Dockerfile .
docker push YOUR_ECR_URL/schematicshop-backend:latest

docker build -t YOUR_ECR_URL/schematicshop-frontend:latest frontend/
docker push YOUR_ECR_URL/schematicshop-frontend:latest
```

3. **Create ECS task definitions and services**
4. **Configure Application Load Balancer**
5. **Set up CloudFront distribution**

### Option 2: EKS (Elastic Kubernetes Service)

1. Create EKS cluster using eksctl or AWS Console
2. Follow the [Kubernetes](#kubernetes) deployment steps
3. Configure AWS Load Balancer Controller
4. Use Amazon RDS and ElastiCache

## Google Cloud Platform

### Architecture
- GKE for containers
- Cloud SQL for PostgreSQL
- Memorystore for Redis
- Cloud Storage for files
- Cloud CDN

### Steps

1. **Create GKE cluster**:
```bash
gcloud container clusters create schematicshop \
  --num-nodes=3 \
  --machine-type=n1-standard-2 \
  --region=us-central1
```

2. **Create Cloud SQL instance**:
```bash
gcloud sql instances create schematicshop-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1
```

3. **Create Redis instance**:
```bash
gcloud redis instances create schematicshop-redis \
  --size=1 \
  --region=us-central1
```

4. **Create Cloud Storage bucket**:
```bash
gsutil mb gs://schematicshop-files
```

5. **Deploy to GKE**:
   - Follow [Kubernetes](#kubernetes) deployment steps
   - Update secrets with GCP credentials
   - Configure Google Cloud Load Balancer

## Azure

### Architecture
- AKS for containers
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Azure Blob Storage
- Azure CDN

### Steps

1. **Create resource group**:
```bash
az group create --name schematicshop --location eastus
```

2. **Create AKS cluster**:
```bash
az aks create \
  --resource-group schematicshop \
  --name schematicshop-cluster \
  --node-count 3 \
  --enable-addons monitoring
```

3. **Create PostgreSQL**:
```bash
az postgres server create \
  --resource-group schematicshop \
  --name schematicshop-db \
  --location eastus \
  --admin-user admin \
  --admin-password YOUR_PASSWORD \
  --sku-name B_Gen5_1
```

4. **Create Redis**:
```bash
az redis create \
  --resource-group schematicshop \
  --name schematicshop-redis \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

5. **Create storage account**:
```bash
az storage account create \
  --name schematicshopfiles \
  --resource-group schematicshop \
  --location eastus \
  --sku Standard_LRS
```

6. **Deploy to AKS**:
   - Follow [Kubernetes](#kubernetes) deployment steps
   - Update secrets with Azure credentials
   - Configure Azure Application Gateway

## Post-Deployment Checklist

After deploying to any platform:

- [ ] Verify all services are running
- [ ] Run database migrations
- [ ] Create superuser account
- [ ] Test file upload
- [ ] Configure backups
- [ ] Set up monitoring (Prometheus, Grafana, CloudWatch, etc.)
- [ ] Configure logging (ELK stack, CloudWatch Logs, etc.)
- [ ] Set up alerting
- [ ] Test disaster recovery
- [ ] Enable auto-scaling
- [ ] Configure CDN
- [ ] Set up DNS
- [ ] Configure SSL/TLS
- [ ] Review security settings
- [ ] Load test the application

## Monitoring

### Health Checks
```bash
# Backend health
curl http://your-domain.com/api/health/

# Should return: {"status": "healthy", "service": "schematicshop-api"}
```

### Logs
```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f celery

# Kubernetes
kubectl logs -f deployment/backend -n schematicshop
kubectl logs -f deployment/celery-worker -n schematicshop
```

### Metrics
- Set up Prometheus and Grafana
- Monitor: CPU, Memory, Disk, Network, Request rate, Error rate, Response time
- Set alerts for critical metrics

## Backup Strategy

### Database Backups
```bash
# PostgreSQL backup
pg_dump -h localhost -U user dbname > backup.sql

# Automated backups (add to cron)
0 2 * * * pg_dump -h localhost -U user dbname | gzip > /backups/backup_$(date +\%Y\%m\%d).sql.gz
```

### File Backups
- Enable versioning on S3/Cloud Storage
- Set up automated backups
- Test restore procedures regularly

## Scaling

### Horizontal Scaling
```bash
# Docker Compose
docker-compose up -d --scale backend=3 --scale celery=2

# Kubernetes
kubectl scale deployment backend --replicas=5 -n schematicshop
kubectl scale deployment celery-worker --replicas=3 -n schematicshop
```

### Auto-scaling (Kubernetes)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check DATABASE_URL
   - Verify network connectivity
   - Check firewall rules

2. **File upload fails**
   - Verify S3/storage credentials
   - Check bucket permissions
   - Verify ClamAV is running

3. **High memory usage**
   - Check Celery task queue
   - Monitor PostgreSQL connections
   - Review application logs

4. **Slow response times**
   - Enable Redis caching
   - Set up CDN
   - Optimize database queries
   - Add read replicas

## Security Hardening

1. Change all default passwords
2. Enable HTTPS only
3. Set up Web Application Firewall (WAF)
4. Enable rate limiting
5. Regular security updates
6. Enable audit logging
7. Use secrets management (Vault, AWS Secrets Manager, etc.)
8. Implement network policies (Kubernetes)
9. Regular security scans
10. GDPR/privacy compliance

## Support

For deployment issues:
- Check documentation: [README.md](README.md)
- Open an issue: https://github.com/aomarai/schematicshop/issues
- Contact: support@schematicshop.example
