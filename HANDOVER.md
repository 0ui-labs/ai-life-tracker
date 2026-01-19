# AI Life Tracker - Projekt Übergabe

## Projektidee

Ein **universeller AI Life Tracker** mit Voice-First Interface. Der User spricht einfach mit der AI und sie trackt alles automatisch - Workouts, Habits, Gesundheit, Produktivität, etc.

### Core Philosophy
- **Voice-First, Zero Learning Curve** - Die AI ist das Interface, nicht Buttons und Menüs
- **Universell** - Nicht nur Gym, sondern alles trackbar (Habits, Schlaf, Wasser, Meditation, ...)
- **Kontextbewusst** - Minimale Eingabe reicht: User sagt "12" und App weiß es sind 12 Reps mit 80kg Bankdrücken
- **Generative UI** - AI wählt vorgefertigte UI-Komponenten (Listen, Charts, Cards) für konsistentes Design

---

## Aktueller Stand

### Was funktioniert:
- **Frontend**: React + Vite + TanStack Router + Tailwind v4
- **Backend**: FastAPI mit Gemini AI Integration + Context Engine
- **Datenbank**: PostgreSQL mit allen Tabellen (Migration angewendet)
- **UI**: Chat-Interface mit Voice Input + Text Input auf Homepage
- **Generative UI**: Confirmation, StatCard, List Components werden von AI gewählt

### Projektstruktur (aktuell):
```
ai-life-tracker/
├── frontend/
│   ├── src/
│   │   ├── routes/
│   │   │   ├── __root.tsx
│   │   │   └── index.tsx          # Chat UI mit Voice + Text
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   ├── button.tsx     # shadcn Button
│   │   │   │   └── card.tsx       # shadcn Card
│   │   │   ├── generative/
│   │   │   │   ├── index.ts
│   │   │   │   ├── Confirmation.tsx
│   │   │   │   ├── StatCard.tsx
│   │   │   │   ├── List.tsx
│   │   │   │   └── ChatMessage.tsx
│   │   │   └── voice/
│   │   │       └── VoiceButton.tsx
│   │   ├── hooks/
│   │   │   └── useVoice.ts        # Web Speech API
│   │   ├── lib/
│   │   │   └── utils.ts           # cn() helper
│   │   ├── stores/
│   │   │   └── workoutStore.ts
│   │   ├── api/
│   │   │   └── client.ts
│   │   └── index.css              # Tailwind v4 + Theme
│   ├── biome.json
│   ├── vite.config.ts
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── tracker.py
│   │   │   ├── entry.py
│   │   │   └── routine.py         # + ScheduledEvent
│   │   ├── routers/
│   │   │   ├── chat.py
│   │   │   └── trackers.py
│   │   ├── services/
│   │   │   ├── ai.py              # Gemini Integration
│   │   │   └── context.py         # Workout Context Engine
│   │   └── schemas/
│   │       ├── chat.py
│   │       └── tracker.py
│   ├── alembic/
│   │   └── versions/
│   │       └── 44333bd5c5d5_initial.py
│   ├── alembic.ini
│   └── pyproject.toml
│
├── docker-compose.yml
├── .env.example
├── ROADMAP.md
└── HANDOVER.md
```

---

## Tech Stack

### Frontend
- **React 19 + Vite 7** - Build & Dev
- **TanStack Router** - File-based Routing (auto-generiert `routeTree.gen.ts`)
- **TanStack Query** - Server State
- **Zustand** - Client State
- **Tailwind CSS v4** - mit `@tailwindcss/vite` Plugin
- **shadcn/ui** - Button, Card (manuell für Tailwind v4 konfiguriert)
- **Biome** - Linting + Formatting
- **lucide-react** - Icons

### Backend
- **FastAPI** - Python API
- **SQLAlchemy 2.0** - Async ORM
- **Alembic** - Migrations
- **PostgreSQL 16** - via Docker
- **Google Gemini** - AI/LLM (`gemini-1.5-flash`)
- **uv** - Package Manager
- **Ruff** - Linting

---

## Setup (Quick Start)

```bash
# 1. Environment
cp .env.example .env
# GEMINI_API_KEY eintragen!

# 2. Datenbank starten
docker-compose up -d

# 3. Backend
cd backend
uv sync
uv run alembic upgrade head    # Migration ist schon erstellt
uv run uvicorn app.main:app --reload

# 4. Frontend (neues Terminal)
cd frontend
pnpm install
pnpm dev
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## API Endpoints

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/chat` | POST | AI Chat - verarbeitet Spracheingabe, speichert Entries |
| `/api/chat/workout/start` | POST | Workout Session starten |
| `/api/chat/workout/end` | POST | Workout beenden, Summary |
| `/api/chat/context` | GET | Aktueller Kontext (Debug) |
| `/api/chat/history` | GET | Tracking History abrufen |
| `/api/trackers` | GET/POST | Tracker auflisten/erstellen |
| `/api/trackers/{id}` | GET | Einzelnen Tracker abrufen |
| `/api/trackers/{id}/entries` | GET/POST | Einträge für Tracker |

---

## Datenmodell (in DB)

