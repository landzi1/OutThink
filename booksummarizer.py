import sys
import customtkinter as ctk
import requests
import webbrowser
import os
import threading
from datetime import datetime
from gtts import gTTS
from PIL import Image, ImageTk, ImageDraw, ImageOps
from dotenv import load_dotenv
from langdetect import detect

# --- SYSTEM CONFIGURATION ---
load_dotenv()

# Color Palette (Elite Dark Theme)
COLOR_BG_MAIN = "#09090B"       # Zinc 950
COLOR_BG_SIDE = "#18181B"       # Zinc 900
COLOR_ACCENT = "#6366F1"        # Indigo 500
COLOR_ACCENT_HOVER = "#4F46E5"  # Indigo 600
COLOR_TEXT_MAIN = "#FAFAFA"     # Zinc 50
COLOR_TEXT_SEC = "#A1A1AA"      # Zinc 400
COLOR_INPUT_BG = "#27272A"      # Zinc 800
COLOR_BORDER = "#3F3F46"        # Zinc 700

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# WEBHOOK CONFIGURATION
# Ensure you have a .env file or replace the fallbacks below
WEBHOOKS = {
    "Business & Finance": os.getenv("WH_BIZ", "PASTE_WEBHOOK_URL_HERE"),
    "Psychology & Relations": os.getenv("WH_PSY", "PASTE_WEBHOOK_URL_HERE"),
    "Philosophy & Science": os.getenv("WH_SCI", "PASTE_WEBHOOK_URL_HERE"),
    "Other": os.getenv("WH_OTH", "PASTE_WEBHOOK_URL_HERE")
}

