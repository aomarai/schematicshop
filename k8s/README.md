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
- `authentik.yaml` - Authentik identity provider (OAuth/OIDC)
- `README.md` - This file

## Quick Deploy

1. **Create namespace and deploy databases**:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f database.yaml
```

2. **Deploy Authentik (for OAuth/social login)**:
```bash
kubectl apply -f authentik.yaml
```

3. **Update secrets**:
```bash
kubectl edit secret backend-secrets -n schematicshop
kubectl edit secret postgres-secret -n schematicshop
kubectl edit secret authentik-secrets -n schematicshop
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

**backend-secrets**: 
- Django secret key
- Database credentials
- AWS keys
- OAuth credentials (Google, Discord, GitHub)
- Authentik connection details

**postgres-secret**: 
- PostgreSQL password

**authentik-secrets**:
- Authentik secret key (generate a random 50-character string)
- Bootstrap password (for initial admin login)
- Bootstrap token
- PostgreSQL password

### OAuth Configuration

To enable social login:

1. **Configure OAuth providers** in their respective developer consoles:
   - Google: https://console.cloud.google.com/
   - Discord: https://discord.com/developers/applications
   - GitHub: https://github.com/settings/developers

2. **Update backend-secrets** with OAuth credentials:
```yaml
stringData:
  GOOGLE_CLIENT_ID: "your-google-client-id"
  GOOGLE_CLIENT_SECRET: "your-google-client-secret"
  DISCORD_CLIENT_ID: "your-discord-client-id"
  DISCORD_CLIENT_SECRET: "your-discord-client-secret"
  GITHUB_CLIENT_ID: "your-github-client-id"
  GITHUB_CLIENT_SECRET: "your-github-client-secret"
```

3. **Access Authentik Admin**:
   - URL: https://auth.schematicshop.example.com
   - Username: `akadmin`
   - Password: (value from authentik-secrets AUTHENTIK_BOOTSTRAP_PASSWORD)

4. **Configure providers in Authentik** following the guide in `../docs/authentik-setup.md`

### Ingress

Update the hostnames in `deployment.yaml`:
```yaml
- schematicshop.example.com      # Frontend
- api.schematicshop.example.com  # Backend API
- auth.schematicshop.example.com # Authentik (OAuth provider)
```

### Storage

This deployment uses:
- PersistentVolumeClaim for PostgreSQL
- PersistentVolumeClaim for Authentik PostgreSQL
- PersistentVolumeClaim for Authentik media files
- External S3-compatible storage for schematic files

Configure your S3 credentials in the `backend-secrets`.

## Scaling

Scale the deployments:
```bash
kubectl scale deployment backend --replicas=5 -n schematicshop
kubectl scale deployment celery-worker --replicas=3 -n schematicshop
kubectl scale deployment authentik-server --replicas=3 -n schematicshop
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
kubectl logs -f deployment/authentik-server -n schematicshop
```

## Backup

Backup PostgreSQL (SchematicShop):
```bash
kubectl exec -it statefulset/postgres -n schematicshop -- pg_dump -U schematicshop schematicshop > backup.sql
```

Backup PostgreSQL (Authentik):
```bash
kubectl exec -it statefulset/authentik-postgres -n schematicshop -- pg_dump -U authentik authentik > authentik-backup.sql
```

## Troubleshooting

### Authentik Issues

**Check Authentik logs**:
```bash
kubectl logs -f deployment/authentik-server -n schematicshop
kubectl logs -f deployment/authentik-worker -n schematicshop
```

**Verify Authentik is healthy**:
```bash
kubectl get pods -n schematicshop | grep authentik
kubectl exec -it deployment/authentik-server -n schematicshop -- wget -O- http://localhost:9000/-/health/live/
```

**Reset Authentik admin password**:
```bash
kubectl exec -it deployment/authentik-server -n schematicshop -- ak create_admin_group
kubectl exec -it deployment/authentik-server -n schematicshop -- ak create_admin_user
```

### OAuth Issues

**Verify environment variables**:
```bash
kubectl exec -it deployment/backend -n schematicshop -- env | grep -E 'GOOGLE|DISCORD|GITHUB|AUTHENTIK'
```

**Check OAuth callback URLs** match in provider console:
- Google: `https://api.schematicshop.example.com/accounts/google/login/callback/`
- Discord: `https://api.schematicshop.example.com/accounts/discord/login/callback/`
- GitHub: `https://api.schematicshop.example.com/accounts/github/login/callback/`

## Production Considerations

1. **Use managed databases** (AWS RDS, Google Cloud SQL, Azure Database)
2. **Use managed object storage** (AWS S3, Google Cloud Storage, Azure Blob)
3. **Set up monitoring** (Prometheus, Grafana, Datadog)
4. **Configure autoscaling** (HorizontalPodAutoscaler)
5. **Set resource limits** appropriately for your workload
6. **Enable network policies** for security
7. **Use secrets management** (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault)
8. **Configure backup automation** for databases
9. **Set up logging** (ELK stack, Loki, CloudWatch)
10. **Enable HTTPS** for all endpoints with valid certificates
11. **Configure OAuth redirect URIs** with production domains
12. **Rotate secrets regularly** (especially OAuth credentials and secret keys)
13. **Enable MFA** in Authentik for admin accounts
14. **Configure rate limiting** at ingress level
15. **Set up disaster recovery plan** with regular backup testing

## Security Checklist

- [ ] Change all default passwords in secrets
- [ ] Generate strong random SECRET_KEY for Django
- [ ] Generate strong random AUTHENTIK_SECRET_KEY
- [ ] Configure OAuth apps with production redirect URIs
- [ ] Enable HTTPS/TLS for all ingress endpoints
- [ ] Restrict database access to cluster-internal only
- [ ] Enable network policies
- [ ] Configure pod security policies
- [ ] Set up RBAC appropriately
- [ ] Enable audit logging
- [ ] Configure MFA in Authentik
- [ ] Rotate OAuth credentials periodically
- [ ] Use managed secrets service in production
- [ ] Enable container image scanning
- [ ] Keep all images updated with security patches

## Architecture Overview

```
Internet
    |
    v
[Ingress Controller]
    |
    +-- schematicshop.example.com -> Frontend (Next.js)
    +-- api.schematicshop.example.com -> Backend (Django)
    +-- auth.schematicshop.example.com -> Authentik (IdP)
    
Backend connects to:
- PostgreSQL (SchematicShop data)
- Redis (cache + Celery)
- S3/Object Storage (schematic files)
- Authentik (OAuth validation)

Authentik connects to:
- PostgreSQL (Authentik data)
- Redis (cache)
- OAuth Providers (Google, Discord, GitHub)
```

## Support

For detailed OAuth setup instructions, see `../docs/authentik-setup.md`

For general deployment issues, check:
- Kubernetes events: `kubectl get events -n schematicshop`
- Pod status: `kubectl describe pod <pod-name> -n schematicshop`
- Logs: `kubectl logs <pod-name> -n schematicshop`