```
users
├── id (String, PK)
├── email (unique)
├── name
├── created_at, updated_at

trackers
├── id (UUID, PK)
├── user_id (FK → users)
├── name, category
├── schema (JSON)
├── icon, color
├── created_at, updated_at

entries
├── id (UUID, PK)
├── user_id, tracker_id (FK)
├── data (JSON)
├── notes
├── scheduled_event_id
├── timestamp, created_at

routines
├── id (UUID, PK)
├── user_id (FK)
├── name, type
├── config (JSON)
├── is_active
├── created_at, updated_at

scheduled_events
├── id (UUID, PK)
├── user_id, tracker_id, routine_id (FK)
├── name, recurrence, time
├── reminder_settings (JSON)
├── is_active
├── created_at, updated_at
```

---

## Was noch fehlt / TODO

### Priorität 1 (für funktionierenden MVP):
- [x] **.env anlegen** - `GEMINI_API_KEY` eintragen
- [x] **Clerk Auth integrieren** - Komplett implementiert!

### Priorität 2 (V1 Features):
- [ ] Tracker CRUD im Frontend
- [x] Entries in DB speichern - Implementiert!
- [ ] Routine Management UI
- [ ] PWA Setup (vite-plugin-pwa)

### Priorität 3 (Nice to have):
- [ ] Tests (Vitest + Playwright)
- [ ] Error Boundaries
- [ ] Offline Support

---

## Clerk Auth Setup

Die Authentifizierung ist vollständig mit Clerk integriert:

### Keys einrichten:
1. Gehe zu https://dashboard.clerk.com und erstelle eine App
2. Kopiere die Keys in die `.env` Dateien:

```bash
# Backend .env
CLERK_SECRET_KEY=sk_test_xxxxx

# Frontend .env (oder frontend/.env)
VITE_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
```

### Wie es funktioniert:
- **Frontend**: `ClerkProvider` wraps die App, `AuthGuard` zeigt Login-Screen für unauthenticated Users
- **API Client**: Sendet automatisch `Authorization: Bearer <token>` Header
- **Backend**: `CurrentUser` Dependency validiert JWT und extrahiert User ID
- **User Sync**: User werden automatisch in der DB angelegt beim ersten API Call

### Relevante Dateien:
- `frontend/src/main.tsx` - ClerkProvider Setup
- `frontend/src/components/auth/AuthGuard.tsx` - Auth UI + Token Setup
- `frontend/src/api/client.ts` - API Client mit Auth Header
- `backend/app/auth.py` - JWT Validation + CurrentUser Dependency
- `backend/app/services/user.py` - User Sync Service

---

## Wichtige Code-Stellen

### AI Service (`backend/app/services/ai.py`)
- System Prompt definiert AI-Verhalten
- Parsed JSON-Responses für Generative UI
- Fallback auf Chat-Message bei Parse-Fehlern

### Context Engine (`backend/app/services/context.py`)
- Hält Workout-State in-memory (pro User)
- Trackt: aktuelle Übung, letztes Gewicht, Set-Nummer
- `start_workout()`, `end_workout()`, `record_set()`

### Chat Router (`backend/app/routers/chat.py`)
- Kombiniert AI + Context + DB-Persistierung
- Bei `action: "track"` werden Entries automatisch in DB gespeichert
- Tracker werden bei Bedarf automatisch erstellt
- Returned strukturierte Response mit `action`, `message`, `component`, `data`

### Entry Service (`backend/app/services/entry.py`)
- `save_entry()` - Speichert Tracking-Daten in DB
- `get_or_create_tracker()` - Erstellt Tracker automatisch wenn nicht vorhanden
- `get_recent_entries()` - Holt letzte Entries für History

### Frontend Chat (`frontend/src/routes/index.tsx`)
- Voice + Text Input
- Sendet an `/api/chat`
- Rendert AI-Response mit passender Generative UI Component

### Generative UI (`frontend/src/components/generative/`)
- `ChatMessage.tsx` - Dispatcher für UI Components
- Components: `Confirmation`, `StatCard`, `List`
- AI returned `component: "confirmation"` → Frontend rendert `<Confirmation />`

---

## Befehle Referenz

```bash
# Frontend
pnpm dev          # Dev Server (http://localhost:5173)
pnpm build        # Production Build
pnpm lint         # Biome Check
pnpm lint:fix     # Biome Fix

# Backend
uv sync           # Dependencies installieren
uv run uvicorn app.main:app --reload  # Dev Server
uv run alembic upgrade head           # Migrations anwenden
uv run alembic revision --autogenerate -m "message"  # Neue Migration
uv run ruff check .   # Linting
uv run ruff format .  # Formatting

# Docker
docker-compose up -d      # PostgreSQL starten
docker-compose down       # Stoppen
docker-compose logs -f    # Logs
```

---

## Roadmap Kurzfassung

| Version | Features |
|---------|----------|
| **V1 MVP** | Voice Input, flexibles Tracking, AI Chat, Routine Management |
| **V2** | Kalender, Planung, Erinnerungen, AI Briefings |
| **V3** | Analytics, AI Coach, Korrelationen |
| **V4** | Gym-Partner Matching |
| **V5** | Gamification, Streaks |
| **V6** | Premium, Wearables |

Vollständige Roadmap: `ROADMAP.md`
