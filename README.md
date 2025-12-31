# OutThink

![OutThink Banner](assets/banner.png)
<!-- GRAFIKA: Minimalistyczny banner z logo i hasłem np. "Your Knowledge Engine" -->

OutThink is a desktop tool built for people who consume a lot of content but struggle to retain and organize it. It bridges the gap between where you learn (YouTube, articles, books) and where you store your knowledge (Notion, Obsidian, Discord).

Instead of manually copy-pasting notes between apps, OutThink automates the distillation process using AI and handles the distribution to your personal databases.

## What you can do with it

### 1. Turn YouTube videos into structured notes
Paste a link to any YouTube video (lectures, podcasts, tutorials). OutThink grabs the transcript and uses AI (Groq Llama 3) to generate a summary. You can choose between:
*   **Quick Spark**: 3 key takeaways, perfect for a quick review.
*   **Deep Dive**: A detailed, essay-style summary with headers and key points.

![YouTube Workflow](assets/youtube_demo.gif)
<!-- GIF: Wklejasz link YT, klikasz enter, pojawia się podsumowanie. -->

### 2. Chat with an AI Editor
The built-in assistant isn't just a summarizer. You can treat it as an editor. Paste a rough draft or a messy article and ask it to:
*   "Fix the grammar and make it punchy."
*   "Format this for a Discord announcement."
*   "Extract all book recommendations from this text."

![Chatbot](assets/chatbot.png)
<!-- SCREENSHOT: Rozmowa z asystentem w zakładce AI Assistant. -->

### 3. Build a "Second Brain" automatically
When you save a note in OutThink, it doesn't just disappear. You can configure it to instantly:
*   **Create a page in Notion** with properties like Author, Category, and Date filled out.
*   **Save a Markdown file** to your local folder (great for Obsidian or Logseq users).
*   **Post to Discord** as a formatted embed to share knowledge with your community.

You can toggle these targets on or off for every note.

![Deployment](assets/deployment.png)
<!-- SCREENSHOT: Panel Target Systems i przycisk Execute. -->

### 4. Listen to your notes
OutThink can read your notes back to you using high-quality neural text-to-speech (Edge TTS). It automatically detects if the text is in English or Polish and selects a natural-sounding voice. This is useful for reviewing your notes while commuting or walking.

### 5. Never lose a thought
Every note you process is saved in a local history (SQLite database). You can browse your archive, search for past insights, and re-export them at any time.

---

## Getting Started

### Requirements
*   Windows or Linux
*   Python 3.10+ (if running from source)
*   Free Groq API Key (for AI features)

### Installation

**Option A: Download**
Grab the latest release for your OS from the [Releases page](../../releases).

**Option B: Run from source**
1.  Clone this repository.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run the app: `python outthink.py`

### First Run Setup
Click the **Settings (⚙️)** button in the sidebar to connect your services:
1.  **Groq API**: Required for AI. It's free and fast.
2.  **Notion**: Optional. Follow the in-app guide to connect your database.
3.  **Local Backup**: Optional. Select a folder where you want your .md files.

---

## Tech Stack
Built with Python.
*   **UI**: CustomTkinter
*   **AI**: Groq API (Llama 3)
*   **Audio**: Edge TTS
*   **Integrations**: Notion API, Discord Webhooks, YouTube Transcript API
*   **Data**: SQLite

---

**Created by [Landzi1](https://github.com/landzi1)**
