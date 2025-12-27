import customtkinter as ctk
import requests
import webbrowser
import os
import threading
import sys
import math
import json
from datetime import datetime
from gtts import gTTS
from PIL import Image, ImageTk, ImageDraw, ImageOps
# from dotenv import load_dotenv # Niepotrzebne, bo config.json
from langdetect import detect
from tkinter import messagebox

# --- SYSTEM CONFIGURATION ---
CONFIG_FILE = "config.json"

# --- PALETTE: Cream & Taupe ---
COLOR_BG_MAIN = "#FDFCF8"
COLOR_BG_SIDE = "#F2EFE7"
COLOR_ACCENT = "#8C8678"
COLOR_ACCENT_HOVER = "#6B6659"
COLOR_TEXT_MAIN = "#2D2A26"
COLOR_TEXT_SEC = "#6E6A60"
COLOR_INPUT_BG = "#FFFFFF"
COLOR_BORDER = "#E0DCD0"
COLOR_TOOLBAR = "#F7F5F0"
COLOR_ERROR = "#DC2626"
COLOR_SUCCESS = "#059669"

# --- PREDEFINED COLORS ---
CAT_COLORS = {
    "Business & Strategy": 0xA8A29E,       # Stone Grey
    "Psychology & Human Nature": 0x8C8678, # Taupe
    "Philosophy & Science": 0xD6D3D1,      # Light Warm Grey
    "Tech & Future": 0x78716C              # Darker Earth
}

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

