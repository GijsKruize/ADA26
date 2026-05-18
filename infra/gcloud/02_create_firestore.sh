#!/bin/bash
set -euo pipefail

echo "Ensuring Firestore database exists..."

# Try to create the database (default). If it exists, this might fail, so we catch it.
# Note: Firestore database creation can sometimes only be done once per project for 'default'.
if gcloud firestore databases describe --project="${PROJECT_ID}" --database="(default)" >/dev/null 2>&1; then
  echo "Firestore (default) database already exists."
else
  echo "Attempting to create Firestore (default) database in ${REGION}..."
  gcloud firestore databases create --project="${PROJECT_ID}" --location="${REGION}" --type=firestore-native || echo "Could not create database. It might already exist or require manual activation in the console."
fi

echo "Firestore setup script completed."
