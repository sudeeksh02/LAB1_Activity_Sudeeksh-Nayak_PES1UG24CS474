# Multi-Modal Cognitive Reflex and Reaction Test Suite

**Course**: Software Engineering Lab (UE24CS251A) — PES University (Dept. of CSE)  
**Student Name**: Sudeeksh Nayak  
**SRN**: `PES1UG24CS474`  
**Topic**: Object-Oriented Pygame Reflex Engine, Psychophysics Paradigms & Signal Detection Analytics  

---

## Deliverables Summary

| Deliverable File | Type | Description |
|---|---|---|
| [`main.py`](main.py) | Python Script | Interactive entrypoint with graphical state-machine rendering at 60 FPS. |
| [`game/game_engine.py`](game/game_engine.py) | Engine Module | State-machine controller handling menu, waiting delays, stimulus generation, feedback, and game over screens. |
| [`game/target.py`](game/target.py) | Physics/Graphics | Dynamic spatial target rendering with animated countdown rings and Euclidean mouse hit detection. |
| [`game/round.py`](game/round.py) | Data Model | Trial data structure recording timestamps, latency, false start flags, and spatial accuracy coordinates. |
| [`game/analytics.py`](game/analytics.py) | Math/Stats | Telemetry analytics computing mean latency, median, standard deviation, percentile ranking, and consistency score. |
| [`game/sound_manager.py`](game/sound_manager.py) | Audio Synthesizer | Pure Python procedural WAV synthesizer generating real-time sine wave cues without external dependencies. |
| [`generate_pdf.py`](generate_pdf.py) | ReportLab Script | Automated technical report generator producing publication-ready PDF documentation. |
| [`Lab_5_Cognitive_Reflex_Testing_PES1UG24CS474.pdf`](Lab_5_Cognitive_Reflex_Testing_PES1UG24CS474.pdf) | PDF (`.pdf`) | Complete technical report with architecture breakdown, psychophysics paradigm analysis, sample telemetry, and prompt logs. |
| [`assets/sounds/`](assets/sounds/) | Audio Assets | Procedurally synthesized WAV audio cues (`go_cue.wav`, `target_hit.wav`, `error_buzzer.wav`, `victory_fanfare.wav`). |
| [`requirements.txt`](requirements.txt) | Dependencies | Python package dependencies (`pygame`, `reportlab`, `matplotlib`). |

---

## 1. Cognitive Testing Paradigms & Implemented Features

This test suite evaluates human-computer interaction (HCI) reflexes across three distinct psychophysics paradigms:

### [1] Visual Reflex Mode (Simple Reaction Time - SRT)
- **Mechanism**: The screen transitions from Waiting (slate gray) to Stimulus (emerald green) after an unpredictable random delay (600 ms – 3500 ms).
- **False Start Detection**: Any premature mouse click or keyboard tap during the waiting phase is intercepted, triggering an error buzzer and logging a False Start penalty without corrupting the numeric average.
- **Timing Precision**: High-resolution millisecond timer (`pygame.time.get_ticks()`) measures latency starting strictly from the stimulus transition timestamp.

### [2] Spatial Aim & Precision Mode (Choice RT & Fitts's Law)
- **Mechanism**: Dynamic bullseye targets spawn at unpredictable canvas coordinates with shrinking animated countdown rings.
- **Bi-Dimensional Metrics**: Simultaneously records decision time (latency to click) and spatial motor accuracy (Euclidean pixel distance from the target center):
  $$d = \sqrt{(x_{\text{click}} - x_{\text{target}})^2 + (y_{\text{click}} - y_{\text{target}})^2}$$
- **Timeout Handling**: Targets expire if not clicked within their lifespan, recording a trial timeout penalty.

### [3] Incongruent Go/No-Go Mode (Cognitive Inhibitory Control)
- **Mechanism**: Visual stimulus randomly alternates between **Green (GO cue, 70% probability)** and **Red/Amber (NO-GO distractor, 30% probability)**.
- **Inhibition Testing**: Tests the prefrontal cortex's ability to suppress automatic motor responses. Clicking on Green is scored as a valid reaction, whereas clicking on Red triggers a Commission Error penalty. Successfully holding back on Red for 1.2 seconds registers as a Successful Inhibition.

---

## 2. Statistical Analytics Engine

At the conclusion of each testing session, `ReflexAnalytics` evaluates empirical trial data:
- **Mean & Median Latency**: Accurate central tendency metrics excluding false alarms.
- **Standard Deviation ($\sigma$)**: Measures reaction variability and neuro-motor stability across trials:
  $$\sigma = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (x_i - \mu)^2}$$
- **Consistency Score**: Normalized metric ($0\% - 100\%$) inversely proportional to the coefficient of variation (CV):
  $$\text{Consistency} = \max\left(0, \min\left(100, \left(1 - \frac{\sigma}{\mu}\right) \times 100\right)\right)$$
- **Performance Rating**: Benchmarks the player's reflexes against standard population norms (Lightning Esports Top 1%, Superior Athletic Top 10%, Normal Human Baseline).

---

## 3. Getting Started & Controls

### Prerequisites
- Python 3.10+
- Pygame (`pip install pygame` or `pip install pygame-ce`)
- ReportLab (`pip install reportlab`)

```bash
pip install -r requirements.txt
```

### Running the Test Suite

```bash
python main.py
```

### Generating the Lab 5 Technical Report PDF

```bash
python generate_pdf.py
```

### Controls

| Action | Keyboard / Mouse Control |
| :--- | :--- |
| **Select Mode** | Click mode card or press `1` (Visual), `2` (Spatial Aim), `3` (Go/No-Go) |
| **Set Difficulty** | Click difficulty button or press `E` (Easy), `M` (Medium), `H` (Hard) |
| **Execute Reaction** | Left Mouse Click or `Spacebar` |
| **Proceed to Next Trial** | Left Mouse Click or `Spacebar` on feedback screen |
| **Replay Session** | Press `R` on summary screen |
| **Return to Menu** | Press `M` on summary screen |
| **Quit Game** | Press `Q` or `Esc` |

---

## 4. Software Architecture

```
lab5/
├── assets/
│   └── sounds/
│       ├── error_buzzer.wav
│       ├── go_cue.wav
│       ├── target_hit.wav
│       └── victory_fanfare.wav
├── game/
│   ├── __init__.py
│   ├── analytics.py
│   ├── game_engine.py
│   ├── round.py
│   ├── sound_manager.py
│   └── target.py
├── generate_pdf.py
├── Lab_5_Cognitive_Reflex_Testing_PES1UG24CS474.pdf
├── main.py
├── requirements.txt
└── README.md
```
