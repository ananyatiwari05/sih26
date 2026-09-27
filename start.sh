#!/bin/bash
set -e

echo "Starting NAZAR 2.0 Backend & Frontend..."

# Install dependencies if needed
echo "Checking backend dependencies..."
cd nazar-backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
export PROJ_DIR=$(brew --prefix proj)
export PATH="$PROJ_DIR/bin:$PATH"
pip install -r requirements.txt
cd ..

echo "Checking frontend dependencies..."
cd nazar-frontend
npm install
cd ..

# Start Backend
echo "Starting Backend on port 8000..."
cd nazar-backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start Frontend
echo "Starting Frontend on port 5173..."
cd nazar-frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "NAZAR 2.0 is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both."

trap "echo 'Stopping servers...'; kill $BACKEND_PID; kill $FRONTEND_PID; exit 0" SIGINT SIGTERM

wait
