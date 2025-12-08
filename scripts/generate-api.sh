#!/bin/bash

# Exit on error
set -e

# Base directory
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$BASE_DIR/backend"
FRONTEND_DIR="$BASE_DIR"

echo "📍 Base directory: $BASE_DIR"

# 1. Export OpenAPI Spec from Backend
echo "📤 Exporting OpenAPI spec from backend..."
cd "$BACKEND_DIR"
python export_openapi.py

if [ ! -f "openapi.json" ]; then
    echo "❌ Error: openapi.json was not generated."
    exit 1
fi

echo "✅ OpenAPI spec exported."

# 2. Generate TypeScript Client
echo "🔨 Generating TypeScript client..."
cd "$FRONTEND_DIR"
npx openapi-typescript-codegen --input "$BACKEND_DIR/openapi.json" --output src/api/generated --client fetch

echo "✅ API Client generated in src/api/generated"
