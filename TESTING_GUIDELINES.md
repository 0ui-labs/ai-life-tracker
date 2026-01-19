# Testing Guidelines

Diese Richtlinien definieren die Qualitätsstandards für Tests in diesem Projekt. Ziel ist es, sinnvolle verhaltensbasierte Tests zu schreiben, die echte Sicherheit bieten - nicht Tests die nur existieren um "grün" zu sein.

## Grundprinzipien

1. **Tests beschreiben Verhalten, nicht Implementation**
2. **Jeder Test prüft genau eine Sache**
3. **Tests sind unabhängig und isoliert**
4. **Tests dienen als lebende Dokumentation**

---

## 1. Verhalten testen, nicht Implementation

Tests sollen brechen wenn sich das *Verhalten* ändert, nicht wenn sich interne Details ändern.

```python
# Schlecht - testet Implementation
def test_context_dict_has_workout_active_key():
    ctx = ContextEngine()
    assert "workout_active" in ctx._contexts[user_id]

# Gut - testet Verhalten
def test_workout_can_be_started_and_tracks_exercises():
    ctx = ContextEngine()
    ctx.start_workout(user_id, routine_name="Push Day")
    
    assert ctx.get_current_exercise(user_id) is not None
```

**Begründung:** Implementation kann sich ändern (Dict wird Dataclass, Variable wird umbenannt), das Verhalten sollte stabil bleiben.

---

## 2. Arrange-Act-Assert Struktur

Jeder Test folgt dieser klaren Struktur:

```python
def test_workout_duration_is_calculated_when_workout_ends():
    # Arrange - Setup mit klarem Kontext
    engine = ContextEngine()
    engine.start_workout(user_id="user-1", routine_name="Legs")
    
    # Act - Eine einzige Aktion
    summary = engine.end_workout(user_id="user-1")
    
    # Assert - Prüfe das erwartete Verhalten
    assert summary["duration"] is not None
    assert summary["exercises_completed"] == 0
```

**Begründung:** Wenn ein Test fehlschlägt, ist sofort klar was kaputt ist.

---

## 3. Aussagekräftige Testnamen

Testnamen erzählen die Story und beschreiben das erwartete Verhalten.

```python
# Schlecht
def test_save_entry():
def test_context_1():
def test_user_service():

# Gut  
def test_entry_is_saved_with_auto_detected_fitness_category():
def test_minimal_input_uses_last_weight_from_context():
def test_unknown_tracker_names_default_to_general_category():
```

**Begründung:** `pytest -v` Ausgabe sollte wie eine Spezifikation lesbar sein. Bei Fehlern sieht man sofort welches Verhalten nicht funktioniert.

---

## 4. Edge Cases und Fehlerfälle

Die meisten Bugs entstehen an den Grenzen. Diese explizit testen:

```python
def test_get_category_returns_general_for_unknown_tracker():
    assert get_category_for_tracker("Meine Katze füttern") == "general"

def test_end_workout_without_start_returns_empty_summary():
    engine = ContextEngine()
    summary = engine.end_workout(user_id="user-1")
    
    assert summary["duration"] is None
    assert summary["exercises_completed"] == 0

def test_calculate_duration_handles_none_start_time():
    engine = ContextEngine()
    assert engine._calculate_duration(None) is None
```

**Zu testende Edge Cases:**
- Leere Listen/Strings
- None-Werte
- Unerwartete Inputs
- Grenzwerte (0, negative Zahlen, sehr große Werte)
- Erstmaliger Aufruf vs. wiederholter Aufruf

---

## 5. Keine Logik im Test

Tests müssen so simpel sein, dass sie offensichtlich korrekt sind.

```python
# Schlecht - Test enthält eigene Logik
def test_category_detection():
    categories = {"bankdrücken": "fitness", "schlaf": "health"}
    for name, expected in categories.items():
        assert get_category_for_tracker(name) == expected

# Gut - Explizit und lesbar
def test_bankdruecken_is_categorized_as_fitness():
    assert get_category_for_tracker("bankdrücken") == "fitness"

def test_schlaf_is_categorized_as_health():
    assert get_category_for_tracker("Schlaf") == "health"
```

**Begründung:** Wenn der Test Logik enthält (Schleifen, Bedingungen), kann der Test selbst Bugs haben.

---

## 6. Unabhängige und isolierte Tests

