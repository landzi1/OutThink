import customtkinter as ctk
import requests
import webbrowser
import os
import threading
import sys
import math
import json
import asyncio
import edge_tts
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw, ImageOps
from notion_client import Client
from youtube_transcript_api import YouTubeTranscriptApi
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
DEFAULT_AI_PLACEHOLDER = "Intelligence Augmentation: Paste raw text to refine..."

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Fallback for dev / onedir
        base_path = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(base_path, relative_path)

    # Fallback: Check if file exists, if not, try CWD or AppDir (Critical for AppImage)
    if not os.path.exists(path):
        # 1. Try CWD (Current Working Directory)
        cwd_path = os.path.join(os.getcwd(), relative_path)
        if os.path.exists(cwd_path):
            return cwd_path

        # 2. Try APPDIR (AppImage Mount Point)
        if "APPDIR" in os.environ:
            app_path = os.path.join(os.environ["APPDIR"], relative_path)
            if os.path.exists(app_path):
                return app_path

    return path

class OutThinkApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        try:
            self.wm_class("OutThink", "OutThink")
        except:
            pass

        # 0. Load Configuration & DB
        self.webhooks_data = self.load_config()
        self.webhooks = self.webhooks_data.get("webhooks", {})
        self.init_db()

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
            # Alert the user if logo fails (Critical for debugging)
            try:
                messagebox.showwarning("Resource Error", f"Could not load logo.png:\n{e}\n\nSearch path: {img_path}")
            except: pass

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

        # Controls Container (Channels + Settings)
        self.ctrl_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.ctrl_frame.grid(row=4, column=0, padx=30, pady=(0, 20), sticky="ew")
        self.ctrl_frame.grid_columnconfigure(0, weight=1)

        # Channels Button
        self.btn_channels = ctk.CTkButton(self.ctrl_frame, text="Manage Channels",
                                          fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
                                          height=40, font=ctk.CTkFont(size=12, weight="bold"),
                                          command=self.open_channels_window)
        self.btn_channels.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Global Settings Button
        self.btn_settings = ctk.CTkButton(self.ctrl_frame, text="⚙️", width=40,
                                          fg_color=COLOR_INPUT_BG, hover_color=COLOR_BORDER,
                                          text_color=COLOR_TEXT_MAIN, border_width=1, border_color=COLOR_BORDER,
                                          height=40, font=ctk.CTkFont(size=16),
                                          command=self.open_global_settings)
        self.btn_settings.grid(row=0, column=1, sticky="e")

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
        self.main_area.grid_rowconfigure(2, weight=1) # Content expands

        # 1. NAVIGATION BAR (Top Controller)
        self.nav_bar = ctk.CTkSegmentedButton(self.main_area,
                                              values=["Deep Dive", "Quick Spark", "AI Assistant", "Archive"],
                                              command=self.switch_tab,
                                              font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                                              fg_color=COLOR_BG_SIDE,  # Background of the bar itself
                                              selected_color=COLOR_ACCENT,
                                              selected_hover_color=COLOR_ACCENT_HOVER,
                                              unselected_color=COLOR_BG_SIDE, # Seamless unselected buttons
                                              unselected_hover_color=COLOR_BORDER, # Subtle hover
                                              text_color=COLOR_TEXT_MAIN,
                                              corner_radius=8, height=40, border_width=0)
        self.nav_bar.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.nav_bar.set("Deep Dive")

        # 2. METADATA (Title & Author)
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

        # 3. CONTENT AREA (Hidden Tabs)
        self.tab_view = ctk.CTkTabview(self.main_area, fg_color="transparent",
                                       height=500, # Initial height
                                       command=None)
        
        self.tab_view.grid(row=2, column=0, sticky="nsew")

        self.tab_view.add("Deep Dive")
        self.tab_view.add("Quick Spark")
        self.tab_view.add("AI Assistant")
        self.tab_view.add("Archive")
        
        # HIDE DUPLICATE MENU (Must be called AFTER adding tabs)
        self.tab_view._segmented_button.grid_remove()

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

        # --- TAB 3: AI ASSISTANT (Chatbot) ---
        self.tab_view.tab("AI Assistant").grid_columnconfigure(0, weight=1)
        self.tab_view.tab("AI Assistant").grid_rowconfigure(0, weight=1)

        # Chat History
        self.chat_scroll = ctk.CTkScrollableFrame(self.tab_view.tab("AI Assistant"), fg_color=COLOR_BG_SIDE)
        self.chat_scroll.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        # Initial Bot Message
        self.add_chat_bubble("Hello! I'm your Editor-in-Chief.\nPaste a YouTube link or an article, and I'll distill it for you.", False)

        # Chat Controls
        self.chat_ctrl = ctk.CTkFrame(self.tab_view.tab("AI Assistant"), fg_color="transparent", height=50)
        self.chat_ctrl.grid(row=1, column=0, sticky="ew")
        self.chat_ctrl.grid_columnconfigure(0, weight=1)

        self.chat_entry = ctk.CTkEntry(self.chat_ctrl, placeholder_text="Type instructions or paste link...", height=45,
                                     border_width=1, border_color=COLOR_BORDER, fg_color=COLOR_INPUT_BG)
        self.chat_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.chat_entry.bind("<Return>", lambda e: self.send_chat_message())

        self.btn_chat_send = ctk.CTkButton(self.chat_ctrl, text="SEND", width=80, height=45,
                                         fg_color=COLOR_TEXT_MAIN, hover_color=COLOR_TEXT_SEC,
                                         command=self.send_chat_message)
        self.btn_chat_send.grid(row=0, column=1)

        # Suggestion Chips
        self.chips_frame = ctk.CTkFrame(self.tab_view.tab("AI Assistant"), fg_color="transparent")
        self.chips_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        chips = ["📺 Summarize YouTube", "📚 Book Deep Dive", "⚡ Quick Spark"]
        for i, chip in enumerate(chips):
            ctk.CTkButton(self.chips_frame, text=chip, height=30,
                          fg_color=COLOR_BG_SIDE, text_color=COLOR_TEXT_MAIN, hover_color=COLOR_BORDER,
                          command=lambda c=chip: self.chat_entry.insert(0, c)).pack(side="left", padx=(0, 10))

        # --- TAB 4: ARCHIVE ---
        self.tab_view.tab("Archive").grid_columnconfigure(0, weight=1)
        self.tab_view.tab("Archive").grid_rowconfigure(1, weight=1)

        self.archive_controls = ctk.CTkFrame(self.tab_view.tab("Archive"), fg_color="transparent")
        self.archive_controls.grid(row=0, column=0, sticky="ew", pady=(5, 10))
        
        ctk.CTkButton(self.archive_controls, text="🔄 REFRESH ARCHIVE", 
                      fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
                      command=self.load_archive).pack(side="left")

        self.archive_scroll = ctk.CTkScrollableFrame(self.tab_view.tab("Archive"), fg_color=COLOR_BG_SIDE)
        self.archive_scroll.grid(row=1, column=0, sticky="nsew")

        # 4. TARGET SYSTEMS (Compact Control Panel)
        self.target_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.target_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        
        # Center the checkboxes using a container
        inner_target = ctk.CTkFrame(self.target_frame, fg_color=COLOR_BG_SIDE, corner_radius=20)
        inner_target.pack(anchor="center")
        
        ctk.CTkLabel(inner_target, text="DEPLOY TO:", 
                     font=("Segoe UI", 11, "bold"), text_color=COLOR_TEXT_SEC).pack(side="left", padx=(15, 5), pady=8)

        self.chk_discord = ctk.CTkCheckBox(inner_target, text="Discord", font=("Segoe UI", 11), width=20, height=20,
                                           fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER)
        self.chk_discord.pack(side="left", padx=8)
        self.chk_discord.select()

        self.chk_notion = ctk.CTkCheckBox(inner_target, text="Notion", font=("Segoe UI", 11), width=20, height=20,
                                          fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER)
        self.chk_notion.pack(side="left", padx=8)
        self.chk_notion.select()

        self.chk_local = ctk.CTkCheckBox(inner_target, text="Backup", font=("Segoe UI", 11), width=20, height=20,
                                         fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER)
        self.chk_local.pack(side="left", padx=(8, 15))

        # Bottom Frame (Char Counter)
        self.bottom_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.bottom_frame.grid(row=4, column=0, sticky="ew", pady=(0, 0))
        
        self.char_counter = ctk.CTkLabel(self.bottom_frame, text="0 chars", text_color=COLOR_TEXT_SEC, font=("JetBrains Mono", 12))
        self.char_counter.pack(side="right")

        # 5. EXECUTE BUTTON
        self.btn_send = ctk.CTkButton(self.main_area, text="EXECUTE DEPLOYMENT",
                                    height=65, font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                                    fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, corner_radius=32,
                                    command=self.start_processing,
                                    text_color="#FFFFFF")
        self.btn_send.grid(row=5, column=0, sticky="ew", pady=(10,0))

        # Initial Logic
        self.textbox.insert("0.0", DEFAULT_PLACEHOLDER)
        self.textbox.configure(text_color=COLOR_TEXT_SEC)
        self.textbox.bind("<FocusIn>", self.on_focus_in)
        self.textbox.bind("<FocusOut>", self.on_focus_out)
        self.textbox.bind("<KeyRelease>", self.update_char_count)

    def add_chat_bubble(self, text, is_user):
        bubble = ctk.CTkFrame(self.chat_scroll, fg_color=COLOR_ACCENT if is_user else COLOR_INPUT_BG,
                              corner_radius=16)
        bubble.pack(anchor="e" if is_user else "w", pady=5, padx=10, fill="x" if len(text) > 50 else "none")
        
        lbl = ctk.CTkLabel(bubble, text=text, text_color="#FFFFFF" if is_user else COLOR_TEXT_MAIN,
                           font=("Segoe UI", 13), justify="left", wraplength=500)
        lbl.pack(padx=15, pady=10)
        
        # Auto-scroll
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def send_chat_message(self):
        msg = self.chat_entry.get().strip()
        if not msg: return

        self.add_chat_bubble(msg, True)
        self.chat_entry.delete(0, "end")
        
        key = self.webhooks_data.get("groq_key")
        if not key:
            self.add_chat_bubble("⚠️ Please configure Groq API Key in settings first.", False)
            return

        # Thinking indicator
        self.btn_chat_send.configure(state="disabled", text="...")
        
        # Determine mode based on keywords
        mode = "⚡ Quick Spark" # Default
        if "Deep Dive" in msg or "Essay" in msg or "Detailed" in msg:
            mode = "🌊 Deep Dive"
        
        # Check for YouTube
        if "youtube.com" in msg or "youtu.be" in msg:
             threading.Thread(target=self._process_youtube, args=(msg, key, mode)).start()
        else:
             threading.Thread(target=self._groq_request, args=(msg, key, mode)).start()

    def load_archive(self):
        for widget in self.archive_scroll.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT id, title, author, mode, timestamp FROM notes ORDER BY timestamp DESC")
        rows = self.cursor.fetchall()

        for r in rows:
            nid, title, author, mode, ts = r
            item = ctk.CTkFrame(self.archive_scroll, fg_color=COLOR_INPUT_BG, corner_radius=8)
            item.pack(fill="x", pady=5, padx=5)

            info_text = f"{title}\nBy {author} | {mode} | {ts[:10]}"
            ctk.CTkLabel(item, text=info_text, font=("Segoe UI", 12), justify="left").pack(side="left", padx=10, pady=10)
            
            ctk.CTkButton(item, text="RESTORE", width=80, fg_color=COLOR_ACCENT, 
                          command=lambda i=nid: self.restore_note(i)).pack(side="right", padx=5)
            
            ctk.CTkButton(item, text="EXPORT", width=80, fg_color=COLOR_TEXT_MAIN,
                          command=lambda i=nid: self.manual_archive_export(i)).pack(side="right", padx=5)

    def manual_archive_export(self, note_id):
        self.cursor.execute("SELECT title, author, content, category, mode FROM notes WHERE id=?", (note_id,))
        res = self.cursor.fetchone()
        if res:
            title, author, content, category, mode = res
            self.export_to_markdown(title, author, content, category, mode)
            messagebox.showinfo("Exported", f"Note '{title}' exported to your chosen directory.")

    def restore_note(self, note_id):
        self.cursor.execute("SELECT title, author, content, mode FROM notes WHERE id=?", (note_id,))
        res = self.cursor.fetchone()
        if res:
            title, author, content, mode = res
            self.entry_book.delete(0, "end")
            self.entry_book.insert(0, title)
            self.entry_author.delete(0, "end")
            self.entry_author.insert(0, author)

            if mode == "Deep Dive":
                self.textbox.delete("0.0", "end")
                self.textbox.insert("0.0", content)
                self.textbox.configure(text_color=COLOR_TEXT_MAIN)
                self.nav_bar.set("Deep Dive")
                self.switch_tab("Deep Dive")
            else:
                # Splitting spark content (stored as 1: ...\n2: ...\n3: ...)
                parts = content.split("\n")
                self.spark_1.delete(0, "end")
                self.spark_2.delete(0, "end")
                self.spark_3.delete(0, "end")
                if len(parts) >= 1: self.spark_1.insert(0, parts[0].replace("1: ", ""))
                if len(parts) >= 2: self.spark_2.insert(0, parts[1].replace("2: ", ""))
                if len(parts) >= 3: self.spark_3.insert(0, parts[2].replace("3: ", ""))
                self.nav_bar.set("Quick Spark")
                self.switch_tab("Quick Spark")
            
            messagebox.showinfo("Restored", "Note has been loaded into the editor.")

    def _process_youtube(self, url, key, mode):
        try:
            video_id = ""
            if "youtu.be" in url:
                video_id = url.split("/")[-1].split("?")[0]
            elif "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            
            if not video_id:
                raise Exception("Could not extract Video ID")

            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([t['text'] for t in transcript])
            
            self._groq_request(full_text, key, mode)

        except Exception as e:
            self.after(0, lambda: self.add_chat_bubble(f"❌ YouTube Error: {e}", False))
            self.after(0, lambda: self.btn_chat_send.configure(state="normal", text="SEND"))

    def _groq_request(self, text, key, mode):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }

            if mode == "⚡ Quick Spark":
                prompt = f"""
                Analyze the text and distill into 3 high-impact insights.
                Respond ONLY in JSON: 'insight1', 'insight2', 'insight3', 'title', 'author'.
                Text: {text[:6000]}
                """
            else: # Deep Dive
                prompt = f"""
                Act as a book editor. Write a comprehensive summary (Deep Dive) in Markdown.
                Respond ONLY in JSON: 'content', 'title', 'author'.
                Text: {text[:6000]}
                """
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            res_data = response.json()
            content = json.loads(res_data['choices'][0]['message']['content'])

            self.after(0, lambda: self._apply_ai_results(content, mode))
        except Exception as e:
            self.after(0, lambda: self.add_chat_bubble(f"❌ AI Error: {e}", False))
            self.after(0, lambda: self.btn_chat_send.configure(state="normal", text="SEND"))

    def _apply_ai_results(self, data, mode):
        self.entry_book.delete(0, "end")
        self.entry_book.insert(0, data.get("title", ""))
        self.entry_author.delete(0, "end")
        self.entry_author.insert(0, data.get("author", "AI Refined"))
        
        if mode == "⚡ Quick Spark":
            self.spark_1.delete(0, "end")
            self.spark_1.insert(0, data.get("insight1", ""))
            self.spark_2.delete(0, "end")
            self.spark_2.insert(0, data.get("insight2", ""))
            self.spark_3.delete(0, "end")
            self.spark_3.insert(0, data.get("insight3", ""))
            
            self.add_chat_bubble(f"✅ Analysis Complete! I've drafted 3 key insights for '{data.get('title')}'.\nSwitching to Quick Spark view...", False)
            self.after(1500, lambda: self.nav_bar.set("Quick Spark"))
            self.after(1500, lambda: self.switch_tab("Quick Spark"))
            
        else: # Deep Dive
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", data.get("content", ""))
            self.textbox.configure(text_color=COLOR_TEXT_MAIN)
            
            self.add_chat_bubble(f"✅ Deep Dive Generated! I've written a full essay for '{data.get('title')}'.\nSwitching to Editor...", False)
            self.after(1500, lambda: self.nav_bar.set("Deep Dive"))
            self.after(1500, lambda: self.switch_tab("Deep Dive"))

        self.btn_chat_send.configure(state="normal", text="SEND")

    def init_db(self):
        self.conn = sqlite3.connect("outthink.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                content TEXT,
                category TEXT,
                mode TEXT,
                timestamp DATETIME
            )
        """)
        self.conn.commit()

    def switch_tab(self, value):
        self.tab_view.set(value)

    # --- CONFIG MANAGER ---
    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            default_data = {"webhooks": {}, "groq_key": "", "export_path": "", "notion_key": "", "notion_db": ""}
            with open(CONFIG_FILE, "w") as f:
                json.dump(default_data, f)
            return default_data

        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                # Migration
                if "webhooks" not in data: data = {"webhooks": data}
                for key in ["groq_key", "export_path", "notion_key", "notion_db"]:
                    if key not in data: data[key] = ""
                return data
        except:
            return {"webhooks": {}, "groq_key": "", "export_path": "", "notion_key": "", "notion_db": ""}

    def save_config_file(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.webhooks_data, f, indent=4)
        except Exception as e:
            print(f"Config save error: {e}")

    # --- SETTINGS WINDOWS ---
    def open_global_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Global Settings")
        win.geometry("500x650")
        win.configure(fg_color=COLOR_BG_MAIN)
        win.attributes("-topmost", True)

        # 1. AI
        ai_header = ctk.CTkFrame(win, fg_color="transparent")
        ai_header.pack(fill="x", padx=20, pady=(20, 5))
        ctk.CTkLabel(ai_header, text="AI CONFIGURATION (GROQ)", font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")
        ctk.CTkButton(ai_header, text="?", width=25, height=25, fg_color="transparent", 
                      border_width=1, border_color=COLOR_BORDER, text_color=COLOR_ACCENT,
                      command=self.open_groq_guide).pack(side="right")

        ai_frame = ctk.CTkFrame(win, fg_color=COLOR_BG_SIDE)
        ai_frame.pack(fill="x", padx=20)
        ctk.CTkLabel(ai_frame, text="Groq API Key:", font=("Segoe UI", 12)).pack(anchor="w", padx=10)
        self.entry_groq_key = ctk.CTkEntry(ai_frame, placeholder_text="gsk_...", show="*")
        self.entry_groq_key.insert(0, self.webhooks_data.get("groq_key", ""))
        self.entry_groq_key.pack(fill="x", padx=10, pady=(0, 10))

        # 2. NOTION
        notion_header = ctk.CTkFrame(win, fg_color="transparent")
        notion_header.pack(fill="x", padx=20, pady=(20, 5))
        
        ctk.CTkLabel(notion_header, text="NOTION INTEGRATION",
                     font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(side="left")
        
        ctk.CTkButton(notion_header, text="?", width=25, height=25, fg_color="transparent", 
                      border_width=1, border_color=COLOR_BORDER, text_color=COLOR_ACCENT,
                      command=self.open_notion_guide).pack(side="right")

        notion_frame = ctk.CTkFrame(win, fg_color=COLOR_BG_SIDE)
        notion_frame.pack(fill="x", padx=20)
        
        ctk.CTkLabel(notion_frame, text="Notion Secret Key:", font=("Segoe UI", 12)).pack(anchor="w", padx=10)
        self.entry_notion_key = ctk.CTkEntry(notion_frame, placeholder_text="secret_...", show="*")
        self.entry_notion_key.insert(0, self.webhooks_data.get("notion_key", ""))
        self.entry_notion_key.pack(fill="x", padx=10, pady=(0, 5))

        ctk.CTkLabel(notion_frame, text="Database ID:", font=("Segoe UI", 12)).pack(anchor="w", padx=10)
        self.entry_notion_db = ctk.CTkEntry(notion_frame, placeholder_text="Ex. 384b2...")
        self.entry_notion_db.insert(0, self.webhooks_data.get("notion_db", ""))
        self.entry_notion_db.pack(fill="x", padx=10, pady=(0, 10))

        # 3. EXPORT
        ctk.CTkLabel(win, text="LOCAL BACKUP",
                     font=("Segoe UI", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(20, 5))
        export_frame = ctk.CTkFrame(win, fg_color=COLOR_BG_SIDE)
        export_frame.pack(fill="x", padx=20)
        path_inner = ctk.CTkFrame(export_frame, fg_color="transparent")
        path_inner.pack(fill="x", padx=10, pady=10)
        self.entry_export_path = ctk.CTkEntry(path_inner)
        self.entry_export_path.insert(0, self.webhooks_data.get("export_path", ""))
        self.entry_export_path.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(path_inner, text="📁", width=40, fg_color=COLOR_ACCENT, command=self.browse_export_path).pack(side="right")

        ctk.CTkButton(win, text="SAVE GLOBAL SETTINGS", height=45, font=("Segoe UI", 13, "bold"),
                      fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER,
                      command=lambda: self.save_global_settings(win)).pack(fill="x", padx=20, pady=30)

    def open_groq_guide(self):
        guide = ctk.CTkToplevel(self)
        guide.title("Groq API Setup")
        guide.geometry("500x400")
        guide.configure(fg_color=COLOR_BG_MAIN)
        guide.attributes("-topmost", True)

        ctk.CTkLabel(guide, text="GETTING YOUR GROQ API KEY", 
                     font=("Segoe UI", 16, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=20)

        step_text = """
        Groq provides extremely fast AI inference (Llama 3).
        It is currently offering a generous FREE tier.

        1. Go to: https://console.groq.com/keys
        2. Create an account (Google/GitHub).
        3. Click 'Create API Key'.
        4. Name it "OutThink".
        5. Copy the key starting with 'gsk_'.
        6. Paste it into the settings window.
        """
        
        textbox = ctk.CTkTextbox(guide, font=("JetBrains Mono", 12), text_color=COLOR_TEXT_MAIN, fg_color=COLOR_BG_SIDE, wrap="word")
        textbox.pack(fill="both", expand=True, padx=20, pady=10)
        textbox.insert("0.0", step_text)
        textbox.configure(state="disabled")
        ctk.CTkButton(guide, text="GOT IT", fg_color=COLOR_ACCENT, command=guide.destroy).pack(pady=20)

    def open_notion_guide(self):
        guide = ctk.CTkToplevel(self)
        guide.title("Notion Setup Guide")
        guide.geometry("600x700")
        guide.configure(fg_color=COLOR_BG_MAIN)
        guide.attributes("-topmost", True)

        ctk.CTkLabel(guide, text="CONNECTING OUTTHINK TO NOTION", 
                     font=("Segoe UI", 16, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=20)

        step_text = """
        STEP 1: CREATE INTEGRATION
        1. Go to: https://www.notion.so/my-integrations
        2. Click 'New Integration'. Name it "OutThink".
        3. Select 'Read content', 'Update content', 'Insert content'.
        4. Submit and COPY the "Internal Integration Secret".
        5. Paste it into the "Notion Secret Key" field here.

        STEP 2: PREPARE DATABASE
        1. Create a new Full Page Database in Notion.
        2. Add these exact properties (columns):
           - Name (Title)
           - Author (Text)
           - Category (Select)
           - Type (Select)
           - Date (Date)
        
        STEP 3: CONNECT & GET ID
        1. Open your new Database page.
        2. Click the '...' menu (top right) -> Connections.
        3. Search for "OutThink" and confirm access.
        4. Look at the database URL:
           https://www.notion.so/user/384b2...123?v=...
           
           The ID is the long part between the last '/' and '?'.
           Copy ONLY that ID (e.g. 384b2...123).
        5. Paste it into "Database ID" field.
        """
        
        textbox = ctk.CTkTextbox(guide, font=("JetBrains Mono", 12), text_color=COLOR_TEXT_MAIN, fg_color=COLOR_BG_SIDE, wrap="word")
        textbox.pack(fill="both", expand=True, padx=20, pady=10)
        textbox.insert("0.0", step_text)
        textbox.configure(state="disabled")

        ctk.CTkButton(guide, text="GOT IT", fg_color=COLOR_ACCENT, command=guide.destroy).pack(pady=20)

    def browse_export_path(self):
        from tkinter import filedialog
        path = filedialog.askdirectory()
        if path:
            self.entry_export_path.delete(0, "end")
            self.entry_export_path.insert(0, path)

    def save_global_settings(self, win):
        self.webhooks_data["groq_key"] = self.entry_groq_key.get().strip()
        self.webhooks_data["notion_key"] = self.entry_notion_key.get().strip()
        self.webhooks_data["notion_db"] = self.entry_notion_db.get().strip()
        self.webhooks_data["export_path"] = self.entry_export_path.get().strip()
        self.save_config_file()
        messagebox.showinfo("Success", "Settings saved!")
        win.destroy()

    def open_channels_window(self):
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

    def save_groq_key(self, window=None):
        key = self.entry_groq_key.get().strip()
        self.webhooks_data["groq_key"] = key
        self.save_config_file()
        messagebox.showinfo("Success", "API Key saved locally!")
        if window: window.destroy()


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
                            fg_color=COLOR_INPUT_BG, hover_color=COLOR_BG_SIDE,
                            border_width=1, border_color=COLOR_BORDER,
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
        current_text = self.textbox.get("0.0", "end").strip()
        if current_text == DEFAULT_PLACEHOLDER:
            self.textbox.delete("0.0", "end")
            self.textbox.configure(text_color=COLOR_TEXT_MAIN)

    def on_focus_out(self, event):
        if not self.textbox.get("0.0", "end").strip():
            self.textbox.insert("0.0", DEFAULT_PLACEHOLDER)
            self.textbox.configure(text_color=COLOR_TEXT_SEC)

    def on_ai_focus_in(self, event):
        if self.ai_input.get("0.0", "end").strip() == DEFAULT_AI_PLACEHOLDER:
            self.ai_input.delete("0.0", "end")
            self.ai_input.configure(text_color=COLOR_TEXT_MAIN)

    def on_ai_focus_out(self, event):
        if not self.ai_input.get("0.0", "end").strip():
            self.ai_input.insert("0.0", DEFAULT_AI_PLACEHOLDER)
            self.ai_input.configure(text_color=COLOR_TEXT_SEC)

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

    def export_to_markdown(self, title, author, content, category, mode):
        path = self.webhooks_data.get("export_path")
        if not path or not os.path.exists(path):
            return

        # Clean filename
        clean_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).rstrip()
        filename = f"{clean_title}.md"
        full_path = os.path.join(path, filename)

        yaml_meta = f"""---
