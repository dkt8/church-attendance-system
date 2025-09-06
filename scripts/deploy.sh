#!/bin/bash
# Quick deploy script for attendance system
# Usage: ./deploy.sh "Your update message"

cd "$(dirname "$0")"

echo "🚀 Pushing code to Google Apps Script..."
clasp push

echo "📦 Updating production deployment..."
MESSAGE="${1:-Updated $(date +'%Y-%m-%d %H:%M')}"
clasp deploy --deploymentId AKfycbxBgVHZ4qzoQTZxeuGJyA-cJUkL9rVPfm_FtJCdIBfNf3qX1V_OfUOz8SayQMcD8xNL --description "$MESSAGE"

echo "✅ Deployment complete!"
echo "🌐 Web App URL: https://script.google.com/macros/s/AKfycbxBgVHZ4qzoQTZxeuGJyA-cJUkL9rVPfm_FtJCdIBfNf3qX1V_OfUOz8SayQMcD8xNL/exec"
