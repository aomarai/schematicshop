#!/bin/bash

# Production deployment script
# Usage: ./deploy.sh [environment]

ENVIRONMENT=${1:-production}

echo "🚀 Deploying SchematicShop to $ENVIRONMENT..."

# Check if environment file exists
if [ ! -f ".env.$ENVIRONMENT" ]; then
    echo "❌ Environment file .env.$ENVIRONMENT not found!"
    exit 1
fi

# Load environment variables
export $(cat .env.$ENVIRONMENT | xargs)

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose -f docker-compose.prod.yml build

# Push images to registry (if using)
# echo "📤 Pushing images to registry..."
# docker-compose -f docker-compose.prod.yml push

# Deploy
echo "🚢 Deploying services..."

if [ "$ENVIRONMENT" = "kubernetes" ]; then
    # Kubernetes deployment
    kubectl apply -f k8s/database.yaml
    kubectl apply -f k8s/deployment.yaml
    
    echo "⏳ Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=backend -n schematicshop --timeout=300s
    
    echo "📦 Running migrations..."
    kubectl exec -it deployment/backend -n schematicshop -- python manage.py migrate
    
    echo "📊 Collecting static files..."
    kubectl exec -it deployment/backend -n schematicshop -- python manage.py collectstatic --noinput
    
else
    # Docker Compose deployment
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    echo "📦 Running migrations..."
    docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate
    
    echo "📊 Collecting static files..."
    docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput
fi

echo "✅ Deployment complete!"
echo ""
echo "🔍 Checking service health..."

# Health check
if curl -f http://localhost/api/health/ > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend health check failed"
fi

echo ""
echo "📌 Next steps:"
echo "   1. Verify all services are running"
echo "   2. Test the application"
echo "   3. Monitor logs for errors"
echo "   4. Set up SSL certificates if not already done"
echo ""
