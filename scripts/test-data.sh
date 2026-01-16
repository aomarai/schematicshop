#!/bin/bash
# Helper script to manage test schematic data
# Usage: ./scripts/test-data.sh [load|clear|reload]

set -e

COMMAND=${1:-"help"}

case "$COMMAND" in
  load)
    echo "📦 Loading test schematic data..."
    docker-compose exec backend python manage.py load_test_schematics
    echo "✅ Test data loaded successfully!"
    echo ""
    echo "You can now:"
    echo "  - Browse schematics at http://localhost:3000"
    echo "  - Login with testuser1/testpass123 (or testuser2, testuser3)"
    echo "  - Access API at http://localhost:8000/api/schematics/"
    ;;
  
  clear)
    echo "🗑️  Clearing test schematic data..."
    docker-compose exec backend python manage.py clear_test_schematics
    echo "✅ Test data cleared successfully!"
    ;;
  
  reload)
    echo "🔄 Reloading test schematic data..."
    docker-compose exec backend python manage.py load_test_schematics --clear
    echo "✅ Test data reloaded successfully!"
    echo ""
    echo "You can now:"
    echo "  - Browse schematics at http://localhost:3000"
    echo "  - Login with testuser1/testpass123 (or testuser2, testuser3)"
    echo "  - Access API at http://localhost:8000/api/schematics/"
    ;;
  
  *)
    echo "Test Data Management Script"
    echo ""
    echo "Usage: ./scripts/test-data.sh [command]"
    echo ""
    echo "Commands:"
    echo "  load    - Load test/dummy schematic data"
    echo "  clear   - Clear test schematic data"
    echo "  reload  - Clear and reload test data"
    echo ""
    echo "Example:"
    echo "  ./scripts/test-data.sh load"
    ;;
esac
