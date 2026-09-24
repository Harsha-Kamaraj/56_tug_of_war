# Tug of War Repair Lab

This project is a competitive tug-of-war game using **Pygame**. It introduces students to alternating keyboard input synchronization, debounce and lock state patterns, physics-based tension balancing, and autonomous AI pulling mechanics within an object-oriented codebase.
---

## What's Provided

A working Tug of War game with:

- A horizontal rope setup with goal markers, center boundary indicators, and a center position flag
- Two anchor pullers (`PLAYER` and `COMPUTER`) rendered with visual team colorings
- An alternating key input model requiring players to alternate `A` and `D` to pull left
- An autonomous computer opponent that pulls the rope rightward at recurring intervals
- Win-state boundary detection and a Game Over overlay with rematch support

It has **one deliberate bug** and **three optional features** left as tasks to implement. You are expected to **analyze**, **interact with an AI assistant**, and **complete/fix** the game to make it fully functional and more interesting.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**
---

## Getting Started

### Setup

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:

```bash
pip install pygame
```

3. Run the game:

```bash
python main.py
```

**Controls:** Left-click on the HIGHER or LOWER buttons to predict the next card.   


## Tasks to Complete

Each task must be completed using an iterative process involving LLM suggestions and your critical code review.

### Task 1: Fix the input lock deadlock bug

When rapidly alternating between A and D, the rope suddenly locks up and stops responding to any player input, giving the computer a free win. In game_engine.handle_event(), self.is_pull_locked is set to True on key down, but it only unlocks on KEYUP if event.key == self.last_key. If the player presses the second key before fully releasing the first key (standard rapid keystroke overlap), self.last_key gets updated, preventing the previous key release from ever setting self.is_pull_locked = False. Remove the broken locking flag mechanism or redesign the debounce logic so simply alternating keys (event.key != self.last_key) successfully pulls without permanently freezing input.

### Task 2: Implement dynamic computer difficulty surge

Right now, the computer pulls at a fixed interval of 180ms with minor random variance. Implement dynamic difficulty in game_engine.update(): if the center flag gets pulled closer to the player's goal line (self.rope.left_win_x), have the computer enter a "panic surge" mode by decreasing its cooldown or increasing its pulling strength to fight back aggressively

### Task 3: Implement rope tension and pull animations

Currently, the rope is drawn as a static straight horizontal line, and puller positions do not react to movement. In rope.render() and puller.render(), implement rope sag or tension effects (e.g., slight vertical vibration/waviness when tension is high) and add a leaning animation to each puller that tilts backwards according to who has pulling momentum

### Task 4: Implement a match timer and sudden death mode
If two evenly matched opponents play, a match can last indefinitely. Add an active match timer displayed at the top of the screen. If neither side has won after 45 seconds, enter "Sudden Death" mode: double the pull distance of every keystroke and computer tick so the match finishes quickly.

---

## Expected Behavior

- Rapidly alternating between A and D reliably moves the red center flag to the left without freezing or dropping inputs during fast mashing.
- The computer pulls the marker to the right at recurring intervals.
- The match ends when the flag crosses the left boundary (Player wins) or right boundary (Computer wins).
- Pressing R on the Game Over screen resets the rope marker, keys, timers, and game states.
---

## Folder Structure

```
tug_of_war/
├── game/
│   ├── game_engine.py
│   ├── player.py
│   └── rope.py
├── main.py
└── README.md
```

---

## Submission Checklist

Submission is only the following three things:

- [] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [] The Chat/LLM used page link, with the complete chat history
