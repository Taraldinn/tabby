#!/bin/bash
# Dokploy Deployment Quick Start Script

set -e

echo "🚀 Tabbycat Dokploy Deployment Setup"
echo "====================================="
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Using existing configuration."
else
    echo "📝 Creating .env file from template..."
    cp .env.dokploy.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and update:"
    echo "   - SECRET_KEY (generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
    echo "   - POSTGRES_PASSWORD"
    echo "   - Email settings (if needed)"
    echo "   - ALLOWED_HOSTS (your domain)"
    echo ""
    read -p "Press Enter after you've updated .env file..."
fi

echo ""
echo "🔧 Deployment Options:"
echo "1. Deploy to Dokploy with Docker (recommended)"
echo "2. Deploy to Dokploy with Buildpacks (simpler)"
echo "3. Test locally with Docker Compose"
echo ""
read -p "Choose option (1, 2, or 3): " option

case $option in
    1)
        echo ""
        echo "📋 Dokploy Docker Deployment Checklist:"
        echo "========================================"
        echo ""
        echo "1. ✅ Ensure Dokploy is installed and running"
        echo "2. ✅ Create a new application in Dokploy dashboard"
        echo "3. ✅ Connect your Git repository"
        echo "4. ✅ Choose 'Docker Compose' as build method"
        echo "5. ✅ Set compose file path: docker-compose.dokploy.yml"
        echo "6. ✅ Add environment variables from .env file"
        echo "7. ✅ Click Deploy"
        echo ""
        echo "📖 Full guide: DOKPLOY_DEPLOYMENT.md"
        echo ""
        echo "🔑 Generate SECRET_KEY:"
        python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
        echo ""
        ;;
    2)
        echo ""
        echo "📋 Dokploy Buildpack Deployment Checklist:"
        echo "==========================================="
        echo ""
        echo "1. ✅ Ensure Dokploy is installed and running"
        echo "2. ✅ Create a new application in Dokploy dashboard"
        echo "3. ✅ Connect your Git repository"
        echo "4. ✅ Choose 'Buildpack' as build method"
        echo "5. ✅ Buildpacks will auto-detect (or use .buildpacks file)"
        echo "6. ✅ Add PostgreSQL and Redis services"
        echo "7. ✅ Add environment variables from .env file"
        echo "8. ✅ Click Deploy"
        echo ""
        echo "📖 Full guide: DOKPLOY_BUILDPACK.md"
        echo ""
        echo "🔑 Generate SECRET_KEY:"
        python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
        echo ""
        echo "📦 Available buildpacks:"
        echo "   - heroku/nodejs (for frontend assets)"
        echo "   - heroku/python (for Django backend)"
        echo ""
        ;;
    3)
        echo ""
        echo "🐳 Testing locally with Docker Compose..."
        echo ""
        
        # Load .env file
        export $(grep -v '^#' .env | xargs)
        
        # Build and start services
        docker-compose -f docker-compose.dokploy.yml up --build -d
        
        echo ""
        echo "⏳ Waiting for services to start..."
        sleep 10
        
        echo ""
        echo "✅ Services started!"
        echo ""
        echo "🌐 Access your application:"
        echo "   - Main app: http://localhost"
        echo "   - Admin panel: http://localhost/database/"
        echo ""
        echo "📊 View logs:"
        echo "   docker-compose -f docker-compose.dokploy.yml logs -f"
        echo ""
        echo "🛑 Stop services:"
        echo "   docker-compose -f docker-compose.dokploy.yml down"
        echo ""
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac

echo ""
echo "✅ Setup complete!"
echo ""
echo "Need help? Check DOKPLOY_DEPLOYMENT.md for detailed instructions."
