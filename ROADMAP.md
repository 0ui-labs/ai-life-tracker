# AI Life Tracker - Roadmap

> **Core Philosophy:** Voice-First, Zero Learning Curve
> Die AI ist das Interface - nicht Buttons und Menüs.

---

## V1 - MVP (Core Experience)

### Voice-First Interface
- [ ] Voice Input als primäres Interface
- [ ] Kontext-Engine (App weiß immer wo User ist)
- [ ] Smart Parsing ("95, 12" / "12" / "nächste")
- [ ] Minimal UI - ein Screen während Workout
- [ ] AI Chat für komplexere Interaktionen

### Flexibles Tracker-System
- [ ] User definiert eigene Tracker (Gym, Habits, alles)
- [ ] Dynamische Schemas - AI fragt wie getrackt werden soll
- [ ] Kategorien: Fitness, Cardio, Habits, Gesundheit, Produktivität, etc.
- [ ] Tracking-Typen: Gewicht×Sätze×Reps, Zeit, Distanz, Zähler, Freitext

### Generative UI
- [ ] Vorgefertigte Komponenten (list, chart, stat-card, etc.)
- [ ] AI wählt passende Komponente + Daten
- [ ] Konsistentes Design, performant

### Routine Management
- [ ] Mehrere Trainings-Routinen verwalten
- [ ] Easy Switching zwischen Routinen
- [ ] Vordefinierte Templates (PPL, Bro Split, 5×5, Dorian Yates HIT, etc.)
- [ ] Custom Routinen erstellen via AI

### Tech Stack
- [ ] Python + FastAPI Backend
- [ ] PostgreSQL Datenbank
- [ ] Clerk Auth
- [ ] Google Gemini API
- [ ] Web Frontend (Mobile-optimiert)

---

## V2 - Planung & Kalender

### Kalender-Ansicht
- [ ] Tages/Wochen/Monatsansicht
- [ ] Geplant vs Getrackt visualisiert
- [ ] Workouts + Habits + alles in einem Kalender

### Scheduling
- [ ] Wiederkehrende Events ("Jeden Mo/Mi/Fr Krafttraining")
- [ ] Verknüpfung: geplant ↔ getrackt
- [ ] Verschieben/Anpassen via Voice ("Verschieb auf morgen")

### AI Briefings
- [ ] Morgen-Briefing: "Heute steht an: Leg Day, Meditation"
- [ ] Erinnerungen / Push Notifications
- [ ] Proaktive Nachfragen bei verpassten Events

---

## V3 - Analytics & AI Coach

### Auswertungen
- [ ] Flexible Abfragen: "Wieviel kg im März bewegt?"
- [ ] Trend-Analyse: Fortschritt über Zeit
- [ ] Visualisierungen: Charts, Heatmaps, Stat Cards

### Session-Analyse
- [ ] AI analysiert Workout nach Abschluss
- [ ] Erkennt: Regression, Fatigue, PRs
- [ ] Fragt nach subjektiven Daten (Energie, Mood, RPE)

### Intelligente Empfehlungen
- [ ] Korrelationen erkennen (Schlaf ↔ Performance)
- [ ] Proaktive Tipps: Deload, Regeneration, Plateau
- [ ] Supplement/Nutrition Hinweise (Creatin, Kaffee, etc.)
- [ ] Auto-Progression Vorschläge

### Reviews
- [ ] Wochen-Zusammenfassung
- [ ] Monats-Report mit Insights
- [ ] Langzeit-Trends

---

## V4 - Social & Matching

### Gym-Partner Matching
- [ ] Privacy-first, Double Opt-in
- [ ] Anonyme Profile (nur Gym, Zeiten, Trainingsstil)
- [ ] Kein Katalog - nur AI-vorgeschlagene Matches
- [ ] Matching basiert auf: Gym, Zeiten, Fokus, Level

### Communication
- [ ] In-App Chat nach Match
- [ ] Workout-Verabredungen
- [ ] Gemeinsame Workouts tracken

### Safety
- [ ] Block/Report Funktion
- [ ] Keine Echtzeit-Location
- [ ] Verifizierung über Gym Check-ins

### Erweitert
- [ ] Spotter-Anfragen (kurzfristig)
- [ ] Partner-Bewertungen nach X Workouts
- [ ] Kleine Trainingsgruppen bilden

---

## V5 - Gamification & Community

### Motivation
- [ ] Streaks (Tage in Folge)
- [ ] Achievements ("100 Workouts", "1 Jahr dabei", "PR König")
- [ ] Progress Visualisierung

### Challenges
- [ ] 30-Tage Challenges (solo)
- [ ] Challenges mit Partner/Gruppe
- [ ] Community Challenges

### Social
- [ ] Leaderboards (Opt-in, unter Freunden)
- [ ] Gruppen/Crews
- [ ] Workout-Templates teilen

---

## V6 - Premium & Erweiterungen

### Advanced Features
- [ ] AI-generierte komplette Workout-Pläne
- [ ] Periodisierung automatisch
- [ ] Ernährungs-Integration (Kalorien, Makros)

### Integrations
- [ ] Wearable Sync (Apple Watch, Garmin, Fitbit)
- [ ] Apple Health / Google Fit
- [ ] MyFitnessPal, etc.

### Pro Features
- [ ] Export (CSV, PDF Reports)
- [ ] API für eigene Integrationen
- [ ] Trainer-Modus (Coaches betreuen Clients)
- [ ] Team/Gym Accounts

