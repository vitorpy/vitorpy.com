#!/bin/bash

# Deployment script for vitorpy.com
# Deploys Hugo site to Hetzner server

set -e  # Exit on any error

# Configuration
SERVER="root@167.235.24.234"
REMOTE_DIR="/var/www/vitorpy.com"
NGINX_CONFIG="/etc/nginx/conf.d/vitorpy.conf"

echo "🚀 Starting deployment to vitorpy.com..."

# Step 1: Build the Hugo site
echo "📦 Building Hugo site..."
hugo --minify

if [ $? -ne 0 ]; then
    echo "❌ Hugo build failed!"
    exit 1
fi

echo "✅ Hugo build complete"

# Step 2: Check if nginx config has changed
echo "🔍 Checking nginx configuration..."
LOCAL_NGINX_HASH=$(sha256sum nginx.conf | cut -d' ' -f1)
REMOTE_NGINX_HASH=$(ssh $SERVER "sha256sum $NGINX_CONFIG 2>/dev/null | cut -d' ' -f1" || echo "")

if [ "$LOCAL_NGINX_HASH" != "$REMOTE_NGINX_HASH" ]; then
    echo "📝 Nginx config has changed, updating..."
    scp nginx.conf $SERVER:$NGINX_CONFIG
    
    # Test nginx config
    ssh $SERVER "nginx -t"
    if [ $? -ne 0 ]; then
        echo "❌ Nginx config test failed! Please check the configuration."
        exit 1
    fi
    
    # Reload nginx
    ssh $SERVER "systemctl reload nginx"
    echo "✅ Nginx config updated and reloaded"
else
    echo "✅ Nginx config unchanged"
fi

# Step 3: Deploy the site files
echo "📤 Uploading site files..."
rsync -avz --delete \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='_site/.git' \
    public/ $SERVER:$REMOTE_DIR/

if [ $? -ne 0 ]; then
    echo "❌ Rsync failed!"
    exit 1
fi

echo "✅ Site files uploaded"

# Step 4: Set correct permissions
echo "🔒 Setting permissions..."
ssh $SERVER "chown -R nginx:nginx $REMOTE_DIR && chmod -R 755 $REMOTE_DIR"

echo "✅ Deployment complete!"
echo "🌐 Your site is live at https://vitorpy.com"