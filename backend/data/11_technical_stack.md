# Technical Stack and Architecture

## Backend

- **Framework**: FastAPI (Python)
- **Database**: SQLite (local file: reports.db)
- **AI/LLM**: Ollama API (cloud) with configurable model (default: gemma4:e4b)
- **Embeddings**: FastEmbed with BAAI/bge-small-en-v1.5 model
- **Vector Store**: ChromaDB (local persistent storage in chroma_db/)
- **RAG Pipeline**: LangChain + ChromaDB for context retrieval
- **HTTP client**: httpx (async)
- **Document loaders**: LangChain (PDF, TXT, Markdown)

## Frontend

- **Framework**: Nuxt.js 4 (Vue.js 3)
- **Styling**: TailwindCSS
- **State management**: Pinia
- **Maps**: Leaflet.js with MarkerCluster plugin
- **Map tiles**: CartoCDN (light_all style)
- **Geocoding**: OpenStreetMap Nominatim API (reverse geocoding and address search)
- **Icons**: Lucide Vue Next
- **Form validation**: vee-validate + Zod
- **i18n**: @nuxtjs/i18n (Uzbek, Russian, English)
- **Telegram integration**: Telegram WebApp SDK

## AI Chat Architecture

1. User sends message via ChatWidget.vue or Telegram bot
2. POST /api/chat receives the message
3. RAG: ChromaDB is queried for relevant context (top 4 chunks)
4. Context is appended to the user message
5. Ollama API called with system prompt + enriched message
6. Response returned to user

## RAG (Retrieval Augmented Generation) System

- Documents stored in backend/data/ directory
- Supported formats: PDF (.pdf), Text (.txt), Markdown (.md)
- Documents are chunked: 800 characters per chunk, 150 character overlap
- Chunks embedded using FastEmbed (BAAI/bge-small-en-v1.5)
- Embeddings stored in ChromaDB (persistent)
- At startup: loads existing ChromaDB or builds from documents
- At query time: retrieves top 4 most relevant chunks

## Telegram Bot Integration

- Webhook-based (not polling)
- /start command shows welcome message with Mini App button
- All other text messages are processed by the AI
- Status change notifications sent via sendMessage API
- HTML parse mode for formatted messages

## Deployment Notes

- Backend: Python 3.14, uvicorn ASGI server
- Frontend: Nuxt.js, can be deployed as static site or Node.js server
- ChromaDB: local filesystem, needs persistent storage
- SQLite: local file, needs persistent storage
- Ollama: requires OLLAMA_API_KEY and OLLAMA_BASE_URL environment variables

## Navigation Structure

Bottom navigation bar with 4 tabs:
1. Home (/) — Interactive map with all reports
2. List (/list) — Card grid view of all reports
3. Report (/report) — Submit new report (4-step wizard)
4. My Reports (/my-reports) — User's own reports and profile

Floating elements:
- ChatWidget (bottom-left) — AI assistant chat button
- Report button on map — navigate to /report

## File Structure (Key Files)

```
backend/
  main.py              — FastAPI app, all routes, RAG, AI chat
  reports.db           — SQLite database
  data/                — RAG training documents
  chroma_db/           — ChromaDB vector store

components/
  AppMap.vue           — Interactive Leaflet map
  ChatWidget.vue       — AI chat floating widget
  PotholeCard.vue      — Report card component
  StatusBadge.vue      — Status color badge

pages/
  index.vue            — Map home page
  list.vue             — Reports list page
  report.vue           — Report submission wizard
  my-reports.vue       — User reports + profile
  admin/               — Admin panel pages

stores/
  reports.ts           — Pinia store for reports state

i18n/locales/
  uz.json              — Uzbek translations
  ru.json              — Russian translations
  en.json              — English translations
```
