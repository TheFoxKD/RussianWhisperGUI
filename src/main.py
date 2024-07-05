import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
from pathlib import Path
import threading
import queue
from typing import List, Tuple
import os


class TranscriptionApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Transcription App")
        self.master.geometry("600x500")  # Увеличим высоту окна
        self.master.configure(bg='#f0f0f0')

        self.file_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.transcription_queue: queue.Queue = queue.Queue()
        self.active_transcriptions: List[threading.Thread] = []

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_file_selection_widgets(main_frame)
        self.create_output_selection_widgets(main_frame)
        self.create_transcribe_button(main_frame)
        self.create_transcription_list(main_frame)

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

        self.apply_style()

        self.master.after(100, self.check_transcription_queue)

    def create_file_selection_widgets(self, parent: ttk.Frame):
        ttk.Label(parent, text="Select Audio or Video File:", font=('Arial', 12)).grid(row=0, column=0, columnspan=2,
                                                                                       pady=(0, 10), sticky='w')

        file_entry = ttk.Entry(parent, textvariable=self.file_path, width=50)
        file_entry.grid(row=1, column=0, padx=(0, 10), sticky='ew')

        browse_button = ttk.Button(parent, text="Browse", command=self.browse_input_file)
        browse_button.grid(row=1, column=1, sticky='e')

    def create_output_selection_widgets(self, parent: ttk.Frame):
        ttk.Label(parent, text="Select Output Directory:", font=('Arial', 12)).grid(row=2, column=0, columnspan=2,
                                                                                    pady=(20, 10), sticky='w')

        output_entry = ttk.Entry(parent, textvariable=self.output_path, width=50)
        output_entry.grid(row=3, column=0, padx=(0, 10), sticky='ew')

        output_browse_button = ttk.Button(parent, text="Browse", command=self.browse_output_directory)
        output_browse_button.grid(row=3, column=1, sticky='e')

    def create_transcribe_button(self, parent: ttk.Frame):
        transcribe_button = ttk.Button(parent, text="Transcribe", command=self.start_transcription)
        transcribe_button.grid(row=4, column=0, columnspan=2, pady=20, sticky='ew')

    def create_transcription_list(self, parent: ttk.Frame):
        self.transcription_list = ttk.Treeview(parent, columns=('File', 'Status'), show='headings')
        self.transcription_list.heading('File', text='File')
        self.transcription_list.heading('Status', text='Status')
        self.transcription_list.grid(row=5, column=0, columnspan=2, sticky='nsew')

    def apply_style(self):
        style = ttk.Style()
        style.theme_use('clam')

    def browse_input_file(self):
        filename = filedialog.askopenfilename(filetypes=[
            ("Audio/Video files", "*.mp3 *.mp4 *.wav *.avi *.mov *.ogg")
        ])
        self.file_path.set(filename)

    def browse_output_directory(self):
        directory = filedialog.askdirectory()
        self.output_path.set(directory)

    def start_transcription(self):
        input_file = self.file_path.get()
        output_dir = self.output_path.get()

        if not input_file or not output_dir:
            messagebox.showerror("Error", "Please select both input file and output directory.")
            return

        input_filename = Path(input_file).stem
        output_file = Path(output_dir) / f"{input_filename}_transcription.txt"

        item = self.transcription_list.insert('', 'end', values=(Path(input_file).name, 'Starting...'))
        thread = threading.Thread(target=self.run_transcription, args=(input_file, str(output_file), item))
        thread.start()
        self.active_transcriptions.append(thread)

    def run_transcription(self, input_file: str, output_file: str, item: str):
        try:
            command = self.build_transcription_command(input_file, output_file)
            self.transcription_queue.put((item, 'Running...'))

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                self.transcription_queue.put((item, 'Completed'))
            else:
                self.transcription_queue.put((item, f'Error: {stderr}'))
        except FileNotFoundError:
            self.transcription_queue.put((item, 'Error: faster-whisper.exe not found'))

    @staticmethod
    def build_transcription_command(input_file: str, output_dir: str) -> List[str]:
        return [
            'faster-whisper.exe',
            input_file,
            "--model", "large",
            "--language", "Russian",
            "--output_format", "txt",
            "--output_dir", output_dir,
            "--task", "transcribe"
        ]

    def check_transcription_queue(self):
        try:
            while True:
                item, status = self.transcription_queue.get_nowait()
                self.update_transcription_status(item, status)
        except queue.Empty:
            pass
        finally:
            self.master.after(100, self.check_transcription_queue)

    def update_transcription_status(self, item: str, status: str):
        self.transcription_list.item(item, values=(self.transcription_list.item(item)['values'][0], status))


def main():
    root = tk.Tk()
    TranscriptionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()