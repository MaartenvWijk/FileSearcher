import os
import subprocess  # To open files in Windows
import tkinter as tk
from tkinter import ttk, messagebox
import configparser  # For reading config.ini

# Optional Pillow support (app must not crash if missing)
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Load settings from config file
CONFIG_FILE = "config.ini"
config = configparser.ConfigParser()

# Set defaults if config doesn't exist
if not os.path.exists(CONFIG_FILE):
    config['Settings'] = {
        'folder_path': r'C:\Users\Administrator\Documents\codes',
        'file_extension': '.txt',
        'use_strict_match': 'no'
    }
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

# Read config values
config.read(CONFIG_FILE)
FOLDER_PATH = config['Settings'].get('folder_path', r'C:\Users\Administrator\Documents\codes')
FILE_EXTENSION = config['Settings'].get('file_extension', '.txt')
USE_STRICT_MATCH = config['Settings'].get('use_strict_match', 'no').lower() == 'yes'

def get_file_list():
    """Retrieve all filenames with the specified extension from the folder and subfolders."""
    file_list = []
    for root_dir, _, files in os.walk(FOLDER_PATH):
        for file in files:
            if file.endswith(FILE_EXTENSION):
                file_list.append(os.path.join(root_dir, file))
    return file_list

def search_exact(code_parts):
    """Search for filenames that contain each code part in sequence (with ignored middle)."""
    try:
        files = get_file_list()
        matches = []
        for file in files:
            filename = os.path.splitext(os.path.basename(file))[0]
            if USE_STRICT_MATCH:
                search_code = "".join([part for part in code_parts if part])
                if filename == search_code:
                    matches.append(file)
            else:
                idx = 0
                found = True
                for part in code_parts:
                    if not part:
                        continue
                    idx = filename.find(part, idx)
                    if idx == -1:
                        found = False
                        break
                    idx += len(part)
                if found:
                    matches.append(file)
        return matches
    except Exception as e:
        messagebox.showerror("Search Error", f"An error occurred while searching: {str(e)}")
        return []

def open_file(file_path):
    """Prompt before opening the file and open if confirmed."""
    try:
        file_name = os.path.basename(file_path)
        confirm = messagebox.askokcancel("Open File", f"Do you want to open the file for order code:\n\n{os.path.splitext(file_name)[0]}?")
        if confirm:
            subprocess.run(["explorer", file_path])
    except Exception as e:
        messagebox.showerror("Open Error", f"Failed to open file: {str(e)}")

