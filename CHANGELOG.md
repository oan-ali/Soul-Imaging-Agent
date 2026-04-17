## Version 1.1.0 – 2026-04-16

### 1. Summary (Saif)
* Initial stability pass focused on UI navigation and frontend context warnings for SSL.

### 2. Key Changes
* **Navigation:** Added Admin dashboard access to the main UI.
* **Security:** Added HTTPS microphone context detection warnings.
* **Performance:** Optimized startup sequence with parallel token fetching.

---

## Version 1.2.0 – 2026-04-17

### 1. Summary (Lead: Abdullah)

* This update restores industry-leading voice quality by reverting to Gladia and Cartesia while introducing critical stability fixes for conversational flow.
* A major branding overhaul was completed, ensuring the real Soul Imaging identity is consistent across all interfaces with a premium dark-mode aesthetic.

### 2. Changes Made

#### Voice & Conversational Intelligence
* **Engine Restoration:** Reverted STT and TTS engines to **Gladia** and **Cartesia** for superior latency and expressive reach.
* **Language Stability:** Hard-locked Gladia STT to English only (`languages=["en"]`) and disabled `code_switching` to eliminate hallucinations and random switches to foreign languages.
* **Conversational Pace Tuning:** 
    * **Intentional Latency:** Increased endpointing delay by **0.5s** (now set to 0.5s - 1.0s range). This target delay is based on industry standards for professional agents to prevent interrupting users mid-sentence.
    * **VAD Optimization:** Updated Silero VAD `min_silence_duration` to 400ms to ignore natural speech gaps, providing a more human-like listening experience.

#### Branding & Architecture
* **Directory Cleanup:** Renamed `Production_Grade_VoiceAgent_FrontEnd` to `frontend` for better project structure and updated all path references in `agent/api.py` and `Dockerfile`.
* **Professional Branding:** 
    * Replaced all placeholder logos with the official Soul Imaging teal logo.
    * Implemented `?v=3` cache-busting to bypass browser caching of old assets.
* **Login Redesign:** Overhauled the Admin Login page from a generic light theme to a premium **Deep Midnight** blue theme with glassmorphism and enhanced focus states.
* **Session Controls:** Added a dedicated Logout dropdown to the administrator avatar in the header to allow secure session termination.
* **Environment Cleanup:** Deleted the redundant `.venv_old` directory to reduce project size.

### 3. End Result
* The agent now feels sophisticated and polite, waiting for the caller to finish their thoughts before responding.
* The administrative interface is now fully synchronized with the clinic's brand identity.
