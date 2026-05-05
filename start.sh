#!/bin/bash

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "🚀 Xafsizyol — запуск..."
echo ""

# --- Останавливаем старые процессы ---
echo "⏹  Останавливаем старые процессы..."
pkill -f "uvicorn main:app" 2>/dev/null && echo "   uvicorn остановлен" || true
pkill -f "ngrok" 2>/dev/null && echo "   ngrok остановлен" || true
sleep 1

# --- Бекенд ---
echo "▶  Бекенд (FastAPI :8000)"
cd "$ROOT/backend"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
sleep 2

# --- Проверка бекенда ---
if ! curl -s http://localhost:8000/api/health | grep -q "ok"; then
  echo "❌ Бекенд не запустился"
  kill $BACKEND_PID 2>/dev/null
  exit 1
fi
echo "✅ Бекенд запущен: http://localhost:8000"

# --- Туннель ---
echo "▶  ngrok туннель → araceli-televisionary-dusti.ngrok-free.dev"
ngrok http --url=araceli-televisionary-dusti.ngrok-free.dev 8000 &
NGROK_PID=$!
sleep 3

echo ""
echo "✅ Бекенд:   http://localhost:8000"
echo "✅ Туннель:  https://araceli-televisionary-dusti.ngrok-free.dev"
echo "✅ API docs: https://araceli-televisionary-dusti.ngrok-free.dev/docs"
echo ""
echo "Остановить — нажми Ctrl+C"
echo ""

trap "echo ''; echo 'Остановка...'; kill $BACKEND_PID $NGROK_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait
