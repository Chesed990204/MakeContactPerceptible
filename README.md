# Making Mid-air Button Contact Perceptible

**Adaptive Feedback Model for Enhancing Interaction Saliency in VR**  
Inhyuk Song and Kihyun Park · WHC 2025 Student Innovation Challenge

A Unity research prototype that adjusts the spatial trigger of fingertip vibration to help users learn where a mid-air button should feel fully pressed.

## Overview

Without physical resistance, users can overshoot or stop short of a virtual button's intended press point. This project combines Leap Motion hand tracking, bHaptics TactGlove DK2 feedback, and repeated-press measurements to explore how tactile feedback should adapt to pressing behavior.

The repository includes five visual/vibrotactile conditions, a Python dashboard for trial logging, and a dinosaur-game demonstration controlled by contact events.

## Feedback and Adaptation

`CustomFeedbackProvider` provides visual-only, fixed-vibration, adaptive-vibration, visual + fixed-vibration, and visual + adaptive-vibration presets. Impact feedback uses a 5 ms pulse on the right index finger. The trigger checks whether the fingertip's z-position is within 0.005 Unity units of `impact_position`; a latch prevents repeated pulses until withdrawal completes.

`CustomCapsuleHand.RecordTrialOutcome` implements this update after 15 valid outcomes reach its accumulator:

```text
error = maximum index-finger z − GROUND_TRUTH
next impact_position = impact_position + 0.1 × mean(error)
```

`GROUND_TRUTH` is 0.1293 in the supplied demo scene. These coordinates belong to that scene's configuration. The Python optimizer is experimental and is not called by the active dashboard.

## Setup

### Requirements

- **Unity 2021.3.26f1**, recorded in `ProjectSettings/ProjectVersion.txt`.
- **Leap Motion/Ultraleap tracking** and its device runtime; **bHaptics TactGlove DK2** and the corresponding bHaptics runtime/device connection.
- **Python 3** with NumPy, pandas, Matplotlib, and Pygame.

The manifest pins Ultraleap Tracking **7.2.0**, Meta XR **72.0.0**, and OpenXR **1.7.0**. Keep `Packages/MixedReality/`: the manifest references its bundled package archives. The bHaptics SDK is included under `Assets/Bhaptics/`.

### Start the Demo

1. Clone the repository and open its root in Unity Hub using the recorded editor version. Allow package import to finish.
2. Connect the tracking device and glove. Open **`Assets/Scenes/[Demo] 250704 dino.unity`**. This scene includes the desktop tracking provider and both TCP clients. Build Settings currently contains no scenes, so open it explicitly in the Editor.
3. Install the Python dependencies in your chosen environment:

   ```bash
   python -m pip install numpy pandas matplotlib pygame
   ```

4. From the repository root, start the dashboard:

   ```bash
   python Assets/Scripts/Python/main.py
   ```

   Enter a participant/session label at the terminal prompt and wait for the listener on **127.0.0.1:25001**.
5. In another terminal, start the game from its own directory so relative asset paths resolve:

   ```bash
   cd Assets/Scripts/chrome-dinosaur-master
   python "[DEMO]game.py"
   ```

   Its listener uses **127.0.0.1:25002**. Start both servers before entering Unity Play mode; the clients attempt their initial connections in `Start()`.
6. Enter Play mode and press the virtual button with the tracked right index finger. Withdraw the finger to complete a trial. The scene starts with **visual + adaptive vibrotactile** feedback.

These instructions follow the committed source; hardware execution has not been verified for this README.

## Controls and Output

| Action | Control |
|---|---|
| Select a feedback condition | `Button` → `CustomFeedbackProvider` → `_feedbackPreset` in the Inspector |
| Start/restart the dinosaur game | Trigger a Unity contact event |
| Jump during gameplay | Unity contact event or **Up Arrow** |
| Duck during gameplay | **Down Arrow** |
| Remove the latest displayed trial | **Backspace/Delete** while the Matplotlib window has focus |

The dashboard saves CSV files under `experiment_data/<label>/<condition>/`, relative to its working directory, with separate `trials/` and `episode_stats/` folders. Restart Play mode between conditions to reset Unity's accumulated adaptation state.

### Current Limitations

- The dashboard's episode-completion reply is not recognized as an accepted outcome by `TCPClient`. This causes Unity and Python episode counts to diverge; align the reply handling before reproducing the intended 15-trial schedule.
- Dashboard undo changes in-memory plots/statistics; it does not remove saved CSVs or roll back Unity adaptation.
- Dashboard `error` means maximum travel minus the feedback position; Unity's adaptation error uses `GROUND_TRUTH`.
- The game menu's keyboard handler uses an incorrect event constant. Use a contact event to start/restart.

## Code Map

| Path under `Assets/Scripts/` | Responsibility |
|---|---|
| `CustomCapsuleHand.cs` | Finger tracking, movement states, trial maxima, adaptation |
| `CustomFeedbackProvider.cs` | Feedback presets, vibration trigger, glove output |
| `TCPClient.cs` | Trial transfer and outcome acknowledgement |
| `RealtimeTCPClient.cs` | Contact-event stream for the game |
| `Python/main.py` | Trial filtering, CSV export, episode plots |
| `chrome-dinosaur-master/[DEMO]game.py` | Contact-controlled game |

## Research and Credits

The WHC 2025 exploratory study involved **six adults**, five feedback conditions, and **four episodes of 15 trials per condition**. Presentation materials report promising stabilization of maximum-travel measures under adaptive feedback. These small-study observations motivate further evaluation rather than establish a general performance advantage.

**Inhyuk Song** led research design, implementation, evaluation, and analysis. **Authors:** Inhyuk Song and Kihyun Park, ITEM Lab, Kyung Hee University.

[WHC 2025 Student Innovation Challenge](https://2025.worldhaptics.org/Student-Innovation-Challenge) · [Dinosaur-game attribution](Assets/Scripts/chrome-dinosaur-master/README.MD) · [MIT license](LICENSE)
