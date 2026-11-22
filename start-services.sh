#!/usr/bin/env bash
# Start (or restart) the SkinCare AI backend + frontend under PM2.
# PM2 keeps both processes alive and auto-restarts them on crash.
set -u

cd "$(dirname "$0")"

echo "==> Starting SkinCare AI services with PM2..."

# Backend (FastAPI on port 12000)
pm2 delete skincare-backend 2>/dev/null
cd backend
pm2 start ". .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 12000" \
  --name skincare-backend --interpreter bash
cd ..

# Frontend (Vite on port 12001)
pm2 delete skincare-frontend 2>/dev/null
cd frontend
pm2 start "npm run dev" --name skincare-frontend --cwd "$(pwd)"
cd ..

pm2 save
echo
echo "==> Services started:"
pm2 list
echo
echo "Backend:  http://localhost:12000/docs"
echo "Frontend: http://localhost:12001/"
echo "Public:   https://work-2-gjzkcahmbvtjklzd.prod-runtime.all-hands.dev"
