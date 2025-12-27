<p align="center"><img src="logo.png" width="120" style="vertical-align: middle; margin-right: 15px;" alt="Logo" /><span style="font-size: 50px; font-weight: 800; vertical-align: middle;">OutThink</span></p>

<p align="center" style="font-size: 18px; color: #666; margin-top: 0;">
  <b>The Personal Knowledge Engine.</b><br>
  <i>Operationalize raw information into a high-fidelity Second Brain.</i>
</p>

---

**OutThink** is not a note-taking app; it is a **knowledge pipeline**. It solves the problem of "information hoarding" by enforcing structure upon your inputs. Whether you are processing a technical textbook or a strategic guide, OutThink compels you to distill chaos into searchable, high-impact assets on Discord.

Engineered with a distraction-free **Cream & Taupe** aesthetic to minimize cognitive load, featuring a local-first architecture and neural audio synthesis for passive consumption.

---

## 📸 Visual Architecture

### The Interface
A minimalist abstraction layer for focused input.
![Application Interface](assets/app_ui.png)

### The Payload (Discord)
Structured data injection. Automated reading time calculation, semantic color-coding, and modular layout.
![Discord Embed Preview](assets/discord_preview.gif)

---

## ⚡ Core Capabilities

### 🧠 Structured Ingestion Modes
* **Deep Dive Protocol:** Designed for granular analysis. Supports rich text formatting (`Markdown`) via an integrated toolbar. The engine automatically fragments long-form content into Discord-compliant chunks without losing context.
* **⚡ Quick Spark (Headway Model):** A rapid-fire synthesis mode. Forces the user to compress complex topics into **3 Axioms** (Concept, Mechanism, Outcome). Renders a specialized, high-contrast visualization on Discord.

### 🎨 Cognitive UI Design
* **Zero-Distraction Environment:** The UI purposefully lacks clutter. Every pixel serves the input process.
* **Semantic Formatting:** The system creates visual hierarchy automatically using Discord Embeds, reducing the friction between "reading" and "understanding".
* **Dynamic Tagging:** Categories (*Business, Psychology, Tech*) are visually distinct via a hardcoded muted-luxury color palette.

### 🎧 Neural Audio Pipeline
* **Local-to-Cloud Synthesis:** The engine utilizes Google's Neural TTS to generate podcast-grade audio summaries (.mp3) in real-time.
* **Smart Language Detection:** Analyzes the input stream to automatically switch synthesis models between English and Polish.

### ⚙️ System Configuration
* **Integrated Channel Manager:** Configure output endpoints (Webhooks) directly within the GUI. No config files or environment variables required.
* **Portable Architecture:** Compiled as a standalone binary. No dependencies, no installation wizard.

---

## 📥 Deployment

Navigate to **[Releases](../../releases)** to retrieve the latest build (`v1.5+`).

### 🪟 Windows
1.  Download `OutThink.exe`.
2.  Execute.
    * *Note: The binary is unsigned. If SmartScreen triggers, acknowledge via "More info" -> "Run anyway".*

### 🐧 Linux (Universal)
Distributed as an **AppImage** for maximum compatibility (Ubuntu, Fedora, Arch, Bazzite, SteamOS).

**Method A: AppImage (Recommended)**
1.  Download `OutThink.AppImage`.
2.  `Right-click` → `Properties` → `Permissions` → **Allow executing file as program**.
3.  Execute.
    * *Pro Tip: Use [Gear Lever](https://github.com/mijorus/gearlever) to manage AppImage integration.*

**Method B: Raw Binary**
For minimalists, download the `OutThink` binary, apply `chmod +x OutThink`, and execute via terminal.

---

## 🚀 Initialization Guide

### 1. Establish Discord Uplink
OutThink pushes data via Webhooks.
1.  **Discord Server Settings** → **Apps & Integrations** → **Webhooks**.
2.  **New Webhook** → Select Target Channel.
3.  **Copy Webhook URL**.

### 2. Configure Engine
1.  Launch OutThink.
2.  Select **"⚙️ Manage Channels"** in the sidebar.
3.  Define a **Sector Name** (e.g., *Engineering, Strategy, Mental Models*).
4.  Input the **Webhook URL**.
5.  **ADD CHANNEL**.

### 3. Execute
* **Target Sector:** Select from the sidebar dropdown.
* **Select Mode:** `Deep Dive` for documentation, `Quick Spark` for axioms.
* **Neural Audio:** Toggle if audio synthesis is required.
* **DEPLOY:** Initiates the processing and upload sequence.

---

## 🛠️ Build from Source

**Prerequisites:** Python 3.10+, `pip`, `git`.

1.  **Clone Repository:**
    ```bash
    git clone https://github.com/landzi1/OutThink.git
    cd OutThink
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Launch:**
    ```bash
    python outthink.py
    ```

---

## 💻 Tech Stack

* **Core Logic:** Python 3.10+
* **GUI Engine:** CustomTkinter (Heavily Modified)
* **Audio Synthesis:** gTTS (Google Neural API), LangDetect
* **Packaging:** PyInstaller, LinuxDeploy (CI/CD via GitHub Actions)

**Engineered by [landzi1](https://github.com/landzi1).**
