#!/bin/bash

# SchematicShop Development Setup Script

echo "🚀 Setting up SchematicShop Development Environment..."

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Create environment files
echo "📝 Creating environment files..."

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env from template"
else
    echo "⚠️  backend/.env already exists, skipping..."
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.example frontend/.env.local
    echo "✅ Created frontend/.env.local from template"
else
    echo "⚠️  frontend/.env.local already exists, skipping..."
fi

# Start services
echo "🐳 Starting Docker services..."
docker compose up -d
if [ $? -ne 0 ]; then
    echo "❌ Docker Compose failed to start services. Check the output above and fix any build errors." 
    exit 1
fi

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service health..."
docker compose ps

# Run migrations
echo "📦 Running database migrations..."
docker compose exec -T backend python manage.py migrate

# Create superuser (optional)
echo ""
echo "Would you like to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    docker compose exec backend python manage.py createsuperuser
fi

# Create MinIO bucket
echo "🪣 Setting up MinIO bucket..."
docker compose exec -T minio mc alias set local http://localhost:9000 minioadmin minioadmin 2>/dev/null || true
docker compose exec -T minio mc mb local/schematics 2>/dev/null || true
docker compose exec -T minio mc anonymous set public local/schematics 2>/dev/null || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "📌 Access the application:"
echo "   - Frontend:    http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - Admin:       http://localhost:8000/admin"
echo "   - API Docs:    http://localhost:8000/api/docs/"
echo "   - MinIO:       http://localhost:9001 (admin/minioadmin)"
echo ""
echo "🛠️  Useful commands:"
echo "   - View logs:        docker compose logs -f"
echo "   - Stop services:    docker compose down"
echo "   - Restart services: docker compose restart"
echo ""