title: "{title}"
author: "{author}"
category: "{category}"
mode: "{mode}"
date: {datetime.now().strftime('%Y-%m-%d')}
source: OutThink
---

"""
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(yaml_meta)
                f.write(content)
        except Exception as e:
            print(f"Export failed: {e}")

    def send_to_notion(self, title, author, content, category, mode):
        token = self.webhooks_data.get("notion_key")
        db_id = self.webhooks_data.get("notion_db")
        if not token or not db_id: return

        try:
            notion = Client(auth=token)
            
            # Basic Block for content (truncated to avoid limits, in reality you'd split)
            # Notion API block limit is 2000 chars per block
            blocks = []
            chunks = [content[i:i+2000] for i in range(0, len(content), 2000)]
            for chunk in chunks:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}]
                    }
                })

            notion.pages.create(
                parent={"database_id": db_id},
                properties={
                    "Name": {"title": [{"text": {"content": title}}]},
                    "Author": {"rich_text": [{"text": {"content": author}}]},
                    "Category": {"select": {"name": category}},
                    "Type": {"select": {"name": mode}},
                    "Date": {"date": {"start": datetime.now().isoformat()[:10]}}
                },
                children=blocks
            )
            print("Notion sync success.")
        except Exception as e:
            print(f"Notion sync failed: {e}")

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

        # Get Target States
        use_discord = self.chk_discord.get()
        use_notion = self.chk_notion.get()
        use_local = self.chk_local.get()

        # --- MODE 1: DEEP DIVE ---
        if current_tab == "Deep Dive":
            content = self.textbox.get("0.0", "end").strip()
            if len(content) < 5:
                self.update_button_status("⚠️ EMPTY DATA", "#D97706", True)
                return

            read_time = self.calculate_read_time(content)
            
            # Discord Logic
            if use_discord and webhook_url:
                text_chunks = self.smart_split(content)
                for i, chunk in enumerate(text_chunks):
                    main_title = book_title if i == 0 else f"{book_title} (Part {i+1})"
                    embed = {
                        "title": main_title,
                        "description": chunk,
                        "color": embed_color,
                        "timestamp": datetime.now().isoformat(),
                        "author": {"name": book_author if book_author else "Unknown Author"},
                        "footer": {"text": f"OutThink • {read_time} • {category}"}
                    }
                    requests.post(webhook_url, json={"embeds": [embed]})

            # Save to local DB (Deep Dive) - ALWAYS SAVE TO DB for History
            self.cursor.execute("INSERT INTO notes (title, author, content, category, mode, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                                (book_title, book_author, content, category, "Deep Dive", datetime.now().isoformat()))
            self.conn.commit()
            
            if use_local:
                self.export_to_markdown(book_title, book_author, content, category, "Deep Dive")

            if use_notion:
                self.send_to_notion(book_title, book_author, content, category, "Deep Dive")

            audio_content = content

        # --- MODE 2: QUICK SPARK ---
        else:
            s1 = self.spark_1.get()
            s2 = self.spark_2.get()
            s3 = self.spark_3.get()
            if not s1 or not s2 or not s3:
                self.update_button_status("⚠️ FILL DATA", "#D97706", True)
                return

            # Discord Logic
            if use_discord and webhook_url:
                embed = {
                    "title": book_title,
                    "description": "──────────────────────────────",
                    "color": embed_color,
                    "author": {"name": book_author if book_author else "OutThink Spark"},
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
            
            # Save to local DB
            self.cursor.execute("INSERT INTO notes (title, author, content, category, mode, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                                (book_title, book_author, f"1: {s1}\n2: {s2}\n3: {s3}", category, "Quick Spark", datetime.now().isoformat()))
            self.conn.commit()
            
            if use_local:
                self.export_to_markdown(book_title, book_author, f"# {book_title}\n\n## Insights\n- {s1}\n- {s2}\n- {s3}", category, "Quick Spark")
            
            if use_notion:
                self.send_to_notion(book_title, book_author, f"1. {s1}\n2. {s2}\n3. {s3}", category, "Quick Spark")

        # --- AUDIO ---
        if generate_audio and use_discord and webhook_url:
            self.update_button_status("SYNTHESIZING (NEURAL)... 🎧", "#8C8678")
            try:
                clean_text = audio_content.replace("*", "").replace("#", "").replace(">", "")
                intro_text = "OutThink Audio."
                final_text = f"{intro_text} {clean_text}"

                filename = "cache_audio.mp3"
                
                # Auto-detect language
                try:
                    lang = detect(clean_text)
                except:
                    lang = "en"
                
                # Voice mapping
                if lang == "pl":
                    VOICE = "pl-PL-MarekNeural"
                else:
                    VOICE = "en-US-ChristopherNeural"

                # Async wrapper dla edge-tts
                async def _gen_audio():
                    communicate = edge_tts.Communicate(final_text, VOICE)
                    await communicate.save(filename)

                asyncio.run(_gen_audio())

                with open(filename, 'rb') as f:
                    requests.post(webhook_url, files={'file': (filename, f)})
                
                if os.path.exists(filename): os.remove(filename)
            except Exception as e:
                print(f"Audio Error: {e}")
                pass

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
