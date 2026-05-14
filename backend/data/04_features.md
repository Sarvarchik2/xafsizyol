# Xafsizyol Features

## Interactive Map (Home Page)

The home page shows an interactive map with all submitted road reports across Uzbekistan.

- **Map markers** — each report is shown as a colored marker based on severity
- **Marker clustering** — nearby markers are grouped when zoomed out to keep the map readable
- **Tap a marker** — shows report details: photo, address, description, severity, status, votes
- **Filters** — filter reports by category directly on the map:
  - All (Hammasi / Все) — shows all reports
  - Critical (Xavfli / Критичные) — only Critical severity reports
  - Recent (Yaqinda / Недавние) — latest submitted reports sorted by date
  - Fixed (Tuzatilgan / Исправленные) — only resolved/fixed reports
- **Add report button** — "+" button navigates to the report submission form
- Map tiles provided by CartoCDN (light style)
- Geolocation support for centering map on user's position

## Report Submission Form (/report page)

4-step wizard for submitting a new road report:
1. Photo upload (required)
2. Location confirmation on map + address, city, district
3. Severity selection + phone number + description
4. Preview and submit

## Report List (/list page)

- Grid view of all reports as cards
- Filter by: All, Critical, Recent, Fixed (tab-based filter)
- Search/filter by city name
- Search/filter by district name
- Reports sorted by vote count (most voted first)
- Each card shows: photo, address, severity badge, vote count, status

## My Reports (/my-reports page)

- Shows the logged-in user's Telegram profile (name, avatar, username, phone)
- Lists all reports submitted by the current user
- Shows status of each report with color-coded badge
- Shows photo, address, description, severity, and submission date for each report
- Counter showing total number of reports submitted
- Empty state with link to submit a new report

## Voting System

- Any user can vote on any report
- Voting means "I have the same problem at this location"
- Vote count is shown on report cards and map popups
- More votes = higher priority for road authorities
- Vote button label: "Menda ham shu muammo" (I have this problem too)

## Telegram Bot Integration

- The Xafsizyol Telegram bot sends welcome message with Mini App button on /start
- Any text message sent to the bot gets an AI-powered reply
- Users receive automatic Telegram notifications when their report status changes
- Bot supports Uzbek, Russian, and English

## AI Chat Assistant

- Floating chat widget available on all pages (bottom-left corner)
- Users choose language first: Uzbek, Russian, or English
- Shows suggested FAQ questions
- Free text chat powered by local Ollama LLM with RAG (ChromaDB)
- Bot only answers questions about Xafsizyol app
- Available on both web and Telegram bot

## Admin Panel (/admin)

- Separate admin section protected by password
- Dashboard with statistics: total reports, pending count, in-progress count, fixed count
- Reports management: view all reports, update statuses
- Admin map: view all reports on map with ability to update status
- Status change triggers automatic Telegram notification to the report submitter
