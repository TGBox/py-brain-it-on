# 🧠 Py Brain it on!

Eine Python-Adaption des mobilen Physik-Puzzlespiels **Brain it on!** — entwickelt mit [pygame-ce](https://github.com/pygame-community/pygame-ce) und [pymunk](http://www.pymunk.org/).

Zeichne Formen mit der Maus, nutze die Physik-Simulation und bringe den Ball in den Eimer!

---

## 🎮 Spielprinzip

1. **Zeichnen**: Zeichne mit der Maus beliebige Linien und Formen auf der Spielfläche.
2. **Verbinden**: Wenn eine gezeichnete Linie eine andere oder ein statisches Objekt berührt, entsteht ein Verbindungspunkt (rote Niete). Verbundene Formen verhalten sich wie ein gemeinsames starres Objekt.
3. **Starten**: Klicke auf *Starten*, um die Physik-Simulation zu starten — die gezeichneten Formen beginnen sich je nach Verbindungen und Schwerkraft zu bewegen.
4. **Ziel**: Bringe den Ball in den Eimer! Je weniger Striche du dafür benötigst, desto mehr Sterne bekommst du.

---

## ✨ Features

- **25 handgefertigte Level** vom Tutorial bis zum großen Finale
- **Pymunk-Physik-Engine** mit realistischer Schwerkraft, Elastizität und Reibung
- **Sternebewertung** (1–3 Sterne) basierend auf der Anzahl der gezeichneten Striche
- **Musterlösungen** für jedes Level, die nach mehreren Fehlversuchen freigeschaltet werden
- **Rückgängig-Funktion** für einzelne Striche
- **Verbindungspunkte** (Nieten) zum Lösen per Klick
- **Fortschrittsspeicherung** — gelöste Level und Sterne bleiben erhalten
- **Fortschritt zurücksetzen** in der Level-Auswahl
- **Vollbild FullHD (1920×1080)** mit moderner UI

### Steuerung

| Aktion | Eingabe |
|---|---|
| Form zeichnen | Linksklick + Ziehen |
| Strich rückgängig | *Rückgängig*-Button |
| Verbindung lösen | Klick auf rote Niete |
| Simulation starten | *Starten*-Button |
| Simulation abbrechen | *Formen anpassen*-Button |
| Level-Tipp anzeigen | *Tipp*-Button |
| Musterlösung ansehen | *Musterlösung*-Button (ab 2 Fehlversuchen) |

---

## 📋 Voraussetzungen

- **Python ≥ 3.14**
- **[uv](https://docs.astral.sh/uv/)** (empfohlener Package-Manager)

---

## 🚀 Installation & Starten

### Mit `uv` (empfohlen)

```bash
# Repository klonen
git clone https://github.com/TGBox/py-brain-it-on.git
cd py-brain-it-on

# Abhängigkeiten installieren und Spiel starten
uv run py-brain-it-on
```

### Alternativ mit `pip`

```bash
git clone https://github.com/TGBox/py-brain-it-on.git
cd py-brain-it-on
pip install -e .
py-brain-it-on
```

### Direkt als Modul

```bash
cd py-brain-it-on
uv run python -m py_brain_it_on
```

---

## 🗂️ Projektstruktur

```
py-brain-it-on/
├── src/py_brain_it_on/
│   ├── __init__.py          # Einstiegspunkt (main())
│   ├── game.py              # Haupt-Spielschleife & Szenen-Stack
│   ├── settings.py          # Globale Konstanten (Farben, Physik, Fenster)
│   ├── save_manager.py      # Fortschritts-Speicherung (JSON)
│   ├── levels/
│   │   ├── base_level.py    # Abstrakte Level-Basisklasse
│   │   ├── level_01.py      # Tutorial: Die Rutsche
│   │   ├── level_02.py      # Bogenbrücke
│   │   ├── ...
│   │   └── level_25.py      # Großes Finale
│   ├── physics/
│   │   ├── world.py         # Pymunk-Physikwelt (Bälle, Segmente, Eimer)
│   │   └── drawing.py       # Maus-Zeichnungsmanager (Douglas-Peucker)
│   ├── scenes/
│   │   ├── base_scene.py    # Abstrakte Szenen-Basisklasse
│   │   ├── menu_scene.py    # Hauptmenü
│   │   ├── level_select.py  # Level-Auswahl mit Seitennavigation
│   │   └── play_scene.py    # Haupt-Spielszene (Zustandsmaschine)
│   └── ui/
│       ├── components.py    # RoundedButton, Hilfsfunktionen, Wortumbruch
│       └── animations.py    # Tween-Animationen (Bounce, Back)
└── tests/
    └── test_game.py         # Regressionstests (Level, Szenen, Physik)
```

---

## 🧩 Level-Übersicht

| # | Titel | Schwierigkeit |
|---|---|---|
| 01 | Tutorial: Die Rutsche | ⭐ |
| 02 | Bogenbrücke | ⭐ |
| 03 | Der Trichter | ⭐⭐ |
| 04 | Zwei Bälle | ⭐⭐ |
| 05 | Zickzack-Kaskade | ⭐⭐ |
| 06 | Die Schlucht | ⭐⭐ |
| 07 | Flipper-Stoß | ⭐⭐ |
| 08 | Gegen den Wind | ⭐⭐⭐ |
| 09 | Kettenreaktion | ⭐⭐⭐ |
| 10 | Dreierlei | ⭐⭐⭐ |
| 11 | Hoch hinaus | ⭐⭐⭐ |
| 12 | Das Labyrinth | ⭐⭐⭐ |
| 13 | Präzisionsschuss | ⭐⭐⭐ |
| 14 | Wippen-Transfer | ⭐⭐⭐ |
| 15 | Zwillings-Eimer | ⭐⭐⭐ |
| 16 | Hängebrücke | ⭐⭐⭐ |
| 17 | Der Ausbruch | ⭐⭐⭐⭐ |
| 18 | Der Tunnel | ⭐⭐⭐⭐ |
| 19 | Turmsturz | ⭐⭐⭐⭐ |
| 20 | Kollision | ⭐⭐⭐⭐ |
| 21 | Schwerelos | ⭐⭐⭐⭐ |
| 22 | Domino-Effekt | ⭐⭐⭐⭐ |
| 23 | Ball-Duell | ⭐⭐⭐⭐⭐ |
| 24 | Katapult-Meister | ⭐⭐⭐⭐⭐ |
| 25 | Großes Finale | ⭐⭐⭐⭐⭐ |

---

## 🔧 Entwicklung

### Tests ausführen

```bash
uv run python tests/test_game.py
```

### Eigenes Level erstellen

Erstelle eine neue Datei `src/py_brain_it_on/levels/level_XX.py` und erbe von `BaseLevel`:

```python
from .base_level import BaseLevel
from ..physics.world import PhysicsWorld

class LevelXX(BaseLevel):
    LEVEL_NUMBER = XX
    TITLE = "Mein Level"
    GOAL_DESCRIPTION = "Bringe den Ball in den Eimer!"
    HINT = "Tipp: Zeichne eine Rampe von links nach rechts."
    STAR_THRESHOLDS = (1, 3)  # (3-Sterne-Schwelle, 2-Sterne-Schwelle)
    SOLUTION_DESCRIPTION = "Kurze Beschreibung der Musterlösung."
    SOLUTION_STROKES = [
        [(x1, y1), (x2, y2), ...]  # Koordinatenpunkte der Musterlösung
    ]

    def setup(self, world: PhysicsWorld) -> None:
        world.add_ball((300, 200))
        world.add_bucket((1600, 900), width=150, height=120)
        # Statische Plattformen, Hindernisse usw. hier hinzufügen
```

Erhöhe anschließend `TOTAL_LEVELS` in [`settings.py`](src/py_brain_it_on/settings.py).

---

## 🛠️ Technologien

| Technologie | Zweck |
|---|---|
| [pygame-ce](https://github.com/pygame-community/pygame-ce) ≥ 2.5.8 | Rendering, Eingabe, Fenster |
| [pymunk](http://www.pymunk.org/) ≥ 7.3.0 | 2D-Physik-Engine (Chipmunk-Bindings) |
| [uv](https://docs.astral.sh/uv/) | Package-Management & Ausführung |
| Python ≥ 3.14 | Programmiersprache |

---

## 👤 Autor

**Daniel Rösch** — [droesch91@gmail.com](mailto:droesch91@gmail.com)

---

## 📄 Lizenz

Dieses Projekt ist eine eigenständige Python-Adaption, die von der Spielidee des originalen *Brain it on!* (Orbital Nine Games) inspiriert wurde. Alle Inhalte (Code, Levels, Assets) wurden neu erstellt.
