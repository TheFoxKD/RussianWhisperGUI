import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class TranscriptionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Transcription App")
        self.master.geometry("500x300")
        self.master.configure(bg='#f0f0f0')

        self.file_path = tk.StringVar()
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.master, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Select Audio or Video File:",
                  font=('Arial', 12)).grid(row=0, column=0, columnspan=2, pady=10, sticky='w')

        file_entry = ttk.Entry(main_frame, textvariable=self.file_path, width=50)
        file_entry.grid(row=1, column=0, padx=(0, 10), sticky='ew')

        browse_button = ttk.Button(main_frame, text="Browse", command=self.browse_file)
        browse_button.grid(row=1, column=1, sticky='e')

        confirm_button = ttk.Button(main_frame, text="Confirm", command=self.run_transcription)
        confirm_button.grid(row=2, column=0, columnspan=2, pady=20, sticky='ew')

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Apply a theme
        style = ttk.Style()
        style.theme_use('clam')

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[
            ("Audio/Video files", "*.mp3 *.mp4 *.wav *.avi *.mov")
        ])
        self.file_path.set(filename)

    def run_transcription(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file first.")
            return

        try:
            command = [
                "faster-whisper.exe",
                file_path,
                "--model", "large",
                "--language", "Russian",
                "--output_format", "text",
                "--task", "transcribe"
            ]
            subprocess.run(command, check=True)
            messagebox.showinfo("Success", "Transcription completed successfully.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Transcription failed: {e}")
        except FileNotFoundError:
            messagebox.showerror("Error", "faster-whisper.exe not found. Please ensure it's in your system PATH.")


def main():
    root = tk.Tk()
    TranscriptionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
