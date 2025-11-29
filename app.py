import re
import threading
import subprocess
from tkinter import *
from tkinter import filedialog, messagebox
import onnxruntime as rt
import numpy as np
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from config.config import Config
from utils.logger import logger


class App:
    def __init__(self):
        self.root = Tk()
        
        self.credential_file_path = StringVar()
        self.target_comment_id = StringVar()
        self.video_url = StringVar()
        self.comments = []

        self.enable_ban_author = BooleanVar(value=False)
        self.enable_ai = BooleanVar(value=False)

        self.sess = None
        self.input_name = None

        self.youtube = None

        # self.load_model()
        self.init_window()
        self.build_ui()
        
        self.root.after(100, lambda: (
            self.root.attributes('-topmost', True),
            self.root.attributes('-topmost', False)
        ))
        
        self.root.mainloop()


    def init_window(self):
        width, height = 400, 480
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - width - 1300) // 2      # Future change
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.iconbitmap(Config.LOGO_PATH)
        self.root.title("YouTube Comments Remover")

    def build_ui(self):
        self.menu_ui()
        self.auth_ui()
        self.comments_ui()
        self.delete_ui()
        self.footer_ui()


    def menu_ui(self):
        menu = Menu(self.root)
        self.root.config(menu=menu)

        filemenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Logs", command=self.show_logs)
        filemenu.add_command(label="Exit", command=self.root.quit)

        helpmenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About", command=self.about)

    def about(self):
        messagebox.showinfo("About", "YouTube comments remover. Provided 2 options: Manual removal and Use AI (Logistic Regression) removal.")

    def show_logs(self):
        log_root = Toplevel(self.root)

        width, height = 600, 400
        log_root.geometry(f"{width}x{height}")
        log_root.resizable(False, False)
        log_root.title("Log(s)")

        frame = Frame(log_root)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)

        text = Text(frame, wrap="word", state="disabled")
        text.grid(row=0, column=0, sticky="nsew")

        y_scroll = Scrollbar(frame, orient="vertical", command=text.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        text.config(yscrollcommand=y_scroll.set)
        
        self.load_logs(text)


    def load_logs(self, text):
        try:
            with open(Config.LOG_PATH, "r", encoding="utf-8") as f:
                logs = f.read()
                text.config(state="normal")
                if logs:
                    text.insert("1.0", logs)
                else:
                    text.insert("1.0", "No logs found.")
                text.config(state="disabled")
        except FileNotFoundError:
            messagebox.showinfo("Error", "Can't load log file.")

    
    def choose_credential_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file_path:
            self.credential_file_path.set(file_path)

    def auth_thread(self):
        thread = threading.Thread(target=self.authenticate)
        thread.daemon = True
        thread.start()

    def authenticate(self):
        if not self.credential_file_path.get():
            messagebox.showerror("Error", "Upload credential file")
            return
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.credential_file_path.get(), Config.SCOPES)
            creds = flow.run_local_server(port=0)
            self.youtube = build("youtube", "v3", credentials=creds)
            self.root.after(0, lambda: messagebox.showinfo("Success", "Authentication complete"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def auth_ui(self):
        frame = LabelFrame(self.root, text="Authentication")
        frame.pack(fill="x", padx=10, pady=5)
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=0)

        entry = Entry(frame, textvariable=self.credential_file_path, width=50)
        entry.grid(row=0, column=0, padx=5, pady=5)
        entry.insert(0, "*client_secret.json")

        Button(frame, text="Browse", command=self.choose_credential_file, width=8).grid(row=0, column=1, padx=5, pady=5)
        Button(frame, text="Auth", command=self.auth_thread, width=8).grid(row=0, column=2, padx=5, pady=5)


    def comments_thread(self, video_id, finish_callback):
        thread = threading.Thread(target=lambda: self.load_comments(video_id, finish_callback))
        thread.daemon = True
        thread.start()

    def load_comments(self, video_id, finish_callback):
        try:
            self.fetch_comments(video_id)
            self.root.after(0, lambda: finish_callback(self.comments))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def fetch_comments(self, video_id):
        comments = []
        next_page = None

        while True:
            response = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page
            ).execute()

            for item in response.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "id": item["id"],
                    "author": snippet["authorDisplayName"],
                    "text": snippet["textOriginal"]
                })

            next_page = response.get("nextPageToken")
            if not next_page:
                break

        self.comments = comments

    def comments_ui(self):
        frame = LabelFrame(self.root, text="Load Comment(s)")
        frame.pack(fill="x", padx=10, pady=5)
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=0)

        entry = Entry(frame, textvariable=self.video_url, width=50)
        entry.grid(row=0, column=0, padx=5, pady=5)
        entry.insert(0, "*www.youtube.com")

        def start():
            video_url = self.video_url.get()
            match = re.search(Config.VIDEO_ID_PATTERN, video_url)
            if not match:
                messagebox.showerror("Error", "Invalid URL")
                return
            
            video_id = match.group(1)
            self.comments_thread(video_id, self.render_comments)

        Button(frame, text="Load", command=start, width=8).grid(row=0, column=1, padx=5, pady=5)

        list_frame = Frame(frame)
        list_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=0)

        self.text = Text(list_frame, width=43, height=12, wrap="word")
        self.text.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0,7))

        y_scroll = Scrollbar(list_frame, orient="vertical", command=self.text.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=y_scroll.set)

    def render_comments(self, comments):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        for c in comments:
            self.text.insert("end", f"ID:     {c['id']}\nAuthor: {c['author']}\nText:   {c['text']}\n{'-'*44}\n")
        self.text.config(state="disabled")

        messagebox.showinfo("Success", f"Loaded {len(comments)} comments")


    def load_model(self):
        try:
            self.sess = rt.InferenceSession(Config.MODEL_PATH, providers=["CPUExecutionProvider"])
            self.input_name = self.sess.get_inputs()[0].name    # output: 'input'

            logger("Logistic Regression Model loaded.")

        except Exception as e:
            messagebox.showerror(title="Error", message=f"Error loading model: {str(e)}")

    def model_predict(self):
        texts = [c["text"] for c in self.comments]
        text_input = np.array(texts, dtype=object).reshape(-1, 1)

        predictions, _ = self.sess.run(None, {self.input_name: text_input})
        flagged_comment_id = [self.comments[i]["id"] for i, pred in enumerate(predictions) if pred == 1]

        return flagged_comment_id


    def delete_comment(self, comment_id, ban_author):
        self.youtube.comments().setModerationStatus(
            id=comment_id,
            moderationStatus="rejected",
            banAuthor=ban_author
        ).execute()

    def execute_delete(self):
        try:
            if not self.enable_ai.get():
                self.delete_comment(self.target_comment_id.get(), self.enable_ban_author.get())
                messagebox.showinfo("Success", f"Deleted comment with id: {self.target_comment_id.get()}")
                return

            flagged_comment_id = self.model_predict()
            if not flagged_comment_id:
                messagebox.showinfo("Result", "No comments flagged")
                return
            
            for comment_id in flagged_comment_id:
                self.delete_comment(comment_id, self.enable_ban_author.get())

            messagebox.showinfo("Success", f"Deleted {len(flagged_comment_id)} comments")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_ui(self):
        frame = LabelFrame(self.root, text="Delete comment(s)")
        frame.pack(fill="x", padx=10, pady=(5,0))
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=0)

        entry = Entry(frame, textvariable=self.target_comment_id, width=50)
        entry.grid(row=0, column=0, padx=5, pady=5)
        entry.insert(0, "*comment_id")

        Checkbutton(frame, text="Ban author", variable=self.enable_ban_author).grid(row=1, column=0, sticky="w")
        Checkbutton(frame, text="Use AI (Logistic Regression)", variable=self.enable_ai).grid(row=2, column=0, sticky="w")

        Button(frame, text="Execute", command=self.execute_delete, width=8).grid(row=0, column=1, padx=5, pady=0)


    def ping(self):
        try:
            output = subprocess.check_output("ping -n 1 console.cloud.google.com", shell=True).decode()
            ms = output.split("time=")[1].split("ms")[0] + " ms"
        except:
            ms = "Disconnected"

        self.ping_label.config(text=ms)
        self.root.after(1000, self.ping)

    def footer_ui(self):
        frame = Frame(self.root)
        frame.pack(fill="both", expand=True)
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=1)

        Label(frame, text="@rifqiansharir2025", font=("Arial", 8), fg="gray").pack(side='left', padx=10, pady=0)

        self.ping_label = Label(frame, text="Checking...", font=("Arial", 8))
        self.ping_label.pack(side='right', padx=10, pady=0)

        self.ping()


if __name__ == "__main__":
    App()