DEFAULT_PLACEHOLDER = "Enter your summary or content here..."

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class BookSummarizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Window Setup
        self.title("BookSummarizer // Knowledge Engine")
        self.geometry("1100x900")
        self.minsize(950, 800)
        self.configure(fg_color=COLOR_BG_MAIN)

        # 2. Logo Processing
        self.sidebar_logo = None
        try:
            raw_img = Image.open("logo.jpg").convert("RGBA")
            size = (140, 140)
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            output = ImageOps.fit(raw_img, size, centering=(0.5, 0.5))
            output.putalpha(mask)

            self.icon_photo = ImageTk.PhotoImage(output)
            self.wm_iconphoto(True, self.icon_photo)

            display_size = (90, 90)
            output_small = output.resize(display_size, Image.Resampling.LANCZOS)
            self.sidebar_logo = ctk.CTkImage(light_image=output_small, dark_image=output_small, size=display_size)
        except Exception:
            pass

        # Grid Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=COLOR_BG_SIDE)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)

        self.brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.brand_frame.grid(row=0, column=0, padx=30, pady=(50, 20), sticky="ew")

        if self.sidebar_logo:
            self.lbl_logo = ctk.CTkLabel(self.brand_frame, text="", image=self.sidebar_logo)
            self.lbl_logo.pack(anchor="center", pady=(0, 15))

        self.lbl_app_name = ctk.CTkLabel(self.brand_frame, text="BookSummarizer",
                                       font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                                       text_color=COLOR_TEXT_MAIN)
        self.lbl_app_name.pack(anchor="center")

        self.lbl_ver = ctk.CTkLabel(self.brand_frame, text="v4.5 STABLE",
                                  font=ctk.CTkFont(family="JetBrains Mono", size=10),
                                  text_color=COLOR_ACCENT)
        self.lbl_ver.pack(anchor="center", pady=(2, 0))

        self.sep = ctk.CTkFrame(self.sidebar, height=1, fg_color=COLOR_BORDER)
        self.sep.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 30))

        self._create_sidebar_label("TARGET FREQUENCY", 2)
        self.combo_cat = ctk.CTkOptionMenu(self.sidebar, values=list(WEBHOOKS.keys()),
                                         width=240, height=45, corner_radius=12,
                                         fg_color=COLOR_INPUT_BG, button_color=COLOR_INPUT_BG,
                                         button_hover_color=COLOR_BORDER, text_color=COLOR_TEXT_MAIN,
                                         dropdown_fg_color=COLOR_BG_SIDE, font=ctk.CTkFont(size=13))
        self.combo_cat.grid(row=3, column=0, padx=30, pady=(0, 20))

        self._create_sidebar_label("SYSTEM OVERRIDE", 4)
        self.audio_var = ctk.BooleanVar(value=True)
        self.chk_audio = ctk.CTkCheckBox(self.sidebar, text="Generate Neural Audio",
                                       variable=self.audio_var, onvalue=True, offvalue=False,
                                       font=ctk.CTkFont(size=13), fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
                                       border_color=COLOR_TEXT_SEC, border_width=2, corner_radius=4)
        self.chk_audio.grid(row=5, column=0, padx=30, pady=0, sticky="w")

        self.footer_lbl = ctk.CTkLabel(self.sidebar, text="ENGINEERED BY LANDZI1",
                                     font=("JetBrains Mono", 10), text_color=COLOR_TEXT_SEC, cursor="hand2")
        self.footer_lbl.grid(row=8, column=0, pady=30)
        self.footer_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/landzi1"))

        # ================= MAIN AREA =================
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=50, pady=50)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(3, weight=1)

        self.header_title = ctk.CTkLabel(self.main_area, text="Initialize Upload",
                                       font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
                                       text_color=COLOR_TEXT_MAIN, anchor="w")
        self.header_title.grid(row=0, column=0, sticky="w", pady=(0, 25))

        # 1. Input: Title
        self.entry_book = ctk.CTkEntry(self.main_area, placeholder_text="Enter source title...",
                                     height=55, font=("Segoe UI", 16), fg_color=COLOR_INPUT_BG,
                                     border_width=1, border_color=COLOR_BORDER, corner_radius=12,
                                     text_color=COLOR_TEXT_MAIN, placeholder_text_color=COLOR_TEXT_SEC)
        self.entry_book.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        # 2. Input: Author
        self.entry_author = ctk.CTkEntry(self.main_area, placeholder_text="Enter Author Name...",
                                     height=55, font=("Segoe UI", 16), fg_color=COLOR_INPUT_BG,
                                     border_width=1, border_color=COLOR_BORDER, corner_radius=12,
                                     text_color=COLOR_TEXT_MAIN, placeholder_text_color=COLOR_TEXT_SEC)
        self.entry_author.grid(row=2, column=0, sticky="ew", pady=(0, 20))

        # 3. Main Textbox
        self.textbox = ctk.CTkTextbox(self.main_area, font=("Segoe UI", 15), corner_radius=12,
                                    border_width=1, border_color=COLOR_BORDER,
                                    fg_color=COLOR_INPUT_BG, text_color=COLOR_TEXT_MAIN, wrap="word")
        self.textbox.grid(row=3, column=0, sticky="nsew", pady=(0, 10))

        # Placeholder Logic Setup
        self.textbox.insert("0.0", DEFAULT_PLACEHOLDER)
        self.textbox.bind("<FocusIn>", self.on_focus_in)
        self.textbox.bind("<FocusOut>", self.on_focus_out)
        self.textbox.bind("<Control-a>", self.select_all_text)

        # Binds for Entries
        self.entry_book.bind("<Control-a>", self.select_all_entry)
        self.entry_author.bind("<Control-a>", lambda e: self.select_all_entry(e, self.entry_author))

        # Character Counter
        self.char_counter = ctk.CTkLabel(self.main_area, text="0 chars", text_color=COLOR_TEXT_SEC, font=("JetBrains Mono", 12))
        self.char_counter.grid(row=4, column=0, sticky="e", padx=5)
        self.textbox.bind("<KeyRelease>", self.update_char_count)

        # Deploy Button
        self.btn_send = ctk.CTkButton(self.main_area, text="EXECUTE DEPLOYMENT",
                                    height=65, font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                                    fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, corner_radius=32,
                                    command=self.start_processing)
        self.btn_send.grid(row=5, column=0, sticky="ew", pady=(20,0))

    # --- UI LOGIC ---
    def _create_sidebar_label(self, text, row):
        label = ctk.CTkLabel(self.sidebar, text=text, anchor="w",
                           font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                           text_color=COLOR_TEXT_SEC)
        label.grid(row=row, column=0, padx=30, pady=(25, 8), sticky="w")

    def on_focus_in(self, event):
        """Clears placeholder when user clicks the textbox."""
        if self.textbox.get("0.0", "end").strip() == DEFAULT_PLACEHOLDER:
            self.textbox.delete("0.0", "end")
            self.textbox.configure(text_color=COLOR_TEXT_MAIN)

    def on_focus_out(self, event):
        """Restores placeholder if empty."""
        if not self.textbox.get("0.0", "end").strip():
            self.textbox.insert("0.0", DEFAULT_PLACEHOLDER)
            self.textbox.configure(text_color=COLOR_TEXT_SEC)

    def select_all_text(self, event):
        self.textbox.tag_add("sel", "1.0", "end")
        return "break"

    def select_all_entry(self, event, widget=None):
        target = widget if widget else self.entry_book
        target.select_range(0, 'end')
        target.icursor('end')
        return "break"

    def update_char_count(self, event):
        text = self.textbox.get("0.0", "end").strip()
        if text == DEFAULT_PLACEHOLDER:
            text_len = 0
        else:
            text_len = len(text)
        self.char_counter.configure(text=f"{text_len} chars")

    def start_processing(self):
        threading.Thread(target=self.send_data).start()

    def smart_split(self, text, limit=3800):
        """Splits text into chunks respecting word boundaries."""
        chunks = []
        while len(text) > limit:
            split_idx = text.rfind(' ', 0, limit)
            if split_idx == -1:
                split_idx = limit

            chunks.append(text[:split_idx])
            text = text[split_idx:].strip()
        chunks.append(text)
        return chunks

    def send_data(self):
        category = self.combo_cat.get()
        book_title = self.entry_book.get()
        book_author = self.entry_author.get()
        content = self.textbox.get("0.0", "end").strip()
        generate_audio = self.audio_var.get()

        # Validation
        if len(content) < 5 or content == DEFAULT_PLACEHOLDER:
            self.update_button_status("⚠️ NO DATA DETECTED", "#DC2626", True)
            return

        webhook_url = WEBHOOKS[category]
        if not webhook_url or "PASTE" in str(webhook_url):
            self.update_button_status("⚠️ CONFIG ERROR (WEBHOOK)", "#D97706", True)
            return

        self.update_button_status("DEPLOYING TO DISCORD... 🚀", "#27272A")

        full_title = book_title
        if book_author:
            full_title = f"{book_title} — {book_author}"

        # 1. Text Processing
        text_chunks = self.smart_split(content, limit=3800)
        total_chunks = len(text_chunks)

        try:
            for i, chunk in enumerate(text_chunks):
                title_text = full_title if i == 0 else f"{full_title} (Part {i+1}/{total_chunks})"

                embed = {
                    "title": title_text,
                    "description": chunk,
                    "color": 0xFFFFFF, # White Color
                    "thumbnail": {"url": "https://cdn-icons-png.flaticon.com/512/2983/2983808.png"},
                    "footer": {"text": f"Vector: {category} • BrainOS • Part {i+1}/{total_chunks}"},
                    "timestamp": datetime.now().isoformat()
                }

                response = requests.post(webhook_url, json={"embeds": [embed]})
                if response.status_code != 204:
                    print(f"Error sending part {i+1}: {response.text}")
                    self.update_button_status("❌ DISCORD REJECTED TEXT", "#DC2626", True)
                    return

        except Exception as e:
            print(e)
            self.update_button_status("❌ CONNECTION ERROR", "#DC2626", True)
            return

        # 2. Audio Processing
        if generate_audio:
            self.update_button_status("DETECTING LANG & SYNTHESIZING... 🎧", "#27272A")
            try:
                try:
                    detected_lang = detect(content)
                except:
                    detected_lang = 'en' # Default fallback

                print(f"Detected language: {detected_lang}")

                clean_text = content.replace("*", "").replace("#", "").replace(">", "").replace("_", "")

                # Dynamic intro
                intro_text = f"Summary of {book_title}." if detected_lang == 'en' else f"Podsumowanie {book_title}."
                if detected_lang not in ['en', 'pl']:
                     intro_text = ""

                filename = "cache_audio.mp3"
                tts = gTTS(text=f"{intro_text} {clean_text}", lang=detected_lang)
                tts.save(filename)

                with open(filename, 'rb') as f:
                    requests.post(webhook_url, files={'file': (filename, f)})

                if os.path.exists(filename): os.remove(filename)
            except Exception as e:
                print(f"Audio error: {e}")

        self.update_button_status("✅ DEPLOYMENT COMPLETE", "#059669", True)

        # UI Cleanup
        self.after(2000, lambda: self.textbox.delete("0.0", "end"))
        self.after(2000, lambda: self.textbox.insert("0.0", DEFAULT_PLACEHOLDER))
        self.after(2000, lambda: self.entry_book.delete(0, "end"))
        self.after(2000, lambda: self.entry_author.delete(0, "end"))
        self.after(2000, lambda: self.char_counter.configure(text="0 chars"))

    def update_button_status(self, text, fg_color, temporary=False):
        self.btn_send.configure(text=text, fg_color=fg_color)
        if temporary:
             self.btn_send.configure(state="disabled")
             self.after(3000, lambda: self.btn_send.configure(text="EXECUTE DEPLOYMENT", fg_color=COLOR_ACCENT, state="normal"))

if __name__ == "__main__":
    app = BookSummarizerApp()
    app.mainloop()
