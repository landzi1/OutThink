# BookSummarizer

![BookSummarizer Logo](logo.jpg)

**BookSummarizer** is a modern desktop utility that streamlines the process of capturing, synthesizing, and archiving knowledge directly to your Discord server.

It converts text summaries into clean, searchable Discord embeds and automatically generates audio versions (TTS) in English or Polish, creating a personal "second brain" for your knowledge.

## ✨ Key Features

* **Modern Dark UI:** Clean interface built with CustomTkinter, featuring a dark theme and responsive inputs.
* **Auto-Generated Audio:** Automatically detects language (EN/PL) and converts summaries to MP3 using Google TTS.
* **Clean Discord Embeds:** Formatted for readability with a clean white style.
* **Smart Message Splitting:** Automatically handles long texts by bypassing Discord's character limits.
* **Secure Configuration:** Webhooks are handled via environment variables for security.

## 🚀 Getting Started

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/BookSummarizer.git](https://github.com/YOUR_USERNAME/BookSummarizer.git)
    cd BookSummarizer
    ```

2.  **Install dependencies:**
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

4.  **Run the application:**
    ```bash
    python main.py
    ```

## 🛠️ Tech Stack

* **Python 3.10+**
* **GUI:** CustomTkinter
* **Audio:** gTTS, LangDetect
* **Processing:** Pillow (PIL)
* **Network:** Requests

---
Created by [landzi1](https://github.com/landzi1).
