#!/bin/bash

set -e

echo "Starting Headscale..."

# start headscale server
headscale serve &

sleep 5

echo "Creating namespace..."

headscale namespaces create containers || true

echo "Generating auth key..."

AUTH_KEY=$(headscale preauthkeys create \
  --namespace containers \
  --expiration 0 \
  --output json | jq -r '.key')

echo "Auth Key Generated:"
echo $AUTH_KEY

echo $AUTH_KEY > /var/lib/headscale/authkey

wait