<h1 align="center">
  <img src="logo.png" width="55" style="vertical-align: middle; margin-right: 10px;" alt="Logo" />
  OutThink
</h1>

> **The Personal Knowledge Engine.** > Bridge the gap between raw information and your Second Brain.

**OutThink** is a streamlined desktop utility designed to transform summaries, notes, and ideas into high-impact, searchable content on Discord. Unlike standard note-taking apps, OutThink forces structure upon your knowledge, offering both deep-dive analysis and rapid "Headway-style" insights.

It features a minimalist **Cream & Taupe interface**, distraction-free writing environment, and a neural audio engine that turns your notes into podcasts.

---

## 📸 Visual Tour

### The Workspace
A distraction-free, minimalist environment designed for focus.
![Application Interface](assets/app_ui.png)

### The Output (Discord)
Your knowledge, formatted beautifully with auto-calculated reading times and category-based color coding.
![Discord Embed Preview](assets/discord_preview.gif)

---

## ✨ Key Features

### 🧠 Dual Knowledge Modes
* **Deep Dive:** For full book summaries or complex topics. Supports rich text formatting via a built-in toolbar (`Bold`, `Italic`, `Quotes`, `Lists`). Automatically splits long texts into readable chunks.
* **⚡ Quick Spark (New):** A "Headway/Blinkist" style mode. Forces you to distill knowledge into **3 Key Insights** (Concept, Mechanism, Outcome). Renders on Discord with a specialized, high-impact structure.

### 🎨 Elite UI & Aesthetics
* **Minimalist Design:** A clean "Cream & Off-White" theme that reduces eye strain and promotes clarity.
* **Smart Formatting:** Automatically calculates **Reading Time** and applies professional formatting to Discord embeds.
* **Category Coloring:** Assigns distinct, muted luxury colors to categories (e.g., *Business* = Stone Grey, *Psychology* = Taupe).

### 🎧 Neural Audio Engine
* **Text-to-Speech:** Automatically converts your notes into an MP3 file and uploads it alongside the text. Perfect for reviewing knowledge on the go.
* **Auto-Language Detection:** Seamlessly switches between English and Polish based on content.

### ⚙️ User-Friendly Configuration
* **In-App Channel Manager:** No more editing configuration files. Add, name, and manage your Discord Webhooks directly within the application's settings GUI.
* **Cross-Platform:** Native support for **Windows** (.exe) and **Linux** (AppImage & Binary).

---

## 📥 Installation

Go to the **[Releases Page](../../releases)** to download the latest version (`v1.5` or newer).

### 🪟 Windows
1.  Download `OutThink.exe`.
2.  Double-click to run.
    * *Note: If Windows SmartScreen appears, click "More info" -> "Run anyway".*

### 🐧 Linux (Universal)
We provide an **AppImage** compatible with Ubuntu, Fedora, Bazzite, SteamOS, and Arch.

**Option A: AppImage (Recommended)**
1.  Download `OutThink.AppImage`.
2.  Right-click → Properties → Permissions → **"Allow executing file as program"**.
3.  Double-click to run.
    * *Tip: Use **Gear Lever** to integrate it into your system menu/dock.*

**Option B: Standalone Binary**
If you prefer raw binaries, download the file named `OutThink` (no extension), `chmod +x OutThink`, and run `./OutThink` in the terminal.

---

## ⚡ Quick Start Guide

### 1. Setting up Discord Webhooks
OutThink sends data to your Discord server via Webhooks. Here is how to get one:

1.  Open **Discord** and go to your server settings.
2.  Navigate to **Apps & Integrations** → **Webhooks**.
3.  Click **"New Webhook"**.
4.  Choose the channel where you want notes to appear.
5.  Click **"Copy Webhook URL"**.

### 2. Configuring OutThink
1.  Open OutThink.
2.  Click the **"⚙️ Manage Channels"** button in the sidebar.
3.  Enter a **Category Name** (e.g., *Business*, *Coding*, *Life Ops*).
4.  Paste the **Webhook URL** you copied from Discord.
5.  Click **ADD CHANNEL**.
    * *You can add as many channels as you like. They will appear in the main dropdown menu.*

### 3. Using the App
* **Select a Target Sector:** Choose the category from the sidebar dropdown.
* **Choose Mode:**
    * Use **Deep Dive** for standard notes. Use the toolbar for formatting.
    * Use **Quick Spark** for 3-point summaries.
* **Neural Audio:** Check the box in the sidebar if you want an MP3 file generated.
* **Deploy:** Click **EXECUTE DEPLOYMENT** to send data to your Second Brain.

---

## 🛠️ Build from Source

Requirements: Python 3.10+, `pip`, `git`.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/landzi1/OutThink.git](https://github.com/landzi1/OutThink.git)
    cd OutThink
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python outthink.py
    ```

---

## 💻 Tech Stack

* **Core:** Python 3.10+
* **UI Framework:** CustomTkinter (Modified)
* **Audio:** gTTS (Google Text-to-Speech), LangDetect
* **Build System:** PyInstaller, LinuxDeploy (via GitHub Actions)

**Created by [landzi1](https://github.com/landzi1).**
