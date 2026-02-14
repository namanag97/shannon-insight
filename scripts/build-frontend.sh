#!/bin/bash
# Build frontend for PyPI packaging

set -e

echo "🎨 Building frontend..."
cd src/shannon_insight/server/frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo "🔨 Running production build..."
npm run build

echo "✅ Frontend built successfully!"
echo "📄 Output: src/shannon_insight/server/static/app.js"
