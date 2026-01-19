# AI Life Tracker - Development Guidelines

## Projekt-Übersicht

Full-Stack Life Tracker mit AI-Chat-Interface:
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Clerk Auth, Google Gemini
- **Frontend:** React, TypeScript, TanStack Router

## Development Workflow

### Bei jeder Code-Änderung diese Schritte befolgen:

#### 1. Vor dem Implementieren
- [ ] Verstehe die Anforderung vollständig
- [ ] Identifiziere betroffene Dateien und deren Abhängigkeiten
- [ ] **Nutze `ref` MCP um Best Practices und aktuelle Dokumentation zu prüfen**
- [ ] Plane die Testfälle BEVOR du Code schreibst (TDD)

#### 2. Test-First Ansatz
```bash
# Schreibe zuerst den Test
# Test muss zunächst FEHLSCHLAGEN (Red)
cd backend && uv run pytest tests/ -v --tb=short

# Dann implementiere den Code bis der Test GRÜN ist (Green)
# Dann refactore wenn nötig (Refactor)
```

#### 3. Nach der Implementierung
```bash
# Backend: Tests + Type Check + Lint
cd backend && uv run pytest tests/ -v && uv run pyright app/ && uv run ruff check app/

# Frontend: Type Check + Lint
cd frontend && pnpm typecheck && pnpm lint
```

#### 4. Vor dem Commit
- [ ] Alle Tests grün
- [ ] Keine Type-Errors
- [ ] Keine Lint-Errors
- [ ] Code Review der eigenen Änderungen

#### 5. Nach Abschluss des Tasks
- [ ] **IMMER `HANDOVER.md` aktualisieren** mit:
  - Was wurde implementiert/geändert
  - Offene Punkte oder bekannte Issues
  - Nächste Schritte für den nächsten Entwickler

---

## Testing Standards

**WICHTIG:** Lies `/TESTING_GUIDELINES.md` für vollständige Test-Richtlinien.

### Kernregeln
1. **Verhalten testen, nicht Implementation**
2. **Aussagekräftige Testnamen:** `test_<was>_<unter_welchen_umständen>_<erwartetes_ergebnis>`
3. **Arrange-Act-Assert Struktur**
4. **Keine Logik in Tests** (keine Schleifen, keine Bedingungen)
5. **Tests müssen isoliert sein** (kein geteilter Zustand)

### Test-Checkliste
Vor jedem Test-Commit:
- [ ] Würde der Test fehlschlagen wenn das Verhalten kaputt ist?
- [ ] Ist der Test unabhängig von anderen Tests?
- [ ] Beschreibt der Testname das erwartete Verhalten?

---

## Code-Struktur

```
backend/
  app/
    models/       # SQLAlchemy Models
    routers/      # FastAPI Endpoints
    services/     # Business Logic ← Hier Tests fokussieren
    schemas/      # Pydantic Schemas
  tests/
    conftest.py   # Gemeinsame Fixtures
    test_*.py     # Unit Tests

frontend/
  src/
    components/   # React Components
    routes/       # TanStack Router Pages
    api/          # API Client
    lib/          # Utilities
```

---

## Befehle

### Backend
```bash
cd backend

# Development Server
uv run uvicorn app.main:app --reload

# Tests ausführen
uv run pytest tests/ -v
uv run pytest tests/ -v --cov=app --cov-report=term-missing

# Type Checking
uv run pyright app/

# Linting & Formatting
uv run ruff check app/
uv run ruff format app/

# Datenbank Migration
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "description"
```

### Frontend
```bash
cd frontend

# Development Server
pnpm dev

# Type Checking
pnpm typecheck

# Linting
pnpm lint
```

---

## Wichtige Dateien

| Datei | Beschreibung |
|-------|--------------|
| `backend/app/services/entry.py` | Entry & Tracker Business Logic |
| `backend/app/services/context.py` | Workout Context Management |
| `backend/app/services/ai.py` | Gemini AI Integration |
| `backend/app/auth.py` | Clerk Authentication |
| `TESTING_GUIDELINES.md` | Vollständige Test-Richtlinien |

---

## Workflow für neue Features

### 1. Feature verstehen
- Was ist das gewünschte Verhalten?
- Welche Edge Cases gibt es?
- Welche bestehenden Komponenten sind betroffen?

### 2. Tests schreiben (TDD)
```python
# tests/test_neue_feature.py

def test_feature_verhält_sich_korrekt_bei_normalem_input():
    # Arrange
    # Act  
    # Assert
    pass  # Test schlägt fehl - gut!

def test_feature_behandelt_edge_case():
    pass

def test_feature_gibt_fehler_bei_ungültigem_input():
    pass
```

### 3. Implementieren
- Minimaler Code um Tests grün zu machen
- Keine vorzeitige Optimierung

### 4. Refactoring
- Code aufräumen
- Duplikation entfernen
- Tests müssen weiterhin grün bleiben

### 5. Integration prüfen
- **E2E Tests mit `chrome-devtools` MCP** (Browser-Verifikation)
- Alle Tests ausführen
- Type Check + Lint

---

## MCP Server Nutzung

### `ref` - Dokumentation & Best Practices
**IMMER nutzen vor der Implementierung** um sicherzustellen, dass der Lösungsansatz aktuell und korrekt ist.

```
Use ref to look up [Thema/Library/API]
Use ref to verify best practices for [Implementierung]
```

Beispiele:
- `Use ref to look up FastAPI dependency injection patterns`
- `Use ref to verify React Query mutation best practices`
- `Use ref to check SQLAlchemy 2.0 async session handling`

### `chrome-devtools` - E2E Testing & Debugging
**Nutzen für Browser-Verifikation** nach Frontend-Änderungen.

```
Check if localhost:5173 loads correctly
Verify the form submission on localhost:5173/trackers
Check the LCP of localhost:5173
```

Verfügbare Funktionen:
- **Performance-Traces:** LCP, Ladezeiten analysieren
- **Netzwerk-Analyse:** CORS-Probleme, fehlgeschlagene Requests
- **Konsolen-Logs:** JavaScript-Fehler identifizieren
- **DOM/CSS Inspektion:** Layout-Probleme debuggen
- **User-Flows:** Formulare testen, Navigation prüfen

---

## Don'ts

- **Keine Tests ohne Assertions**
- **Keine Tests die immer grün sind**
- **Keine Implementation ohne Test**
- **Keine globalen Variablen in Tests**
- **Keine Tests die von Reihenfolge abhängen**
- **Keine print() Statements im Code lassen**
- **Keine Implementierung ohne `ref` MCP Recherche bei unklaren Best Practices**
