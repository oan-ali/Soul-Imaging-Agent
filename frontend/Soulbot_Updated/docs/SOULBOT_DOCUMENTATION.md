# Soulbot AI: Project Documentation

Soulbot is a premium, healthcare-inspired AI assistant interface designed for "Soul Imaging." It features a state-of-the-art interactive orb identity and a clean, clinical aesthetic.

---

## 🏗️ Project Architecture

The project is a vanilla web application (HTML/CSS/JS) built with a focus on high-fidelity animations and modular UI components.

### File Structure & Roles

#### 1. Core Application Files
*   **`index.html`**: The entry point. It defines the layout structure, including the glassmorphism header, the AI interaction space, and the persistent input bar.
*   **`style.css`**: The design system. Contains the palette (Medical Blue, Deep Slate, Off-white), typography, and the responsive layout logic for a fixed 100vh experience.
*   **`script.js`**: Central controller. Manages chat flow, bot state transitions, and simulates AI interactions (using `setTimeout` for thinking/speaking delays).

#### 2. The Orb Component (`/Orb/`)
The "Orb" is a self-contained visual identity for the AI.
*   **`soulbot_orb_component.html`**: Defines the DOM structure for the orb (eyes, eyelids, mouth, ambient glow rings).
*   **`soulbot_orb_component.css`**: Powers the "life-like" animations. Includes complex CSS keyframes for breathing, blinking, and state-specific pulses.
*   **`soulbot_orb_component.js`**: Provides the API to switch states programmatically (e.g., `setSoulbotState('speaking')`).

---

## 🎨 Design System

| Element | Description |
| :--- | :--- |
| **Color Palette** | Primary Blue (`#2F7DD7`), Secondary Blue (`#4A90E2`), Clinical BG (`#F9FBFF`). |
| **Typography** | Headlines: **Outfit** (Modern/Stable) \| Body: **Inter** (Clean/Functional). |
| **Effects** | Heavy use of `backdrop-filter: blur()`, glassmorphism, and radial gradients for depth. |

---

## 🤖 Interaction States

The application moves through several logical states, each reflected by the Orb's behavior:

1.  **Idle**: Minimal activity, natural blinking, calm breathing.
2.  **Listening**: Triggered by voice input. Displays an outer expanding ring to show sensitivity.
3.  **Thinking**: Triggered after user input. The orb pulses with a deep blue glow.
4.  **Writing**: Used during response generation. Displays a cloud-like thought indicator.
5.  **Speaking**: Rhythmic mouth and ring animations synced to the simulated playback duration.

---

## 🚀 How to Run

1.  Open the project directory.
2.  Serve it using any local HTTP server (e.g., `python -m http.server` or `live-server`).
3.  Navigate to `http://localhost:8000`.

---

> [!NOTE]
> This project is designed for browsers that support modern CSS features like `backdrop-filter`. For the best experience, use a recent version of Chrome, Edge, or Safari.
