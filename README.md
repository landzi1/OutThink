# BookSummarizer

![BookSummarizer Logo](logo.jpg)

**BookSummarizer** is a streamlined desktop utility designed to act as your personal knowledge engine. It bridges the gap between raw AI summaries and your "Second Brain" on Discord.

It converts text summaries into clean, searchable Discord embeds and automatically generates audio versions (TTS) in English or Polish, featuring a distraction-free dark interface.

## ✨ Key Features

* **Cross-Platform:** Native support for **Windows** (.exe) and **Linux** (.AppImage).
* **Auto-Generated Audio:** Automatically detects language (EN/PL) and synthesizes MP3 summaries via Google Neural TTS.
* **Discord Integration:** Sends formatted, white-label embeds directly to your server.
* **Smart Splitting:** Automatically handles long texts, bypassing Discord's 4096-character limit.
* **Distraction-Free UI:** Built with CustomTkinter for a focus-centric dark mode experience.

## 📥 Download

Go to the **[Releases Page](../../releases)** to download the latest version for your system.

## 🚀 How to Run

### 🪟 Windows
1.  Download `BookSummarizer.exe` from the Releases page.
2.  Double-click to run.
    * *Note: If Windows SmartScreen appears (because the app is not digitally signed), click "More info" -> "Run anyway".*

### 🐧 Linux (AppImage)
BookSummarizer is distributed as an **AppImage**, which works on almost all Linux distributions (Ubuntu, Fedora, Arch, Bazzite, SteamOS) without installation.

#### Option A: Using AppImage Managers (Recommended)
For the best experience (system integration, icon in menu), use a manager like **Gear Lever** or **AppImageLauncher**.

* **Gear Lever:** Open Gear Lever, drag and drop `BookSummarizer.AppImage` into the window, and click "Integrate".
* **AppImageLauncher:** Double-click the file and select "Integrate and run".

#### Option B: The "Quick Run" (Terminal)
1.  Open your terminal in the downloads folder.
2.  Make the file executable:
    ```bash
    chmod +x BookSummarizer.AppImage
    ```
3.  Run it:
    ```bash
    ./BookSummarizer.AppImage
    ```

#### Option C: GUI Method
Right-click the file → **Properties** → **Permissions** → Check **"Allow executing file as program"**. Then just double-click it.

---

## ⚙️ Configuration (First Run)

The application requires Discord Webhook URLs to function. You have two ways to configure them:

**Method 1: The `.env` file (Recommended for portability)**
Create a file named `.env` in the same folder as the application and add your links:
```env
WH_BIZ="your_business_webhook_url"
WH_PSY="your_psychology_webhook_url"
WH_SCI="your_science_webhook_url"
WH_OTH="your_other_webhook_url"
```

## 🛠️ Build from Source

If you prefer to run the raw Python code or build it yourself:

    **Clone the repository:**
    ```bash
    git clone [https://github.com/landzi1/BookSummarizer.git](https://github.com/landzi1/BookSummarizer.git)
    cd BookSummarizer
    ```

    **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    **Run the application:**
    ```bash
    python booksummarizer.py
    ```
## 💻 Tech Stack

* **Core: Python 3.10+**

* **GUI:** CustomTkinter

* **Audio Engine:** gTTS, LangDetect

* **Build System:** PyInstaller, LinuxDeploy (GitHub Actions)

Created by [landzi1](https://github.com/landzi1).
