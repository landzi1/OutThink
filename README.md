# BookSummarizer // Elite Knowledge Engine 🧠

![Status](https://img.shields.io/badge/Status-Stable-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)

**BookSummarizer** is a high-performance desktop tool for ambitious learners. It bridges the gap between AI-generated knowledge summaries and your personal "Second Brain" on Discord.

Designed for productivity enthusiasts who want to curate, digest, and archive knowledge with zero friction.

## ✨ Features

* **Cyber-Minimalist UI:** Built with CustomTkinter, featuring a Zinc/Indigo dark theme.
* **Discord Integration:** Sends beautifully formatted white-label embeds directly to your categorized Discord channels.
* **Neural Audio:** Automatically detects language (EN/PL) and generates an MP3 summary using Google TTS.
* **Smart Splitting:** Automatically handles long summaries by splitting them into multiple parts (bypassing Discord's 4096 char limit).
* **Privacy First:** Webhooks are handled via environment variables.

## 🚀 Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/BookSummarizer.git](https://github.com/YOUR_USERNAME/BookSummarizer.git)
    cd BookSummarizer
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration:**
    Create a `.env` file in the root directory and add your Discord Webhook URLs:
    ```env
    WH_BIZ="your_business_webhook_url"
    WH_PSY="your_psychology_webhook_url"
    WH_SCI="your_science_webhook_url"
    WH_OTH="your_other_webhook_url"
    ```
    *Alternatively, you can hardcode them in `main.py` (not recommended for public repos).*

4.  **Add Logo:**
    Place a `logo.jpg` file in the root folder (it will be automatically rounded and processed).

5.  Run the engine:
    ```bash
    python main.py
    ```

## 🛠 Tech Stack

* **GUI:** CustomTkinter
* **Audio:** gTTS (Google Text-to-Speech)
* **Processing:** Pillow (Image Ops), LangDetect (Polyglot support)
* **Network:** Requests (Webhook Payloads)

## 👤 Author

**landzi1**
* [GitHub Profile](https://github.com/landzi1)

---
*Built for the Elite Ball Knowledge community.*
