#!/bin/bash

echo "🚦 Starting Smart Traffic Management Dashboard..."
echo

echo "📡 Starting Backend Server..."
cd backend
python run.py &
BACKEND_PID=$!

echo "⏳ Waiting for backend to start..."
sleep 5

echo "🎨 Starting Frontend Server..."
cd ..
npm start &
FRONTEND_PID=$!

echo
echo "✅ Both servers are starting up!"
echo "📡 Backend: http://localhost:5000"
echo "🎨 Frontend: http://localhost:3000"
echo
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Wait for user to stop
wait