Jeder Test muss unabhängig von anderen Tests laufen können.

```python
# Schlecht - Tests teilen Zustand
engine = ContextEngine()  # Globaler Zustand!

def test_start_workout():
    engine.start_workout("user-1")
    
def test_end_workout():  # Hängt vom vorherigen Test ab!
    summary = engine.end_workout("user-1")

# Gut - Jeder Test ist isoliert
def test_start_workout():
    engine = ContextEngine()
    engine.start_workout("user-1")
    assert engine.get_context("user-1")["workout_active"] is True

def test_end_workout_after_start():
    engine = ContextEngine()
    engine.start_workout("user-1")  # Eigenes Setup
    summary = engine.end_workout("user-1")
    assert summary is not None
```

**Begründung:** Tests können in beliebiger Reihenfolge oder parallel laufen. Geteilter Zustand führt zu flaky Tests.

---

## 7. Fixtures für Setup

Fixtures machen Setup wiederverwendbar und halten Tests fokussiert.

```python
@pytest.fixture
def context_engine():
    return ContextEngine()

@pytest.fixture  
def user_with_active_workout(context_engine):
    context_engine.start_workout("user-1", routine_name="Push")
    return "user-1"

def test_recording_set_increments_set_counter(context_engine, user_with_active_workout):
    context_engine.record_set(user_with_active_workout, weight=80, reps=10)
    
    ctx = context_engine.get_context(user_with_active_workout)
    assert ctx["current_set"] == 2  # Started at 1, now 2
```

**Richtlinien für Fixtures:**
- Fixtures für Setup verwenden, nicht für Assertions
- Fixtures sollten einen klaren, beschreibenden Namen haben
- Komplexe Fixtures in `conftest.py` auslagern

---

## 8. Mutation Testing Prinzip

Ein guter Test muss fehlschlagen, wenn die Implementation geändert wird.

```python
# Wenn dieser Code...
def get_category_for_tracker(name: str) -> str:
    name_lower = name.lower()
    for key, category in TRACKER_CATEGORIES.items():
        if key in name_lower:
            return category
    return "general"

# ...zu diesem mutiert wird...
def get_category_for_tracker(name: str) -> str:
    return "general"  # Mutation: immer "general" zurückgeben

# ...dann MUSS mindestens ein Test fehlschlagen!
```

**Selbsttest:** Frage dich bei jedem Test: "Wenn ich diese Zeile Code lösche/ändere, würde dieser Test fehlschlagen?"

---

## 9. Was NICHT getestet werden sollte

- **Externe Libraries:** Nicht testen ob SQLAlchemy funktioniert
- **Triviale Getter/Setter:** Kein Test für `return self.name`
- **Framework-Code:** Nicht testen ob FastAPI Routing funktioniert
- **Generierter Code:** Keine Tests für Alembic Migrations

**Stattdessen fokussieren auf:**
- Business Logic
- Datenvalidierung und -transformation
- Zustandsübergänge
- Fehlerbehandlung
- Integration zwischen eigenen Komponenten

---

## 10. Test-Checkliste

Vor dem Commit eines Tests diese Fragen beantworten:

- [ ] Beschreibt der Testname das erwartete Verhalten?
- [ ] Testet der Test Verhalten, nicht Implementation?
- [ ] Ist der Test unabhängig von anderen Tests?
- [ ] Würde der Test fehlschlagen wenn das Verhalten kaputt ist?
- [ ] Ist der Test ohne Kommentare verständlich?
- [ ] Gibt es keine Logik (Schleifen, Bedingungen) im Test?

---

## Projektspezifische Konventionen

### Dateistruktur

```
backend/
  tests/
    __init__.py
    conftest.py              # Gemeinsame Fixtures
    test_entry_service.py    # Tests für services/entry.py
    test_context_engine.py   # Tests für services/context.py
    test_user_service.py     # Tests für services/user.py
    integration/
      test_chat_router.py    # API Integration Tests
      test_tracker_router.py
```

### Ausführung

```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=app --cov-report=term-missing

# Nur Unit Tests
pytest tests/ --ignore=tests/integration

# Verbose Output
pytest -v
```

### Async Tests

Für async Funktionen `pytest-asyncio` verwenden:

```python
import pytest

@pytest.mark.asyncio
async def test_save_entry_creates_tracker_if_not_exists():
    # ...
```
