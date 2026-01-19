# AI Life Tracker - API Dokumentation

> **Stand:** 19. Januar 2026  
> **Version:** 0.1.0 (MVP in Entwicklung)

---

## Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Was ist ein Endpoint?](#was-ist-ein-endpoint)
3. [Alle Endpoints im Detail](#alle-endpoints-im-detail)
   - [Chat Endpoints](#chat-endpoints)
   - [Tracker Endpoints](#tracker-endpoints)
   - [Entry Endpoints](#entry-endpoints)
4. [Authentifizierung](#authentifizierung)
5. [Implementierungsstatus](#implementierungsstatus)
6. [Bekannte Einschränkungen](#bekannte-einschränkungen)
7. [Voraussetzungen](#voraussetzungen)

---

## Übersicht

Der AI Life Tracker ist eine Voice-First App zum Tracken von allem Möglichen - Workouts, Gewohnheiten, Gesundheit, Produktivität. Die AI ist das Hauptinterface: Du sprichst oder tippst, und die AI versteht und speichert automatisch.

### Architektur-Überblick

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│   React + TanStack Router + Tailwind                        │
│   Voice Input → Chat UI → Generative UI Components          │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/JSON
┌─────────────────────▼───────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│   │   Auth   │  │    AI    │  │ Tracker  │  │  Context   │ │
│   │  (Clerk) │  │ (Gemini) │  │  CRUD    │  │  Engine    │ │
│   └──────────┘  └──────────┘  └──────────┘  └────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │ SQL
┌─────────────────────▼───────────────────────────────────────┐
│                     PostgreSQL                               │
│   users │ trackers │ entries │ routines │ scheduled_events  │
└─────────────────────────────────────────────────────────────┘
```

---

## Was ist ein Endpoint?

Stell dir einen Endpoint wie einen **Schalter am Postamt** vor:
- Du gehst zum Schalter (Endpoint)
- Sagst was du willst (Anfrage)
- Bekommst eine Antwort zurück

Die App hat verschiedene "Schalter" für verschiedene Aufgaben.

### HTTP-Methoden erklärt

| Methode | Bedeutung | Alltags-Analogie |
|---------|-----------|------------------|
| `GET` | Daten abrufen | "Zeig mir meine Tracker" |
| `POST` | Etwas Neues erstellen | "Erstelle einen neuen Tracker" |
| `PUT` | Etwas Bestehendes ändern | "Ändere den Namen des Trackers" |
| `DELETE` | Etwas löschen | "Lösche diesen Tracker" |

---

## Alle Endpoints im Detail

### Chat Endpoints

Diese Endpoints sind für die AI-Kommunikation zuständig.

---

#### `POST /api/chat`

**Was macht es?**  
Verarbeitet deine Sprach- oder Texteingabe durch die AI.

**Alltags-Beispiel:**
> Du sagst: *"Bankdrücken 80kg, 3 Sätze, 10 Wiederholungen"*
> 
> Die AI versteht das, speichert es automatisch und antwortet:
> *"Super! Ich habe dein Bankdrücken getrackt: 80kg × 3 × 10"*

**Technische Details:**
```
Anfrage:
{
  "message": "Bankdrücken 80kg, 3x10",
  "context": {}  // Optional: zusätzlicher Kontext
}

Antwort:
{
  "action": "track",
  "message": "Gespeichert: Bankdrücken 3×10 mit 80kg",
  "data": {"sets": 3, "reps": 10, "weight": 80},
  "component": "confirmation",
  "tracker": "Bankdrücken"
}
```

**Mögliche Actions:**
- `track` - Daten wurden getrackt
- `chat` - Normale Konversation
- `query` - Abfrage von Daten
- `error` - Fehler aufgetreten

**Mögliche Components:**
- `confirmation` - Bestätigungs-Karte
- `list` - Liste von Einträgen
- `stat-card` - Statistik-Karte
- `null` - Nur Text

---

#### `POST /api/chat/workout/start`

**Was macht es?**  
Startet eine Workout-Session.

**Alltags-Beispiel:**
> Du sagst: *"Starte Push Day"*
> 
> Ab jetzt weiß die App: Du trainierst gerade. Wenn du später nur *"12"* sagst, versteht sie: Das sind 12 Wiederholungen der aktuellen Übung mit dem letzten Gewicht.

**Warum braucht man das?**  
Ohne aktive Session müsstest du jedes Mal sagen: *"Bankdrücken, 80kg, 12 Wiederholungen"*. Mit Session reicht: *"12"* - die App erinnert sich an Übung und Gewicht.

**Technische Details:**
```
Anfrage: POST /api/chat/workout/start?routine_name=Push%20Day

Antwort:
{
  "status": "started",
  "routine": "Push Day"
}
```

---

#### `POST /api/chat/workout/end`

**Was macht es?**  
Beendet deine Workout-Session und gibt eine Zusammenfassung.

**Alltags-Beispiel:**
> Du sagst: *"Workout beenden"*
> 
> Die App antwortet:
> *"Workout abgeschlossen! 45 Minuten, 5 Übungen, 2.400kg Gesamtvolumen"*

**Technische Details:**
```
Anfrage: POST /api/chat/workout/end

Antwort:
{
  "status": "ended",
  "summary": {
    "duration": 45,
    "exercises_completed": 5,
    "total_volume": 2400
  }
}
```

---

#### `GET /api/chat/context`

**Was macht es?**  
Zeigt den aktuellen Kontext (hauptsächlich für Entwickler/Debugging).

**Alltags-Beispiel:**
> Entwickler will wissen: "Was weiß die App gerade über den User?"
> 
> Antwort zeigt: Aktuelle Übung ist Bankdrücken, letztes Gewicht 80kg, Set 2 von 3

**Technische Details:**
```
Anfrage: GET /api/chat/context

Antwort:
{
  "workout_active": true,
  "current_exercise": "Bankdrücken",
  "last_weight": 80,
  "current_set": 2,
  "workout_started": "2026-01-19T10:30:00"
}
```

---

#### `GET /api/chat/history`

**Was macht es?**  
Holt deine letzten Tracking-Einträge.

**Alltags-Beispiel:**
> Du fragst: *"Was habe ich diese Woche trainiert?"*
> 
> Die App schaut in deine History und zeigt alle Einträge.

**Technische Details:**
```
Anfrage: GET /api/chat/history?tracker=Bankdrücken&limit=10

Antwort:
[
  {
    "id": "uuid-123",
    "tracker_id": "uuid-456",
    "data": {"weight": 85, "reps": 8, "sets": 3},
    "notes": null,
    "timestamp": "2026-01-19T10:45:00"
  },
  ...
]
```

**Query Parameter:**
- `tracker` (optional) - Filter nach Tracker-Name
- `limit` (optional, default: 20) - Anzahl der Einträge

---

### Tracker Endpoints

Tracker sind wie **Kategorien/Ordner** für verschiedene Dinge, die du tracken willst.

---

#### `GET /api/trackers`

**Was macht es?**  
Zeigt alle deine Tracker an.

**Alltags-Beispiel:**
> Du öffnest die Tracker-Seite und siehst:
> - 💪 Bankdrücken (Fitness)
> - 💧 Wasser trinken (Gesundheit)
> - 🧘 Meditation (Gewohnheit)

**Technische Details:**
```
Anfrage: GET /api/trackers

Antwort:
[
  {
    "id": "uuid-123",
    "name": "Bankdrücken",
    "category": "fitness",
    "schema": {},
    "icon": "💪",
    "color": "#3b82f6",
    "created_at": "2026-01-15T08:00:00"
  },
  ...
]
```

---

#### `POST /api/trackers`

**Was macht es?**  
Erstellt einen neuen Tracker.

**Alltags-Beispiel:**
> Du willst anfangen, deinen Kaffeekonsum zu tracken.
> 
> Du erstellst: *"Kaffee"* mit Kategorie *"Gesundheit"* und Icon ☕

**Technische Details:**
```
Anfrage:
{
  "name": "Kaffee",
  "category": "health",
  "schema": {},
  "icon": "☕",
  "color": "#8B4513"
}

Antwort:
{
  "id": "uuid-789",
  "name": "Kaffee",
  "category": "health",
  "schema": {},
  "icon": "☕",
  "color": "#8B4513",
  "created_at": "2026-01-19T11:00:00"
}
```

**Verfügbare Kategorien:**
- `fitness` - Sport und Training
- `health` - Gesundheit (Schlaf, Wasser, etc.)
- `habit` - Gewohnheiten
- `productivity` - Produktivität
- `general` - Alles andere

---

#### `GET /api/trackers/{id}`

**Was macht es?**  
Zeigt Details zu einem bestimmten Tracker.

**Alltags-Beispiel:**
> Du klickst auf deinen "Bankdrücken" Tracker und siehst alle Details.

**Technische Details:**
```
Anfrage: GET /api/trackers/uuid-123

Antwort:
{
  "id": "uuid-123",
  "name": "Bankdrücken",
  "category": "fitness",
  "schema": {},
  "icon": "💪",
  "color": "#3b82f6",
  "created_at": "2026-01-15T08:00:00"
}
```

---

#### `PUT /api/trackers/{id}`

**Was macht es?**  
Ändert einen bestehenden Tracker.

**Alltags-Beispiel:**
> Du merkst: "Bankdrücken" sollte besser "Flachbankdrücken" heißen.
> 
> Du änderst den Namen - alle bisherigen Einträge bleiben erhalten.

**Technische Details:**
```
Anfrage:
{
  "name": "Flachbankdrücken"  // Nur geänderte Felder nötig
}

Antwort:
{
  "id": "uuid-123",
  "name": "Flachbankdrücken",  // Aktualisiert
  "category": "fitness",
  "schema": {},
  "icon": "💪",
  "color": "#3b82f6",
  "created_at": "2026-01-15T08:00:00"
}
```

**Sicherheit:** Du kannst nur eigene Tracker bearbeiten (403 Fehler bei fremden).

---

#### `DELETE /api/trackers/{id}`

**Was macht es?**  
Löscht einen Tracker und alle seine Einträge.

**Alltags-Beispiel:**
> Du hast einen Test-Tracker erstellt und willst ihn loswerden.

**Technische Details:**
```
Anfrage: DELETE /api/trackers/uuid-123

Antwort:
{
  "message": "Tracker deleted successfully"
}
```

**Achtung:** Alle Einträge dieses Trackers werden auch gelöscht! Diese Aktion kann nicht rückgängig gemacht werden.

**Sicherheit:** Du kannst nur eigene Tracker löschen (403 Fehler bei fremden).

---

### Entry Endpoints

Entries sind die **einzelnen Einträge/Datenpunkte** innerhalb eines Trackers.

---

#### `GET /api/trackers/{id}/entries`

**Was macht es?**  
Zeigt alle Einträge eines Trackers.

**Alltags-Beispiel:**
> Du öffnest deinen "Bankdrücken" Tracker und siehst den Verlauf:
> - 19.01.: 85kg × 3 × 8
> - 17.01.: 82.5kg × 3 × 10
> - 15.01.: 80kg × 3 × 10

**Technische Details:**
```
Anfrage: GET /api/trackers/uuid-123/entries?limit=50

Antwort:
[
  {
    "id": "entry-uuid-1",
    "tracker_id": "uuid-123",
    "data": {"weight": 85, "reps": 8, "sets": 3},
    "notes": "Fühlte sich schwer an",
    "timestamp": "2026-01-19T10:45:00",
    "created_at": "2026-01-19T10:45:00"
  },
  ...
]
```

---

#### `POST /api/trackers/{id}/entries`

**Was macht es?**  
Fügt einen neuen Eintrag manuell hinzu.

**Alltags-Beispiel:**
> Du hast gestern vergessen zu tracken und willst es nachtragen.

**Technische Details:**
```
Anfrage:
{
  "data": {"weight": 80, "reps": 10, "sets": 3},
  "notes": "Nachgetragen",
  "timestamp": "2026-01-18T10:00:00"  // Optional, sonst jetzt
}

Antwort:
{
  "id": "entry-uuid-new",
  "tracker_id": "uuid-123",
  "data": {"weight": 80, "reps": 10, "sets": 3},
  "notes": "Nachgetragen",
  "timestamp": "2026-01-18T10:00:00",
  "created_at": "2026-01-19T11:30:00"
}
```

**Hinweis:** Normalerweise erstellt die AI Entries automatisch über `/api/chat`. Dieser Endpoint ist für manuelle Nachträge.

---

## Authentifizierung

Alle Endpoints (außer Dokumentation) erfordern eine Anmeldung über **Clerk**.

### Wie funktioniert es?

1. User meldet sich im Frontend an (Clerk UI)
2. Frontend erhält JWT Token von Clerk
3. Bei jedem API-Call wird der Token im Header mitgeschickt:
   ```
   Authorization: Bearer eyJhbGc...
   ```
4. Backend validiert den Token und identifiziert den User

### Warum Authentifizierung?

- **Datenschutz:** Deine Daten gehören nur dir
- **Sicherheit:** Niemand kann deine Tracker sehen oder ändern
- **Multi-Device:** Du kannst von mehreren Geräten auf deine Daten zugreifen

### Fehler-Codes

| Code | Bedeutung |
|------|-----------|
| 401 | Nicht angemeldet oder Token abgelaufen |
| 403 | Angemeldet, aber keine Berechtigung (z.B. fremder Tracker) |

---

## Implementierungsstatus

### Vollständig implementiert und funktionsfähig

| Endpoint | Status | Tests |
|----------|--------|-------|
| `POST /api/chat` | ✅ Funktioniert | ✅ |
| `POST /api/chat/workout/start` | ✅ Funktioniert | ✅ |
| `POST /api/chat/workout/end` | ✅ Funktioniert | ✅ |
| `GET /api/chat/context` | ✅ Funktioniert | ✅ |
| `GET /api/chat/history` | ✅ Funktioniert | ✅ |
| `GET /api/trackers` | ✅ Funktioniert | ✅ |
| `POST /api/trackers` | ✅ Funktioniert | ✅ |
| `GET /api/trackers/{id}` | ✅ Funktioniert | ✅ |
| `PUT /api/trackers/{id}` | ✅ Funktioniert | ✅ |
| `DELETE /api/trackers/{id}` | ✅ Funktioniert | ✅ |
| `GET /api/trackers/{id}/entries` | ✅ Funktioniert | ✅ |
| `POST /api/trackers/{id}/entries` | ✅ Funktioniert | ✅ |

### Noch nicht implementiert

| Feature | Geplant für |
|---------|-------------|
| `GET/POST /api/routines` | V1 |
| `GET/POST /api/schedule` | V2 |
| `GET /api/analytics` | V3 |

---

## Bekannte Einschränkungen

### 1. AI-Parsing nicht 100% zuverlässig

**Problem:**  
Die AI (Gemini) versucht JSON zurückzugeben, aber manchmal antwortet sie mit Freitext statt strukturiertem JSON.

**Auswirkung:**  
Nicht jede Eingabe wird zuverlässig als Tracking erkannt.

**Beispiele:**
```
✅ "80kg Bankdrücken" → Wird meist erkannt
✅ "3x10 mit 80kg" → Wird meist erkannt
⚠️ "hab grad trainiert" → Unklar, was getrackt werden soll
⚠️ "war gut heute" → Keine Daten extrahierbar
```

**Workaround:**  
Klare, strukturierte Eingaben nutzen mit Zahlen und Übungsnamen.

---

### 2. Workout-Kontext mit Redis-Persistierung

**Lösung:**  
Der Workout-Kontext (aktive Session, aktuelle Übung, letztes Gewicht) wird in Redis gespeichert mit einem konfigurierbaren TTL (Time-To-Live).

**Verhalten:**  
- Sessions werden automatisch nach Ablauf des TTL gelöscht (Standard: 2 Stunden)
- Bei Server-Neustarts bleibt der Kontext erhalten, solange Redis läuft
- Jeder User hat seinen eigenen isolierten Kontext

**Einschränkungen:**
- Ohne laufende Redis-Instanz funktioniert die Kontextpersistierung nicht
- Nach TTL-Ablauf muss eine neue Workout-Session gestartet werden

---

### 3. Keine Schema-Validierung

**Problem:**  
Das `schema` Feld bei Trackern wird gespeichert, aber nicht zur Validierung von Entries genutzt.

**Auswirkung:**  
Man kann beliebige Daten in Entries speichern, auch wenn sie nicht zum definierten Schema passen.

**Beispiel:**
```
Tracker-Schema definiert: {weight: number, reps: number}
Entry speichert: {foo: "bar", random: 123}  → Wird trotzdem akzeptiert
```

---

### 4. Keine Pagination

**Problem:**  
Bei vielen Einträgen werden alle auf einmal geladen (nur durch `limit` begrenzt).

**Auswirkung:**  
Bei sehr vielen Einträgen könnte die Performance leiden.

**Workaround:**  
`limit` Parameter nutzen.

---

## Voraussetzungen

### Environment Variables

```bash
# Backend (.env)
GEMINI_API_KEY=AIza...           # Google AI Studio API Key
CLERK_SECRET_KEY=sk_test_...     # Clerk Backend API Key
DATABASE_URL=postgresql://...     # PostgreSQL Connection String

# Frontend (.env oder frontend/.env)
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...  # Clerk Frontend Key
```

### Services starten

```bash
# 1. Datenbank starten
docker-compose up -d

# 2. Migrations anwenden
cd backend
uv run alembic upgrade head

# 3. Backend starten
uv run uvicorn app.main:app --reload

# 4. Frontend starten (neues Terminal)
cd frontend
pnpm dev
```

### URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Dokumentation (Swagger) | http://localhost:8000/docs |
| API Dokumentation (ReDoc) | http://localhost:8000/redoc |

---

## Wie hängt alles zusammen?

```
User spricht: "Bankdrücken 80kg, 10 Reps"
        │
        ▼
┌───────────────────────────────────────┐
│  Frontend sendet POST /api/chat       │
│  Body: {"message": "Bankdrücken..."}  │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│  Backend: AI Service (Gemini)         │
│  - Versteht die Eingabe               │
│  - Extrahiert: Tracker + Daten        │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│  Backend: Entry Service               │
│  - Sucht/Erstellt Tracker             │
│  - Speichert Entry in DB              │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│  Response an Frontend                 │
│  {                                    │
│    "action": "track",                 │
│    "message": "Getrackt!",            │
│    "component": "confirmation"        │
│  }                                    │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│  Frontend zeigt Confirmation-Card     │
│  "Bankdrücken: 80kg × 10 Reps ✓"     │
└───────────────────────────────────────┘
```

---

## Weiterführende Dokumentation

- **HANDOVER.md** - Projekt-Übergabe und Setup
- **ROADMAP.md** - Geplante Features
- **TESTING_GUIDELINES.md** - Test-Standards
- **CLAUDE.md** - Development Guidelines

---

*Letzte Aktualisierung: 19. Januar 2026*
