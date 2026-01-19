# AI Life Tracker - Vision

## Ein Satz

**Ein Chat. Mehr nicht.**

---

## Die Idee

Die gesamte App ist ein einziger Chat. Kein Menü, keine Navigation, keine Settings-Seite, keine Dashboards. Der User spricht oder tippt - die AI versteht und handelt.

---

## Warum?

Jede Tracking-App scheitert am selben Problem: **Friction.**

- Zu viele Buttons
- Zu viele Screens
- Zu viel Konfiguration
- Zu viel Lernaufwand

Unser Ansatz: **Zero Interface.**

Der User muss nichts lernen. Er redet einfach mit der App wie mit einem Menschen.

---

## Das Interface

```
┌─────────────────────────────────┐
│            [Logo]               │
│                                 │
│  ┌───────────────────────────┐  │
│  │                           │  │
│  │      Chat-Verlauf         │  │
│  │                           │  │
│  │   mit eingebetteten       │  │
│  │   UI-Components           │  │
│  │                           │  │
│  └───────────────────────────┘  │
│                                 │
│  ┌─────────────────────┬─────┐  │
│  │ Nachricht...        │ 🎤  │  │
│  └─────────────────────┴─────┘  │
│         (hold to talk)          │
└─────────────────────────────────┘
```

Drei Elemente:
1. **Logo** (oben)
2. **Chat** (Mitte)
3. **Input + Voice-Button** (unten, Push-to-Talk)

Das war's.

---

## Voice-First, Text-Fallback

**Primär:** Sprechen (Push-to-Talk)

**Fallback:** Tippen - für Situationen in denen Voice nicht geht:
- In der Bahn
- Laute Umgebung
- Keine Lust zu reden

Beides führt zum selben Ergebnis.

---

## Generative UI mit Component Templates

Die AI generiert **keine** UI. Sie **wählt aus**.

### Wie es funktioniert:

```
User: "Wie lief meine Woche?"

AI entscheidet: WeeklyChart passt hier
AI liefert: { component: "WeeklyChart", data: {...} }

Frontend: Rendert immer dasselbe WeeklyChart Template
```

### Warum Templates statt freier Generierung:

| Frei generiert | Component Templates |
|----------------|---------------------|
| Jedes Mal anders | Immer konsistent |
| Unvorhersehbar | Vorhersehbar |
| Schwer zu stylen | Einmal gestalten |
| Wirkt chaotisch | Wirkt durchdacht |

### Component-Bibliothek:

Die AI kann aus diesen Templates wählen:

**Bestätigungen & Feedback:**
- `Confirmation` - Aktion bestätigen/ablehnen
- `SuccessMessage` - Kurze Erfolgsmeldung

**Daten anzeigen:**
- `StatCard` - Einzelner Wert mit Label
- `List` - Einfache Auflistung
- `EntryCard` - Einzelner Tracking-Eintrag
- `WeeklyView` - Wochenübersicht
- `ProgressChart` - Fortschritt über Zeit

**System:**
- `AccountCard` - Account-Informationen
- `DownloadLink` - Export/Download

Neue Components werden nach Bedarf ergänzt - aber immer als **festes Template**, nie dynamisch generiert.

---

## Alles ist Chat-gesteuert

### Tracking (Kernfunktion)

```
User: "Bankdrücken 80kg 12 Wiederholungen"
AI: "Gespeichert." [Confirmation]

User: "Starte Brust-Workout"
AI: "Workout gestartet. Viel Erfolg!"

User: "Ich trainiere jetzt immer Montag und Donnerstag"
AI: "Routine gespeichert. Soll ich dich erinnern?"
```

### Auswertungen

```
User: "Zeig mir meine Woche"
AI: [WeeklyView Component]

User: "Wie hat sich mein Bankdrücken entwickelt?"
AI: [ProgressChart Component]

User: "Was hab ich gestern gemacht?"
AI: [List Component mit gestrigen Entries]
```

### Einstellungen & Account

```
User: "Mach Dark Mode an"
AI: "Erledigt." → [Theme wechselt sofort]

User: "Zeig meine Account-Infos"
AI: [AccountCard Component]

User: "Exportier meine Daten"
AI: [DownloadLink Component]

User: "Lösch meinen Account"
AI: [Confirmation Component mit Warnung]
```

### Hilfe

```
User: "Was kannst du alles?"
AI: "Ich kann für dich tracken: Workouts, Habits, Schlaf, 
     Wasser, Gewicht - eigentlich alles. Sag mir einfach 
     was du festhalten willst."

User: "Wie funktionieren Routinen?"
AI: "Sag mir einfach wann du was machst. Zum Beispiel: 
     'Ich meditiere jeden Morgen' oder 'Dienstags ist Leg Day'"
```

---

## Design-Prinzipien

### Minimalistisch
- Viel Whitespace
- Wenige Elemente
- Ein Fokus pro Ansicht
- Kein visuelles Rauschen

### Stylish
- Cleane Typografie
- Subtile Animationen
- Durchdachte Farbakzente
- Dark Mode als Standard

### Konsistent
- Feste Component Templates
- Einheitliche Abstände
- Gleiche Interaktionsmuster
- Vorhersehbares Verhalten

---

## Die einzige "klassische" UI

**Login-Screen** (via Clerk)

Danach: Nur noch Chat.

---

## Später: Programmierbare Shortcuts

Für Power-User die bestimmte Anfragen sehr häufig nutzen:

```
[Woche] [Workout] [Stats]
```

Anpassbare Buttons die vordefinierte Chat-Befehle auslösen.

Aber: Kein MVP-Feature. Erstmal nur Chat.

---

## Zusammenfassung

| Traditionelle App | AI Life Tracker |
|-------------------|-----------------|
| Menüs, Tabs, Screens | Ein Chat |
| Forms und Buttons | Natürliche Sprache |
| Settings-Seiten | "Mach Dark Mode an" |
| Dashboard mit Widgets | AI zeigt was relevant ist |
| Lernkurve | Einfach reden |

**Das Ziel:** Eine App die sich anfühlt wie ein Gespräch mit einem persönlichen Assistenten - nicht wie Software.
