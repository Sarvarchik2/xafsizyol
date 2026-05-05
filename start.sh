#!/bin/bash

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "🚀 Xafsizyol — запуск..."
echo ""

# --- Бекенд ---
echo "▶ Бекенд (FastAPI :8000)"
cd "$ROOT/backend"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

sleep 2

# --- Туннель ---
echo "▶ ngrok туннель → araceli-televisionary-dusti.ngrok-free.dev"
ngrok http --url=araceli-televisionary-dusti.ngrok-free.dev 8000 &
NGROK_PID=$!

sleep 3

# --- Проверка ---
echo ""
if curl -s http://localhost:8000/api/health | grep -q "ok"; then
  echo "✅ Бекенд: http://localhost:8000"
  echo "✅ Туннель: https://araceli-televisionary-dusti.ngrok-free.dev"
  echo "✅ API docs: https://araceli-televisionary-dusti.ngrok-free.dev/docs"
else
  echo "❌ Бекенд не отвечает"
fi

echo ""
echo "Остановить — нажми Ctrl+C"
echo ""

# Ждём и при Ctrl+C убиваем всё
trap "echo ''; echo 'Остановка...'; kill $BACKEND_PID $NGROK_PID 2>/dev/null; exit 0" SIGINT SIGTERM
wait
