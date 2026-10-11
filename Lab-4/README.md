# Real-Time Reaction Time Tester

This project is an interactive reaction time tester built using **Pygame**. It demonstrates interactive game design using object-oriented principles, real-time graphical rendering, dynamic sound synthesis, and state-machine architecture.

---

## What’s Implemented & Fixed

All tasks specified in the lab assignment have been fully implemented and verified:

- [x] **Task 1: Refined Input Timing Detection & False Start Handling**
  - Measures elapsed time starting strictly from when the screen turns green (`go_time`), eliminating the previous wait-duration time inflation bug.
  - Detects premature clicks/presses during the grey "wait" phase and marks them as **False Starts** (red screen feedback: "TOO SOON!").
  - False starts are recorded separately and excluded from corrupting the numeric average reaction time.

- [x] **Task 2: Dedicated Game Over & Results Screen**
  - Displays a complete graphical summary screen at the conclusion of all rounds instead of abruptly ending or printing only to the console.
  - Shows an itemized round-by-round breakdown (with milliseconds or False Start badge).
  - Summarizes key performance indicators: Average Time, Best/Fastest Reaction, and False Start Count.
  - Computes and displays reflex skill ratings (e.g. *Lightning Reflexes*, *Great Reflexes*, *Average*, *Needs Practice*).

- [x] **Task 3: Interactive Replay & Difficulty System**
  - Offers three difficulty levels with custom round counts and wait intervals:
    - **[1] Easy:** 3 Rounds, 1500 ms – 3500 ms delay
    - **[2] Medium:** 5 Rounds, 1000 ms – 3000 ms delay
    - **[3] Hard:** 7 Rounds, 500 ms – 1800 ms delay
  - Interactive clickable buttons with hover visual feedback.
  - Keyboard shortcuts for rapid selection:
    - `1` / `E`: Easy
    - `2` / `M`: Medium
    - `3` / `H`: Hard
    - `R` / `Space`: Replay current difficulty
    - `Q` / `Esc`: Cleanly exit the game

- [x] **Task 4: Dynamic Sound Effects**
  - Built-in procedural WAV audio synthesis via `SoundManager` (zero external asset downloads required):
    - **Go Cue:** Crisp 880 Hz chime when the screen turns green.
    - **False Start:** Low 200/140 Hz buzzer when clicking too early.
    - **Game Over:** Celebratory ascending 4-note arpeggio upon completing all rounds.

---

## Getting Started

### Prerequisites

- Python 3.10+
- Pygame (`pygame` or `pygame-ce`)

### Installation

```bash
pip install -r requirements.txt
```

### Running the Game

```bash
python main.py
```

### Generating the Lab 4 Prompts & Chat History PDF

```bash
python generate_pdf.py
```
This generates `Lab_4_VibeCoding_Prompts_And_Chat_History.pdf` for submission.

---

## Controls

| Action | Controls |
| :--- | :--- |
| **React / Click** | Left Mouse Click or `Spacebar` |
| **Select Easy** | Click `[1] Easy` button or press `1` / `E` |
| **Select Medium** | Click `[2] Medium` button or press `2` / `M` |
| **Select Hard** | Click `[3] Hard` button or press `3` / `H` |
| **Replay Current** | Press `R` or `Spacebar` on the game over screen |
| **Quit Game** | Click `[Q] Quit` button or press `Q` / `Esc` |

---

## Folder Structure

```
43_reaction-time-tester-main/
├── assets/
│   └── sounds/
│       ├── false_start.wav
│       ├── game_over.wav
│       └── go.wav
├── game/
│   ├── __init__.py
│   ├── game_engine.py
│   ├── round.py
│   └── sound_manager.py
├── generate_pdf.py
├── Lab_4_VibeCoding_Prompts_And_Chat_History.pdf
├── Lab_4_VibeCoding_Student_handout.pdf
├── main.py
├── requirements.txt
└── README.md
```

---

## Submission Checklist

Upload the following to your Lab repository under the `Lab-4` folder:

- [ ] A 10-second video of gameplay **before** changes, showing the inflated timing / unhandled early click.
- [ ] A 10-second video of gameplay **after** changes, showing the false start warning, accurate reaction timing, game over results, and audio cues.
- [ ] The generated PDF (`Lab_4_VibeCoding_Prompts_And_Chat_History.pdf`) containing the full prompt history and technical report.