---

## Technische Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│   Mobile-optimierte Web App (PWA)                           │
│   Voice Input → AI → Generative UI Components               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                      FastAPI Backend                         │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│   │   Auth   │  │    AI    │  │ Tracker  │  │  Calendar  │ │
│   │  (Clerk) │  │ (Gemini) │  │  Engine  │  │   Engine   │ │
│   └──────────┘  └──────────┘  └──────────┘  └────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┘
│                     PostgreSQL                               │
│   Users │ Trackers │ Entries │ Routines │ Schedules │ ...  │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack & Tooling

### Frontend
| Kategorie | Tool | Zweck |
|-----------|------|-------|
| Framework | React | UI Library |
| Build | Vite | Schneller Dev Server + Build |
| Routing | TanStack Router | Type-safe Routing |
| Server State | TanStack Query | API Calls, Caching |
| Client State | Zustand | Leichtgewichtig |
| Styling | Tailwind CSS | Utility-first CSS |
| UI Components | shadcn/ui | Kopierte, anpassbare Komponenten |
| PWA | vite-plugin-pwa | Offline-fähig, installierbar |

### Frontend Tooling
| Kategorie | Tool | Zweck |
|-----------|------|-------|
| Package Manager | pnpm | Schnell, disk-effizient |
| Linting + Formatting | Biome | All-in-one, extrem schnell |
| Type Checking | TypeScript | Type Safety |
| Testing | Vitest | Unit Tests (Vite-native) |
| E2E Testing | Playwright | End-to-End Tests |
| Git Hooks | Husky + lint-staged | Pre-commit Checks |
| API Mocking | MSW | Mock Service Worker für Dev |

### Backend
| Kategorie | Tool | Zweck |
|-----------|------|-------|
| Framework | FastAPI | Async Python API |
| ORM | SQLAlchemy | Database Models |
| Migrations | Alembic | Schema Migrations |
| Auth | Clerk | Hosted Authentication |
| AI | Google Gemini API | LLM für Chat + Parsing |

### Backend Tooling
| Kategorie | Tool | Zweck |
|-----------|------|-------|
| Package Manager | uv | Schneller als pip/poetry |
| Linting + Formatting | Ruff | Extrem schnell, all-in-one |
| Type Checking | Pyright | Strikte Type Checks |
| Testing | Pytest | Standard für Python |

### DevOps / Infra
| Kategorie | Tool | Zweck |
|-----------|------|-------|
| Containerization | Docker | Konsistente Environments |
| Local DB | Docker Compose | PostgreSQL lokal |
| Env Management | direnv + .env | Environment Variables |
| CI/CD | GitHub Actions | Automated Testing + Deploy |

---

## Projektstruktur

```
ai-life-tracker/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/              # shadcn Komponenten
│   │   │   ├── generative/      # AI UI Komponenten
│   │   │   │   ├── List.tsx
│   │   │   │   ├── Chart.tsx
│   │   │   │   ├── StatCard.tsx
│   │   │   │   ├── CalendarHeatmap.tsx
│   │   │   │   ├── ProgressRing.tsx
│   │   │   │   └── WorkoutScreen.tsx
│   │   │   └── voice/
│   │   │       └── VoiceButton.tsx
│   │   ├── hooks/
│   │   │   ├── useVoice.ts
│   │   │   └── useAI.ts
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── routes/
│   │   ├── stores/
│   │   └── App.tsx
│   ├── biome.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI App
│   │   ├── database.py          # PostgreSQL Connection
│   │   ├── models/              # SQLAlchemy Models
│   │   │   ├── user.py
│   │   │   ├── tracker.py
│   │   │   ├── entry.py
│   │   │   ├── routine.py
│   │   │   └── schedule.py
│   │   ├── routers/             # API Endpoints
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── trackers.py
│   │   │   └── entries.py
│   │   ├── services/
│   │   │   ├── ai.py            # Gemini Integration
│   │   │   └── context.py       # Kontext-Engine
│   │   └── schemas/             # Pydantic Schemas
│   ├── alembic/                 # Migrations
│   ├── tests/
│   ├── pyproject.toml
│   └── ruff.toml
│
├── docker-compose.yml           # PostgreSQL + Dev Setup
├── .github/
│   └── workflows/
│       └── ci.yml
├── .husky/
├── .env.example
└── README.md
```

## Datenmodell (Core)

```sql
-- Tracker Definition (flexibel für alles)
Tracker {
  id
  user_id
  name ("Bench Press", "Meditation", "Wasser")
  category (fitness, habit, health, productivity...)
  schema JSON (welche Felder, welche Typen)
  icon
  color
}

-- Einzelne Einträge
Entry {
  id
  tracker_id
  user_id
  timestamp
  data JSON (die tatsächlichen Werte)
  notes
  scheduled_event_id (optional: war geplant?)
}

-- Trainings-Routinen
Routine {
  id
  user_id
  name ("Push/Pull/Legs", "Dorian Yates HIT")
  type (template, custom)
  config JSON (Übungen, Reihenfolge, Sätze, etc.)
  is_active
}

-- Geplante Events
ScheduledEvent {
  id
  user_id
  tracker_id / routine_id
  recurrence (RRULE Format)
  time
  reminder_settings
}

-- Gym Partner Matching
MatchProfile {
  id
  user_id
  gym_name
  gym_location
  preferred_times
  training_style
  experience_level
  is_active
  is_anonymous (true bis Match)
}
```
