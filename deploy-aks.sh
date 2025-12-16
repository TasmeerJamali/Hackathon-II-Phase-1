#!/bin/bash
# AKS Deployment Script for Todo Evolution
# Run this in Azure Cloud Shell after connecting to your AKS cluster

echo "🚀 Deploying Todo Evolution to AKS..."

# Step 1: Clone the repository
echo "📥 Cloning repository..."
git clone https://github.com/TasmeerJamali/Hackathon-II-Phase-1.git
cd Hackathon-II-Phase-1

# Step 2: Create namespace
echo "📦 Creating namespace..."
kubectl create namespace todo-evolution --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Create secrets (values from .env.local)
echo "🔐 Creating secrets..."
kubectl create secret generic todo-secrets \
  --namespace=todo-evolution \
  --from-literal=DATABASE_URL='postgresql://neondb_owner:npg_1hZQEksyeWg4@ep-spring-wave-ahu3yhw4-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require' \
  --from-literal=BETTER_AUTH_SECRET='panaversity-hackathon-physical-ai-2024-super-secret-key' \
  --from-literal=OPENAI_API_KEY='sk-placeholder-add-your-key' \
  --dry-run=client -o yaml | kubectl apply -f -

# Step 4: Deploy backend
echo "🐍 Deploying backend..."
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: todo-evolution
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: python:3.13-slim
        command: ["sh", "-c", "pip install fastapi uvicorn sqlmodel && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
        workingDir: /app
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: DATABASE_URL
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: BETTER_AUTH_SECRET
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: OPENAI_API_KEY
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: todo-evolution
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: backend
EOF

# Step 5: Wait for service to get external IP
echo "⏳ Waiting for external IP (this may take 1-2 minutes)..."
kubectl get service backend -n todo-evolution -w &
sleep 60

# Step 6: Get the external IP
echo ""
echo "✅ Deployment complete!"
echo ""
kubectl get all -n todo-evolution
echo ""
echo "🌐 Get your backend URL with:"
echo "kubectl get svc backend -n todo-evolution -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
