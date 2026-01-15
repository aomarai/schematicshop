# SchematicShop Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying SchematicShop to a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- NGINX Ingress Controller
- cert-manager (for TLS certificates)
- Persistent Volume provisioner

## Files

- `deployment.yaml` - Main application deployments (backend, frontend, celery)
- `database.yaml` - Database and Redis StatefulSets
- `README.md` - This file

## Quick Deploy

1. **Create namespace**:
```bash
kubectl apply -f deployment.yaml
```

2. **Deploy databases**:
```bash
kubectl apply -f database.yaml
```

3. **Update secrets**:
```bash
kubectl edit secret backend-secrets -n schematicshop
kubectl edit secret postgres-secret -n schematicshop
```

4. **Run migrations**:
```bash
kubectl exec -it deployment/backend -n schematicshop -- python manage.py migrate
```

5. **Create superuser**:
```bash
kubectl exec -it deployment/backend -n schematicshop -- python manage.py createsuperuser
```

## Configuration

### Secrets

Update these secrets before deploying to production:
- `backend-secrets`: Django secret key, database credentials, AWS keys
- `postgres-secret`: PostgreSQL password

### Ingress

Update the hostnames in `deployment.yaml`:
```yaml
- schematicshop.example.com
- api.schematicshop.example.com
```

### Storage

This deployment uses:
- PersistentVolumeClaim for PostgreSQL
- External S3-compatible storage for schematic files

Configure your S3 credentials in the `backend-secrets`.

## Scaling

Scale the deployments:
```bash
kubectl scale deployment backend --replicas=5 -n schematicshop
kubectl scale deployment celery-worker --replicas=3 -n schematicshop
```

## Monitoring

Check pod status:
```bash
kubectl get pods -n schematicshop
```

View logs:
```bash
kubectl logs -f deployment/backend -n schematicshop
kubectl logs -f deployment/celery-worker -n schematicshop
```

## Backup

Backup PostgreSQL:
```bash
kubectl exec -it statefulset/postgres -n schematicshop -- pg_dump -U schematicshop schematicshop > backup.sql
```

## Production Considerations

1. **Use managed databases** (AWS RDS, Google Cloud SQL, etc.)
2. **Use managed object storage** (AWS S3, Google Cloud Storage, etc.)
3. **Set up monitoring** (Prometheus, Grafana)
4. **Configure autoscaling** (HorizontalPodAutoscaler)
5. **Set resource limits** appropriately for your workload
6. **Enable network policies** for security
7. **Use secrets management** (HashiCorp Vault, AWS Secrets Manager)