def search_files(event=None):
    """Search for files based on the dropdowns and manual input."""
    selected_parts = [
        dropdown_vars[0].get().strip(),  # FP Type
        dropdown_vars[1].get().strip(),  # Motor Frame IEC
        dropdown_vars[2].get().strip(),  # Middle Part
        dropdown_vars[3].get().strip(),  # Execution Type
        dropdown_vars[4].get().strip(),  # Cooling Type
        manual_input_var.get().strip()   # Manual input (optional)
    ]

    try:
        matches = search_exact(selected_parts)
        listbox.delete(0, tk.END)
        if matches:
            for match in matches:
                file_name = os.path.basename(match)
                file_name_without_ext = os.path.splitext(file_name)[0]
                listbox.insert(tk.END, file_name_without_ext)
        else:
            messagebox.showinfo("No Match", "No exact match found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def on_double_click(event):
    """Handle double-click events to open a selected file."""
    try:
        selected = listbox.curselection()
        if selected:
            file_name = listbox.get(selected[0])
            full_path = [file for file in get_file_list() if os.path.splitext(os.path.basename(file))[0] == file_name]
            if full_path:
                open_file(full_path[0])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open file: {str(e)}")

def toggle_theme():
    """Switch between light and dark themes dynamically."""
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        root.configure(bg="#2d2d2d")
        title_label.config(background="#2d2d2d", foreground="#ffffff")
        listbox.config(background="#3c3f41", foreground="#ffffff")
        status_label.config(background="#2d2d2d", foreground="#ffffff")
        for widget in dropdown_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(background="#2d2d2d", foreground="#ffffff")
    else:
        root.configure(bg="#ffffff")
        title_label.config(background="#ffffff", foreground="#000000")
        listbox.config(background="#ffffff", foreground="#000000")
        status_label.config(background="#ffffff", foreground="#000000")
        for i, widget in enumerate(dropdown_frame.winfo_children()):
            if isinstance(widget, tk.Label):
                widget.configure(background=dropdown_definitions[i]["color"] if "color" in dropdown_definitions[i] else "#ffffff", foreground="#000000")

# GUI Setup
root = tk.Tk()
root.title("File Search Tool")
root.geometry("650x600")
root.resizable(False, False)
root.configure(bg="#ffffff")

dark_mode = False

# Load and display logo
logo_path = "logo.png"
if PIL_AVAILABLE and os.path.exists(logo_path):
    try:
        logo_image = Image.open(logo_path)
        icon_image = logo_image.resize((32, 32))
        logo_photo = ImageTk.PhotoImage(icon_image)
        root.tk.call("wm", "iconphoto", root._w, logo_photo)

        ui_image = logo_image.resize((250, 100))
        logo_ui_photo = ImageTk.PhotoImage(ui_image)
        logo_label = tk.Label(root, image=logo_ui_photo, bg="#ffffff")
        logo_label.image = logo_ui_photo
        logo_label.pack(pady=(10, 5), anchor="center")
    except Exception as e:
        print("Logo failed to load:", e)

# Dropdown configuration
dropdown_definitions = [
    {"label": "Engine Type", "values": ["", "FP2SS", "FP3SS", "xx", "xx"], "color": "#d6c381"},
    {"label": "Engine Size", "values": ["", "63", "71", "80", "90", "100"], "color": "#8bab89"},
    {"label": "Engine Size cont.", "values": ["", "B3", "B5", "B14A", "B5T1"], "color": "#8bab89"},
    {"label": "Execution Type", "values": ["", "B5T1", "B3", "B5", "B14A"], "color": "#92aeb9"},
    {"label": "Cooling Type", "values": ["", "TENV", "TEFC", "TEWC"], "color": "#c78ca0"}
]

# Motor code example
example_text = tk.Text(
    root,
    height=1,
    width=50,
    borderwidth=0,
    background="#f0f0f0",
    foreground="#333333",
    font=("Segoe UI", 12),
    highlightthickness=0
)
example_text.pack(pady=(5, 0), fill="x")

# Center-align text
example_text.tag_configure("center", justify="center")
example_text.tag_add("center", "1.0", "end")

# Disable user editing
example_text.configure(state='normal')
example_text.insert("end", "Example: ")
example_text.insert("end", "FP3SS", "yellow")
example_text.insert("end", "   ")
example_text.insert("end", "6314", "green")
example_text.insert("end", "   ")
example_text.insert("end", "B14B", "purple")
example_text.insert("end", "   ")
example_text.insert("end", "TENV", "darkgreen")
example_text.configure(state='disabled')

# Reapply center tag now that text is in
example_text.tag_add("center", "1.0", "end")
example_text.configure(state='disabled')

# Tag color definitions
example_text.tag_configure("yellow", background="#d6c381")
example_text.tag_configure("green", background="#8bab89")
example_text.tag_configure("purple", background="#92aeb9")
example_text.tag_configure("darkgreen", background="#c78ca0")

# Dropdowns
dropdown_vars = []
dropdown_frame = tk.Frame(root, bg="#ffffff")
dropdown_frame.pack(pady=(10, 5))

for i, definition in enumerate(dropdown_definitions):
    var = tk.StringVar()
    label_color = definition["color"] if "color" in definition else "#ffffff"
    label = tk.Label(dropdown_frame, text=definition["label"], bg=label_color, font=('Segoe UI', 9))
    label.grid(row=0, column=i, padx=5, pady=(0, 2))
    combo = ttk.Combobox(dropdown_frame, textvariable=var, values=definition["values"], state="readonly", width=12)
    combo.current(0)
    combo.grid(row=1, column=i, padx=5)
    dropdown_vars.append(var)

# Manual input field
manual_input_var = tk.StringVar()
manual_entry_label = tk.Label(root, text="Barcode Input:", bg="#ffffff", font=('Segoe UI', 12))
manual_entry_label.pack(pady=(10, 0))
manual_entry = ttk.Entry(root, textvariable=manual_input_var, width=40)
manual_entry.pack(pady=(0, 10))
manual_entry.bind("<Return>", search_files)

# Search button
search_button = ttk.Button(root, text="Search", command=search_files)
search_button.pack(pady=10)

# Listbox
listbox_frame = ttk.Frame(root)
listbox_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

listbox = tk.Listbox(listbox_frame, width=80, height=15, font=("Segoe UI", 10))
listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
listbox.bind("<Double-Button-1>", on_double_click)

# Status
status_label = ttk.Label(root, text=f"Folder: {FOLDER_PATH} | File Type: {FILE_EXTENSION}", font=("Segoe UI", 9), background="#ffffff", foreground="#000000")
status_label.pack(pady=5, side=tk.BOTTOM, fill=tk.X)

root.mainloop()
