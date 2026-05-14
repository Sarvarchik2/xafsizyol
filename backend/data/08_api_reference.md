# Xafsizyol API Reference

## Base URL

The backend API runs at the configured BACKEND_URL. Version: v3.

## Authentication

Most read endpoints are public. Telegram initData validation is available via POST /api/auth/validate.

## Endpoints

### GET /
Health check root.
Response: `{"status": "ok", "message": "Xafsizyol API v3 (SQLite)"}`

### GET /api/health
Returns API status and total report count.
Response: `{"status": "ok", "reports": <count>}`

### GET /api/reports
Returns all reports sorted by creation date (newest first).
Response: Array of Report objects.

### GET /api/reports/{id}
Returns a single report by its ID.
Path param: id — 8-character hex string
Response: Report object or 404 if not found.

### GET /api/reports/user/{userId}
Returns all reports submitted by a specific user.
Path param: userId — Telegram user ID string
Response: Array of Report objects.

### POST /api/reports
Creates a new report.
Required body fields: lat (float), lng (float), address (string), severity (Small|Medium|Critical), description (string)
Optional body fields: photo (base64 string or URL), city (string), district (string), userId (string), phoneNumber (string)
Response: Created Report object.
Side effect: Sends Telegram notification to the user and admin.

### POST /api/reports/{id}/vote
Increments the vote count of a report by 1.
Path param: id — report ID
Response: Updated Report object.

### PATCH /api/reports/{id}/status
Updates the status of a report.
Path param: id — report ID
Query param: status — one of: Pending, In Progress, Fixed
Response: Updated Report object.
Side effect: Sends Telegram notification to report owner.

### POST /api/auth/validate
Validates Telegram WebApp initData (HMAC verification).
Body: `{"initData": "<telegram_init_data_string>"}`
Response: `{"valid": true}` or 401 Unauthorized.

### POST /api/chat
Web chat endpoint powered by RAG + Ollama LLM.
Body: `{"message": "<user_message>", "language": "uz|ru|en"}`
Response: `{"reply": "<ai_response>"}`

### GET /api/setup-webhook
Registers the Telegram webhook URL with Telegram API.
Requires BACKEND_URL environment variable to be set.

### POST /webhook
Telegram webhook receiver — handles incoming Telegram bot messages.
Processes /start command and free-text messages (sent to AI).

## Report Object Schema

```
{
  "id": string,          // 8-char hex, unique
  "photo": string|null,  // image URL or base64
  "lat": float,          // latitude
  "lng": float,          // longitude
  "address": string,     // street address
  "city": string|null,
  "district": string|null,
  "severity": "Small"|"Medium"|"Critical",
  "description": string,
  "userId": string|null, // Telegram user ID
  "phoneNumber": string|null,
  "createdAt": string,   // ISO 8601 timestamp
  "status": "Pending"|"In Progress"|"Fixed",
  "votes": integer
}
```

## Environment Variables

- TELEGRAM_BOT_TOKEN — Telegram bot token
- ADMIN_CHAT_ID — Telegram chat ID for admin notifications
- BACKEND_URL — Public URL of this backend (for webhook setup)
- WEB_APP_URL — URL of the Telegram Mini App
- OLLAMA_API_KEY — API key for Ollama cloud
- OLLAMA_BASE_URL — Ollama base URL (default: http://localhost:11434)
- LLM_MODEL — LLM model name (default: gemma4:e4b)
- EMBED_MODEL — Embedding model name (default: nomic-embed-text-v2-moe)