DEFAULT_PLACEHOLDER = "Paste your knowledge stream here..."

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class OutThinkApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        try:
            self.wm_class("OutThink", "OutThink")
        except:
            pass

        # 0. Load Configuration
        self.webhooks = self.load_config()

        # 1. Window Configuration
        self.title("OutThink")
        self.geometry("1100x900")
        self.minsize(950, 850)
        self.configure(fg_color=COLOR_BG_MAIN)

        # 2. Logo Processing
        self.sidebar_logo = None
        try:
            img_path = resource_path("logo.png")
            raw_img = Image.open(img_path).convert("RGBA")

            safe_icon = raw_img.resize((256, 256), Image.Resampling.LANCZOS)

            self.system_icon = ImageTk.PhotoImage(safe_icon)
            self.iconphoto(False, self.system_icon)
            # ---------------------------------------

            display_size = (110, 110)
            output_img = raw_img.resize(display_size, Image.Resampling.LANCZOS)
            self.sidebar_logo = ctk.CTkImage(light_image=output_img, dark_image=output_img, size=display_size)
        except Exception as e:
            print(f"Warning: Logo loading failed: {e}")

        # 3. Grid Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=COLOR_BG_SIDE)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        self.brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.brand_frame.grid(row=0, column=0, padx=30, pady=(50, 20), sticky="ew")

        if self.sidebar_logo:
            self.lbl_logo = ctk.CTkLabel(self.brand_frame, text="", image=self.sidebar_logo)
            self.lbl_logo.pack(anchor="center", pady=(0, 15))

        self.lbl_app_name = ctk.CTkLabel(self.brand_frame, text="OutThink",
                                       font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
                                       text_color=COLOR_TEXT_MAIN)
        self.lbl_app_name.pack(anchor="center")

        self.lbl_ver = ctk.CTkLabel(self.brand_frame, text="v1.5 STABLE",
                                  font=ctk.CTkFont(family="JetBrains Mono", size=10),
                                  text_color=COLOR_ACCENT)
        self.lbl_ver.pack(anchor="center", pady=(2, 0))

        self.sep = ctk.CTkFrame(self.sidebar, height=1, fg_color=COLOR_BORDER)
        self.sep.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 30))

        self._create_sidebar_label("TARGET SECTOR", 2)

        # Dynamic Dropdown Values
        webhook_keys = list(self.webhooks.keys()) if self.webhooks else ["No Channels Configured"]

        self.combo_cat = ctk.CTkOptionMenu(self.sidebar, values=webhook_keys,
                                         width=240, height=45, corner_radius=12,
                                         fg_color=COLOR_INPUT_BG, button_color=COLOR_INPUT_BG,
                                         button_hover_color=COLOR_BORDER, text_color=COLOR_TEXT_MAIN,
                                         dropdown_fg_color=COLOR_BG_SIDE, font=ctk.CTkFont(size=13))
        self.combo_cat.grid(row=3, column=0, padx=30, pady=(0, 20))

        # Settings Button
        self.btn_settings = ctk.CTkButton(self.sidebar, text="⚙️  Manage Channels",
                                          fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
                                          height=40, font=ctk.CTkFont(size=12, weight="bold"),
                                          command=self.open_settings_window)
        self.btn_settings.grid(row=4, column=0, padx=30, pady=(0, 20), sticky="ew")

        self._create_sidebar_label("SYSTEM OVERRIDE", 5)
        self.audio_var = ctk.BooleanVar(value=True)
        self.chk_audio = ctk.CTkCheckBox(self.sidebar, text="Neural Audio Synthesis",
                                       variable=self.audio_var, onvalue=True, offvalue=False,
                                       font=ctk.CTkFont(size=13), fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
                                       border_color=COLOR_TEXT_SEC, border_width=2, corner_radius=4,
                                       text_color=COLOR_TEXT_MAIN)
        self.chk_audio.grid(row=6, column=0, padx=30, pady=0, sticky="w")

        self.footer_lbl = ctk.CTkLabel(self.sidebar, text="ENGINEERED BY LANDZI1",
                                     font=("JetBrains Mono", 10), text_color=COLOR_TEXT_SEC, cursor="hand2")
        self.footer_lbl.grid(row=9, column=0, pady=30)
        self.footer_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/landzi1"))

        # ================= MAIN AREA =================
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=50, pady=40)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(4, weight=1)

        self.header_title = ctk.CTkLabel(self.main_area, text="Initialize Upload",
                                       font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
                                       text_color=COLOR_TEXT_MAIN, anchor="w")
        self.header_title.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Metadata Inputs
        self.meta_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.meta_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.meta_frame.grid_columnconfigure(0, weight=1)
        self.meta_frame.grid_columnconfigure(1, weight=1)

        self.entry_book = ctk.CTkEntry(self.meta_frame, placeholder_text="Source Title...",
                                     height=50, font=("Segoe UI", 16), fg_color=COLOR_INPUT_BG,
                                     border_width=1, border_color=COLOR_BORDER, corner_radius=12,
                                     text_color=COLOR_TEXT_MAIN, placeholder_text_color=COLOR_TEXT_SEC)
        self.entry_book.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.entry_author = ctk.CTkEntry(self.meta_frame, placeholder_text="Author Name...",
                                     height=50, font=("Segoe UI", 16), fg_color=COLOR_INPUT_BG,
                                     border_width=1, border_color=COLOR_BORDER, corner_radius=12,
                                     text_color=COLOR_TEXT_MAIN, placeholder_text_color=COLOR_TEXT_SEC)
        self.entry_author.grid(row=0, column=1, sticky="ew", padx=(10, 0))

        # --- TAB SYSTEM ---
        self.tab_view = ctk.CTkTabview(self.main_area, fg_color="transparent",
                                       text_color=COLOR_TEXT_MAIN,
                                       segmented_button_fg_color=COLOR_BG_SIDE,
                                       segmented_button_selected_color=COLOR_ACCENT,
                                       segmented_button_selected_hover_color=COLOR_ACCENT_HOVER,
                                       segmented_button_unselected_color=COLOR_BG_SIDE,
                                       segmented_button_unselected_hover_color=COLOR_BORDER)
        self.tab_view.grid(row=3, column=0, sticky="nsew")

        self.tab_view.add("Deep Dive")
        self.tab_view.add("Quick Spark")

        # --- TAB 1: DEEP DIVE ---
        self.tab_view.tab("Deep Dive").grid_columnconfigure(0, weight=1)
        self.tab_view.tab("Deep Dive").grid_rowconfigure(1, weight=1)

        self.toolbar_frame = ctk.CTkFrame(self.tab_view.tab("Deep Dive"), height=40, fg_color=COLOR_TOOLBAR, corner_radius=8)
        self.toolbar_frame.grid(row=0, column=0, sticky="ew", pady=(5, 5))

        self._create_format_btn(self.toolbar_frame, "B", self.fmt_bold, 0)
        self._create_format_btn(self.toolbar_frame, "I", self.fmt_italic, 1)
        self._create_format_btn(self.toolbar_frame, "“ ”", self.fmt_quote, 2)
        self._create_format_btn(self.toolbar_frame, "• List", self.fmt_list, 3)
        self._create_format_btn(self.toolbar_frame, "H1", self.fmt_h1, 4)

        self.btn_help = ctk.CTkButton(self.toolbar_frame, text="?", width=30, height=30,
                                      fg_color="transparent", border_width=1, border_color=COLOR_BORDER,
                                      text_color=COLOR_ACCENT, hover_color=COLOR_BG_SIDE,
                                      command=self.open_guide_window)
        self.btn_help.grid(row=0, column=6, padx=10, sticky="e")

        self.textbox = ctk.CTkTextbox(self.tab_view.tab("Deep Dive"), font=("Segoe UI", 15), corner_radius=12,
                                    border_width=1, border_color=COLOR_BORDER,
                                    fg_color=COLOR_INPUT_BG, text_color=COLOR_TEXT_MAIN, wrap="word")
        self.textbox.grid(row=1, column=0, sticky="nsew")

        # --- TAB 2: QUICK SPARK ---
        self.tab_view.tab("Quick Spark").grid_columnconfigure(0, weight=1)

        self.lbl_spark = ctk.CTkLabel(self.tab_view.tab("Quick Spark"), text="Distill into 3 High-Impact Insights (Headway Style)",
                                      text_color=COLOR_TEXT_SEC, font=("Segoe UI", 12))
        self.lbl_spark.grid(row=0, column=0, pady=(0, 10), sticky="w")

        self.spark_1 = self._create_spark_entry(self.tab_view.tab("Quick Spark"), "Insight #1: The Core Concept", 1)
        self.spark_2 = self._create_spark_entry(self.tab_view.tab("Quick Spark"), "Insight #2: The Mechanism/Why", 2)
        self.spark_3 = self._create_spark_entry(self.tab_view.tab("Quick Spark"), "Insight #3: Actionable Outcome", 3)

        # Bottom Controls
        self.bottom_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.bottom_frame.grid(row=5, column=0, sticky="ew", pady=(10, 0))

        self.char_counter = ctk.CTkLabel(self.bottom_frame, text="0 chars", text_color=COLOR_TEXT_SEC, font=("JetBrains Mono", 12))
        self.char_counter.pack(side="right")

        self.btn_send = ctk.CTkButton(self.main_area, text="EXECUTE DEPLOYMENT",
                                    height=65, font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                                    fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, corner_radius=32,
                                    command=self.start_processing,
                                    text_color="#FFFFFF")
        self.btn_send.grid(row=6, column=0, sticky="ew", pady=(20,0))

        # Initial Logic
        self.textbox.insert("0.0", DEFAULT_PLACEHOLDER)
        self.textbox.configure(text_color=COLOR_TEXT_SEC)
        self.textbox.bind("<FocusIn>", self.on_focus_in)
        self.textbox.bind("<FocusOut>", self.on_focus_out)
        self.textbox.bind("<KeyRelease>", self.update_char_count)

    # --- CONFIG MANAGER ---
    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            default_data = {}
            with open(CONFIG_FILE, "w") as f:
                json.dump(default_data, f)
            return default_data

        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return {}

    def save_config_file(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.webhooks, f, indent=4)
        except Exception as e:
            print(f"Config save error: {e}")

    # --- SETTINGS WINDOW ---
    def open_settings_window(self):
        self.settings_win = ctk.CTkToplevel(self)
        self.settings_win.title("Manage Channels")
        self.settings_win.geometry("500x600")
        self.settings_win.configure(fg_color=COLOR_BG_MAIN)
        self.settings_win.attributes("-topmost", True)

        ctk.CTkLabel(self.settings_win, text="CHANNEL CONFIGURATION",
                     font=("Segoe UI", 16, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=20)

        add_frame = ctk.CTkFrame(self.settings_win, fg_color="transparent")
        add_frame.pack(fill="x", padx=20)

        self.entry_new_cat = ctk.CTkEntry(add_frame, placeholder_text="Category Name (e.g. Finance)", height=40)
        self.entry_new_cat.pack(fill="x", pady=(0, 5))

        self.entry_new_url = ctk.CTkEntry(add_frame, placeholder_text="Discord Webhook URL", height=40)
        self.entry_new_url.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(add_frame, text="+ ADD CHANNEL", fg_color=COLOR_SUCCESS,
                      text_color="white", hover_color="#047857",
                      command=self.add_webhook).pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(self.settings_win, text="ACTIVE CHANNELS",
                     font=("JetBrains Mono", 12, "bold"), text_color=COLOR_TEXT_SEC).pack(pady=(0, 10))

        self.scroll_frame = ctk.CTkScrollableFrame(self.settings_win, fg_color=COLOR_BG_SIDE, height=300)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.refresh_settings_list()

        self.settings_win.wait_visibility()
        self.settings_win.grab_set()

    def refresh_settings_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.webhooks:
            ctk.CTkLabel(self.scroll_frame, text="No channels configured.", text_color=COLOR_TEXT_SEC).pack(pady=20)
            return

        for name, url in self.webhooks.items():
            item = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            item.pack(fill="x", pady=5)

            ctk.CTkLabel(item, text=name, font=("Segoe UI", 13, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left", padx=5)
            ctk.CTkButton(item, text="DELETE", width=60, fg_color=COLOR_ERROR, hover_color="#B91C1C",
                          command=lambda n=name: self.delete_webhook(n)).pack(side="right")

    def add_webhook(self):
        name = self.entry_new_cat.get().strip()
        url = self.entry_new_url.get().strip()
        if not name or not url: return
        if not url.startswith("http"): return

        self.webhooks[name] = url
        self.save_config_file()
        self.refresh_settings_list()
        self.entry_new_cat.delete(0, "end")
        self.entry_new_url.delete(0, "end")
        self.update_dropdown()

    def delete_webhook(self, name):
        if name in self.webhooks:
            del self.webhooks[name]
            self.save_config_file()
            self.refresh_settings_list()
            self.update_dropdown()

    def update_dropdown(self):
        new_values = list(self.webhooks.keys()) if self.webhooks else ["No Channels Configured"]
        self.combo_cat.configure(values=new_values)
        self.combo_cat.set(new_values[0])

    # --- UI HELPERS ---
    def _create_sidebar_label(self, text, row):
        label = ctk.CTkLabel(self.sidebar, text=text, anchor="w",
                           font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                           text_color=COLOR_TEXT_SEC)
        label.grid(row=row, column=0, padx=30, pady=(25, 8), sticky="w")

    def _create_format_btn(self, parent, text, command, col):
        btn = ctk.CTkButton(parent, text=text, width=40, height=30,
                            fg_color="transparent", hover_color=COLOR_BORDER,
                            text_color=COLOR_TEXT_MAIN, command=command)
        btn.grid(row=0, column=col, padx=2, pady=2)

    def _create_spark_entry(self, parent, placeholder, row):
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, height=50,
                             fg_color=COLOR_INPUT_BG, border_color=COLOR_BORDER,
                             text_color=COLOR_TEXT_MAIN, font=("Segoe UI", 14))
        entry.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        return entry

    # --- GUIDE WINDOW ---
    def open_guide_window(self):
        guide = ctk.CTkToplevel(self)
        guide.title("OutThink // Formatting Manual")
        guide.geometry("500x500")
        guide.configure(fg_color=COLOR_BG_MAIN)
        guide.resizable(False, False)
        guide.attributes("-topmost", True)

        ctk.CTkLabel(guide, text="FORMATTING PROTOCOLS", font=("Segoe UI", 18, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=20)

        guide_text = """
        Use the toolbar or standard Markdown to style your notes.
        The system will automatically convert these to Discord Embeds.

        [ B ] Bold (**text**) -> Highlights key concepts.
        [ I ] Italic (*text*) -> For emphasis or sub-ideas.
        [ " ] Quote (> text)  -> Creates a block quote bar.
        [ • ] List (- text)   -> Good for bullet points.
        [ H1] Header (# text) -> Creates a large section title.

        --- PRO TIP ---
        "Quick Spark" mode ignores this formatting and forces a
        clean 3-point structure ideal for rapid review.
        """
        lbl = ctk.CTkLabel(guide, text=guide_text, font=("JetBrains Mono", 13), text_color=COLOR_TEXT_MAIN, justify="left")
        lbl.pack(padx=20, pady=10)

        ctk.CTkButton(guide, text="ACKNOWLEDGED", fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
                      text_color="#fff", command=guide.destroy).pack(pady=20)

        guide.wait_visibility()
        guide.grab_set()

    # --- FORMATTING LOGIC ---
    def _insert_tag(self, start_char, end_char=""):
        try:
            sel_start = self.textbox.index("sel.first")
            sel_end = self.textbox.index("sel.last")
            selected_text = self.textbox.get(sel_start, sel_end)
            self.textbox.delete(sel_start, sel_end)
            self.textbox.insert(sel_start, f"{start_char}{selected_text}{end_char}")
        except:
            self.textbox.insert("insert", f"{start_char}{end_char}")

    def fmt_bold(self): self._insert_tag("**", "**")
    def fmt_italic(self): self._insert_tag("*", "*")
    def fmt_quote(self): self._insert_tag("> ")
    def fmt_list(self): self._insert_tag("- ")
    def fmt_h1(self): self._insert_tag("# ")

    # --- EVENT HANDLERS ---
    def on_focus_in(self, event):
        if self.textbox.get("0.0", "end").strip() == DEFAULT_PLACEHOLDER:
            self.textbox.delete("0.0", "end")
            self.textbox.configure(text_color=COLOR_TEXT_MAIN)

    def on_focus_out(self, event):
        if not self.textbox.get("0.0", "end").strip():
            self.textbox.insert("0.0", DEFAULT_PLACEHOLDER)
            self.textbox.configure(text_color=COLOR_TEXT_SEC)

    def update_char_count(self, event):
        text = self.textbox.get("0.0", "end").strip()
        text_len = 0 if text == DEFAULT_PLACEHOLDER else len(text)
        self.char_counter.configure(text=f"{text_len} chars")

    def start_processing(self):
        threading.Thread(target=self.send_data).start()

    def smart_split(self, text, limit=3800):
        chunks = []
        while len(text) > limit:
            split_idx = text.rfind(' ', 0, limit)
            if split_idx == -1: split_idx = limit
            chunks.append(text[:split_idx])
            text = text[split_idx:].strip()
        chunks.append(text)
        return chunks

    def calculate_read_time(self, text):
        words = len(text.split())
        minutes = math.ceil(words / 200)
        return f"{minutes} min read"

    def send_data(self):
        if not self.webhooks:
             self.update_button_status("⚠️ CONFIG CHANNELS FIRST", "#D97706", True)
             return

        category = self.combo_cat.get()
        book_title = self.entry_book.get()
        book_author = self.entry_author.get()
        generate_audio = self.audio_var.get()
        current_tab = self.tab_view.get()

        webhook_url = self.webhooks.get(category)

        embed_color = CAT_COLORS.get(category, 0x8C8678)

        if not webhook_url:
            self.update_button_status("⚠️ CONFIG ERROR", "#D97706", True)
            return

        self.update_button_status("UPLOADING... 🚀", "#8C8678")

        # --- MODE 1: DEEP DIVE ---
        if current_tab == "Deep Dive":
            content = self.textbox.get("0.0", "end").strip()
            if len(content) < 5:
                self.update_button_status("⚠️ EMPTY DATA", "#D97706", True)
                return

            read_time = self.calculate_read_time(content)
            text_chunks = self.smart_split(content)

            for i, chunk in enumerate(text_chunks):
                main_title = book_title if i == 0 else f"{book_title} (Part {i+1})"

                embed = {
                    "title": main_title,
                    "description": chunk,
                    "color": embed_color,
                    "timestamp": datetime.now().isoformat(),
                    "author": {
                        "name": book_author if book_author else "Unknown Author"
                    },
                    "footer": {
                        "text": f"OutThink • {read_time} • {category}",
                    }
                }

                requests.post(webhook_url, json={"embeds": [embed]})

            audio_content = content

        # --- MODE 2: QUICK SPARK ---
        else:
            s1 = self.spark_1.get()
            s2 = self.spark_2.get()
            s3 = self.spark_3.get()
            if not s1 or not s2 or not s3:
                self.update_button_status("⚠️ FILL DATA", "#D97706", True)
                return

            embed = {
                "title": book_title,
                "description": "──────────────────────────────",
                "color": embed_color,
                "author": {
                    "name": book_author if book_author else "OutThink Spark"
                },
                "fields": [
                    {"name": "💎 The Concept", "value": f"> {s1}", "inline": False},
                    {"name": "⚙️ The Mechanism", "value": f"{s2}", "inline": False},
                    {"name": "🚀 The Outcome", "value": f"```diff\n+ {s3}\n```", "inline": False}
                ],
                "footer": {"text": f"OutThink • Quick Spark • {category}"},
                "timestamp": datetime.now().isoformat()
            }

            requests.post(webhook_url, json={"embeds": [embed]})

            audio_content = f"Spark. {book_title}. 1: {s1}. 2: {s2}. 3: {s3}."

        # --- AUDIO ---
        if generate_audio:
            self.update_button_status("SYNTHESIZING... 🎧", "#8C8678")
            try:
                try: detected_lang = detect(audio_content)
                except: detected_lang = 'en'

                clean_text = audio_content.replace("*", "").replace("#", "").replace(">", "")
                intro_text = "OutThink Audio."

                filename = "cache_audio.mp3"
                tts = gTTS(text=f"{intro_text} {clean_text}", lang=detected_lang)
                tts.save(filename)
                with open(filename, 'rb') as f:
                    requests.post(webhook_url, files={'file': (filename, f)})
                if os.path.exists(filename): os.remove(filename)
            except: pass

        self.update_button_status("✅ DEPLOYED", "#059669", True)
        self._reset_ui()

    def update_button_status(self, text, fg_color, temporary=False):
        self.btn_send.configure(text=text, fg_color=fg_color)
        if temporary:
             self.btn_send.configure(state="disabled")
             self.after(3000, lambda: self.btn_send.configure(text="EXECUTE DEPLOYMENT", fg_color=COLOR_ACCENT, state="normal"))

    def _reset_ui(self):
        self.after(2000, lambda: self.textbox.delete("0.0", "end"))
        self.after(2000, lambda: self.textbox.insert("0.0", DEFAULT_PLACEHOLDER))
        self.after(2000, lambda: self.textbox.configure(text_color=COLOR_TEXT_SEC))
        self.after(2000, lambda: self.spark_1.delete(0, "end"))
        self.after(2000, lambda: self.spark_2.delete(0, "end"))
        self.after(2000, lambda: self.spark_3.delete(0, "end"))
        self.after(2000, lambda: self.entry_book.delete(0, "end"))
        self.after(2000, lambda: self.entry_author.delete(0, "end"))

if __name__ == "__main__":
    app = OutThinkApp()
    app.mainloop()
