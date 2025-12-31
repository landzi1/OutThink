# OutThink // The Personal Knowledge Engine

![OutThink Banner](assets/banner.png)
<!-- GRAFIKA: Banner z logo OutThink i hasłem "Consume. Distill. Deploy." -->

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**OutThink** is a comprehensive knowledge management system designed for power users. It bridges the gap between passive consumption (YouTube, Articles) and active retention (Notion, Obsidian), powered by advanced AI and Neural Audio synthesis.

It's not just a note-taking app; it's your personal **Editor-in-Chief**.

---

## ⚡ Key Capabilities

### 🎥 YouTube Intelligence
Paste any YouTube link, and OutThink will watch it for you. It extracts the transcript, analyzes the content using **Groq AI (Llama 3)**, and generates a structured summary (Deep Dive) or key insights (Quick Spark).

![YouTube Workflow](assets/youtube_demo.gif)
<!-- GIF: Pokaż wklejanie linku YT do czatu AI Assistant i generowanie wyniku. -->

### 🧠 AI Assistant Chatbot
Interact with your content. Ask the built-in chatbot to refine ideas, expand on concepts, or format text for specific platforms.

![Chatbot](assets/chatbot.png)
<!-- SCREENSHOT: Widok zakładki AI Assistant z rozmową. -->

### 🔗 Multi-Target Deployment
One click sends your distilled knowledge everywhere:
*   **Discord**: Beautifully formatted embeds for your community.
*   **Notion**: Automatically creates database entries with tags and metadata.
*   **Local Vault**: Saves Markdown (`.md`) files for Obsidian/Logseq.

![Deployment](assets/deployment.png)
<!-- SCREENSHOT: Pokaż panel "Target Systems" i przycisk Execute. -->

### 🎧 Neural Audio
Turn your notes into a private podcast using Microsoft's Edge TTS neural voices. Perfect for reviewing knowledge on the go.

---

## 🛠️ Installation & Setup

### Prerequisites
1.  **Python 3.10+** installed.
2.  **Groq API Key** (Free) - for AI features.
3.  **Notion Integration** (Optional) - for syncing.

### Quick Start
```bash
# 1. Clone the repository
git clone https://github.com/landzi1/OutThink.git
cd OutThink

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
python outthink.py
```

### Configuration
Click the **⚙️ Settings** icon in the app to configure your API keys.
*   **Groq API**: Get your key at [console.groq.com](https://console.groq.com).
*   **Notion**: Create an integration at [notion.so/my-integrations](https://www.notion.so/my-integrations).

---

## 🏗️ Build from Source

You can build standalone executables for Windows and Linux.

**Linux (AppImage & Binary):**
```bash
# Requires pyinstaller, linuxdeploy, and appimagetool
# Check .github/workflows/build.yml for the full CI/CD pipeline
```

**Windows (.exe):**
```bash
pyinstaller --noconfirm --onefile --windowed --name "OutThink" --add-data "logo.png;." --collect-all customtkinter --hidden-import=PIL --hidden-import=edge_tts --hidden-import=langdetect --hidden-import=notion_client --hidden-import=youtube_transcript_api --hidden-import=requests outthink.py
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Engineered by [Landzi1](https://github.com/landzi1)**