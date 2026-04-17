# Soulbot Project: Comprehensive Report & Integration Guide

Welcome to the Soulbot documentation. This report provides a detailed breakdown of the project architecture, dependencies, and operational flows required to run and maintain the Soul Imaging AI ecosystem.

---

## 🏗️ Project Architecture Overview

The Soulbot ecosystem is divided into two primary applications that work in tandem:

1.  **Frontend (Main AI Interface)**: A high-fidelity, vanilla web application that serves as the patient-facing side of the AI assistant.
2.  **Admin Dashboard**: A modern React-based management interface used by clinic staff to configure the AI, view call histories, and manage team access.

### 📂 Directory Structure

```text
Soulbot/
├── Admin/              # React + Vite Admin Dashboard
├── Frontend/           # Vanilla HTML/CSS/JS AI Interface
│   ├── Orb/            # The core AI visual component (animations/logic)
│   ├── index.html      # Main Chatbot entry point
│   ├── script.js       # Core frontend logic & chat simulation
│   └── style.css       # Visual styling and glassmorphism design
└── docs/               # Project documentation and reports
```

---

## 💻 Modules & Dependencies

### 1. Frontend (Main AI)
*   **Technologies**: HTML5, CSS3, Vanilla JavaScript.
*   **External Libraries (CDN)**:
    *   **Lucide Icons**: Used for modern, clinical-grade iconography.
    *   **Google Fonts**: Uses **Outfit** (Headlines) and **Inter** (Body) for a premium medical aesthetic.
*   **Core Systems**:
    *   **Orb Component**: A custom-built SVG/CSS animation system that reflects the bot's state (Idle, Thinking, Speaking, Listening).

### 2. Admin Dashboard (React)
Built with the modern Vite + React + TypeScript stack.
*   **Framework**: [React 18](https://reactjs.org/)
*   **Styling**: [Tailwind CSS](https://tailwindcss.com/) with [Shadcn UI](https://ui.shadcn.com/) components.
*   **State Management**: [TanStack Query (React Query)](https://tanstack.com/query/latest) for data fetching.
*   **Routing**: [React Router DOM v6](https://reactrouter.com/) for page navigation.
*   **Charts**: [Recharts](https://recharts.org/) for analytics visualization.
*   **Components**: Based on **Radix UI** primitives (Accordion, Dialog, Tabs, etc.).
*   **Validation**: **Zod** for schema validation and **React Hook Form** for managing forms.

---

## 🚀 Installation & Setup Guide

To run the full project from scratch, follow these steps:

### Phase 1: Install Node.js
Ensure you have **Node.js (v18 or higher)** installed on your system.

### Phase 2: Set Up Admin Dashboard
1.  Open your terminal in the `Admin/` directory.
2.  Install all required modules:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    *The Admin panel will launch at [http://localhost:8080](http://localhost:8080).*

### Phase 3: Set Up Main AI Interface (Frontend)
The frontend is a static site and needs a simple HTTP server to run correctly (especially for module/asset loading).
1.  Open your terminal in the `Frontend/` directory.
2.  Use a simple server like `serve` or `live-server`:
    ```bash
    npx serve -l 8000 .
    ```
    *The Chatbot will launch at [http://localhost:8000](http://localhost:8000).*

---

## 🔄 Operational Flow

### 1. User/Patient Flow
1.  **Landing**: The user enters the site and is greeted by the Soulbot Orb in "Idle" state.
2.  **Interaction**: The user types a message or uses the Mic button (Listening state).
3.  **Simulation**: The `script.js` handles the logic, transitioning the Orb to "Thinking" then "Speaking" as the bot responds.
4.  **Admin Access**: Clinic staff can click the **Admin Panel** button in the header (linked to port 8080) to switch to the management side.

### 2. Administrator Flow
1.  **Dashboard**: View real-time analytics on AI calls and system bookings.
2.  **Agent Config**: Update the AI's behavior, tone, and clinical knowledge.
3.  **Team Management**: Manage authorized email addresses for staff access.
4.  **Call History**: Review transcripts and AI performance metrics.

---

## 📄 File-by-File Breakdown

| File Path | Purpose |
| :--- | :--- |
| `Frontend/index.html` | The main layout. Contains the glassmorphism header, the Orb container, and the chat input. |
| `Frontend/script.js` | Manages the conversation logic, bot state triggers, and UI transitions. |
| `Frontend/style.css` | Defines the "Soul Imaging" design system, clinical colors, and responsive layouts. |
| `Frontend/Orb/` | Contains the HTML/CSS/JS specifically for the AI's visual "Orb" identity. |
| `Admin/src/App.tsx` | The root React component defining the layout and routing providers. |
| `Admin/src/pages/` | Contains individual views like `DashboardOverview.tsx`, `TeamManagement.tsx`, and `Analytics.tsx`. |
| `Admin/tailwind.config.ts` | The configuration file for the dashboard's design system and theme. |

---

> [!TIP]
> **Port Linking & Navigation**: The Frontend interface links to the Admin dashboard at port **8080**. Conversely, the Admin sidebar is configured to redirect back to the Chatbot at port **8000**. These ports must remain constant for optimized bidirectional navigation.
