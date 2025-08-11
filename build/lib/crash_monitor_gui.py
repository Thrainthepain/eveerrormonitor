#!/usr/bin/env python3
"""
Simple GUI for Eve Online Crash Monitor
Inspired by CCP Games' EveLogLite
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import os
import sys
from datetime import datetime
import queue
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Add the python directory to the path to import our crash monitor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from eve_crash_monitor import EveOnlineCrashMonitor
except ImportError:
    print("Error: Could not import eve_crash_monitor. Make sure it's in the same directory.")
    sys.exit(1)


class GUILogHandler(logging.Handler):
    """Custom logging handler that sends logs to the GUI queue."""
    
    def __init__(self, log_queue: queue.Queue[str]):
        super().__init__()
        self.log_queue = log_queue
        
    def emit(self, record: logging.LogRecord) -> None:
        """Send log record to GUI queue."""
        try:
            log_message = self.format(record)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"[{timestamp}] {record.levelname}: {log_message}\n"
            self.log_queue.put(formatted_message)
        except Exception:
            pass  # Avoid recursive logging errors


class CrashMonitorGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Eve Online Crash Monitor - GUI")
        self.root.geometry("900x700")
        
        # Initialize monitor
        self.monitor: Optional[EveOnlineCrashMonitor] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        self.log_queue: queue.Queue[str] = queue.Queue()
        self.start_time: Optional[datetime] = None
        
        # Create GUI
        self.create_widgets()
        self.setup_layout()
        
        # Start checking for log updates
        self.check_log_queue()
        
    def create_widgets(self) -> None:
        """Create all GUI widgets."""
        
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        
        # Control frame
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Monitor Controls", padding="5")
        
        # Start/Stop buttons
        self.start_btn = ttk.Button(self.control_frame, text="Start Monitoring", 
                                   command=self.start_monitoring, style="Accent.TButton")
        self.stop_btn = ttk.Button(self.control_frame, text="Stop Monitoring", 
                                  command=self.stop_monitoring, state="disabled")
        
        # Status label
        self.status_label = ttk.Label(self.control_frame, text="Status: Stopped", 
                                     font=("Arial", 10, "bold"))
        
        # Configuration frame
        self.config_frame = ttk.LabelFrame(self.main_frame, text="Configuration", padding="5")
        
        # Check interval
        ttk.Label(self.config_frame, text="Check Interval (seconds):").grid(row=0, column=0, sticky="w", padx=5)
        self.interval_var = tk.StringVar(value="5")
        self.interval_entry = ttk.Entry(self.config_frame, textvariable=self.interval_var, width=10)
        
        # Process names
        ttk.Label(self.config_frame, text="Process Names:").grid(row=1, column=0, sticky="w", padx=5)
        self.processes_var = tk.StringVar(value="ExeFile.exe, eve.exe")
        self.processes_entry = ttk.Entry(self.config_frame, textvariable=self.processes_var, width=30)
        
        # Log display frame
        self.log_frame = ttk.LabelFrame(self.main_frame, text="Crash Events Log", padding="5")
        
        # Log display with scrollbar
        self.log_display = scrolledtext.ScrolledText(self.log_frame, height=20, width=80, 
                                                    font=("Consolas", 9))
        
        # Statistics frame
        self.stats_frame = ttk.LabelFrame(self.main_frame, text="Statistics", padding="5")
        
        self.crashes_count_label = ttk.Label(self.stats_frame, text="Total Crashes: 0")
        self.processes_count_label = ttk.Label(self.stats_frame, text="Eve Processes: 0")
        self.uptime_label = ttk.Label(self.stats_frame, text="Monitor Uptime: 00:00:00")
        
        # Menu bar
        self.create_menu()
        
    def create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Log File", command=self.open_log_file)
        file_menu.add_command(label="Save Configuration", command=self.save_config)
        file_menu.add_command(label="Load Configuration", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Clear Log Display", command=self.clear_log_display)
        view_menu.add_command(label="Refresh Statistics", command=self.refresh_stats)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def setup_layout(self):
        """Setup widget layout."""
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control frame layout
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.status_label.pack(side=tk.LEFT)
        
        # Configuration frame layout
        self.config_frame.pack(fill=tk.X, pady=(0, 10))
        self.interval_entry.grid(row=0, column=1, sticky="w", padx=5)
        self.processes_entry.grid(row=1, column=1, sticky="w", padx=5)
        
        # Log display layout
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.log_display.pack(fill=tk.BOTH, expand=True)
        
        # Statistics layout
        self.stats_frame.pack(fill=tk.X)
        self.crashes_count_label.pack(side=tk.LEFT, padx=(0, 20))
        self.processes_count_label.pack(side=tk.LEFT, padx=(0, 20))
        self.uptime_label.pack(side=tk.LEFT)
        
    def start_monitoring(self) -> None:
        """Start the crash monitor."""
        try:
            # Create monitor configuration
            config: Dict[str, Any] = {
                "check_interval": int(self.interval_var.get()),
                "process_names": [name.strip() for name in self.processes_var.get().split(",")],
                "log_level": "INFO",
                "enable_event_log_monitoring": True,
                "enable_process_monitoring": True,
                "enable_log_file_monitoring": True,
                "crash_detection_threshold": 30,
                "output_file": "../logs/eve_crash_log.txt",
                "exclude_files": [
                    "eve_crash_monitor.log",
                    "eve_crash_log.txt",
                    "eve_crash_log.json",
                    "eve_crash_log_simple.txt",
                    "simple_eve_crash_log.txt",
                    "crash_monitor.log",
                    "enhanced_crash_monitor.log",
                    "Squirrel-CheckForUpdate.log",
                    "Squirrel-Update.log",
                    "Squirrel.log"
                ],
                "exclude_patterns": [
                    "Squirrel",
                    "update", 
                    "launcher",
                    "crash_monitor",
                    "crash_log",
                    "monitor",
                    "eve_crash"
                ]
            }
            
            # Initialize monitor
            self.monitor = EveOnlineCrashMonitor()
            # Type assertion to fix config type annotation issue
            self.monitor.config.update(config)  # type: ignore
            
            # Add our GUI log handler to the monitor's logger
            gui_handler = GUILogHandler(self.log_queue)
            gui_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(message)s')
            gui_handler.setFormatter(formatter)
            self.monitor.logger.addHandler(gui_handler)
            
            # Start monitoring in a separate thread
            self.monitor_thread = threading.Thread(target=self.run_monitor, daemon=True)
            self.monitor_thread.start()
            
            # Track start time
            self.start_time = datetime.now()
            
            # Update UI
            self.is_monitoring = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_label.config(text="Status: Monitoring", foreground="green")
            
            self.log_message("INFO", "🚀 Crash monitoring started successfully")
            self.log_message("INFO", f"Monitoring processes: {', '.join(config['process_names'])}")
            self.log_message("INFO", f"Check interval: {config['check_interval']} seconds")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {e}")
            self.log_message("ERROR", f"Failed to start monitoring: {e}")
            
    def stop_monitoring(self) -> None:
        """Stop the crash monitor."""
        if self.monitor:
            self.monitor.stop_monitoring()
            
        self.is_monitoring = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Status: Stopped", foreground="red")
        
        # Calculate uptime
        if self.start_time:
            uptime = datetime.now() - self.start_time
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            self.log_message("INFO", f"⏹️ Monitoring stopped. Uptime: {uptime_str}")
        else:
            self.log_message("INFO", "⏹️ Crash monitoring stopped")
        
    def run_monitor(self) -> None:
        """Run the monitor in a separate thread."""
        if self.monitor:
            self.monitor.start_monitoring()
            
    def log_message(self, level: str, message: str) -> None:
        """Add a message to the log display."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # Add to queue for thread-safe GUI update
        self.log_queue.put(formatted_message)
        
    def check_log_queue(self) -> None:
        """Check for new log messages and update the display."""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_display.insert(tk.END, message)
                self.log_display.see(tk.END)
                
                # Update statistics when we get new messages
                self.update_statistics()
        except queue.Empty:
            pass
        
        # Update statistics every 5 seconds when monitoring
        if self.is_monitoring:
            self.update_statistics()
        
        # Schedule next check
        self.root.after(100, self.check_log_queue)
        
    def update_statistics(self) -> None:
        """Update the statistics display."""
        if self.monitor:
            try:
                # Get current statistics - use the correct attribute name
                eve_processes = getattr(self.monitor, 'eve_processes', [])
                process_count = len(eve_processes) if eve_processes else 0
                self.processes_count_label.config(text=f"Eve Processes: {process_count}")
                
                # Update uptime
                if self.start_time and self.is_monitoring:
                    uptime = datetime.now() - self.start_time
                    uptime_str = str(uptime).split('.')[0]  # Remove microseconds
                    self.uptime_label.config(text=f"Monitor Uptime: {uptime_str}")
                    
                # Log debug info periodically
                if hasattr(self, '_last_stats_log'):
                    if (datetime.now() - self._last_stats_log).seconds > 30:  # Log every 30 seconds
                        self.log_message("DEBUG", f"Statistics: {process_count} Eve processes detected")
                        self._last_stats_log = datetime.now()
                else:
                    self._last_stats_log = datetime.now()
                    
            except Exception as e:
                self.log_message("DEBUG", f"Error updating statistics: {e}")
        
    def clear_log_display(self) -> None:
        """Clear the log display."""
        self.log_display.delete(1.0, tk.END)
        self.log_message("INFO", "📝 Log display cleared")
        
    def refresh_stats(self) -> None:
        """Refresh statistics display."""
        self.update_statistics()
        if self.monitor and hasattr(self.monitor, 'eve_processes'):
            eve_processes = getattr(self.monitor, 'eve_processes', [])
            process_count = len(eve_processes) if eve_processes else 0
            self.log_message("INFO", f"📊 Statistics refreshed - {process_count} Eve processes")
                
    def open_log_file(self) -> None:
        """Open and display a log file."""
        filename = filedialog.askopenfilename(
            title="Open Log File",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                self.log_display.delete(1.0, tk.END)
                self.log_display.insert(1.0, content)
                self.log_message("INFO", f"📁 Opened log file: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")
                
    def save_config(self) -> None:
        """Save current configuration to file."""
        config = {
            "check_interval": self.interval_var.get(),
            "process_names": self.processes_var.get()
        }
        
        # Use the correct tkinter method name
        filename = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            file_path = Path(filename)
            try:
                with open(file_path, 'w') as f:
                    json.dump(config, f, indent=4)
                messagebox.showinfo("Success", "Configuration saved successfully")
                self.log_message("INFO", f"💾 Configuration saved: {file_path.name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")
                
    def load_config(self) -> None:
        """Load configuration from file."""
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            file_path = Path(str(filename))
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)
                
                if "check_interval" in config:
                    self.interval_var.set(str(config["check_interval"]))
                if "process_names" in config:
                    if isinstance(config["process_names"], list):
                        self.processes_var.set(", ".join(config["process_names"]))
                    else:
                        self.processes_var.set(config["process_names"])
                        
                messagebox.showinfo("Success", "Configuration loaded successfully")
                self.log_message("INFO", f"📂 Configuration loaded: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {e}")
                
    def show_about(self) -> None:
        """Show about dialog."""
        about_text = """Eve Online Crash Monitor GUI

Version: 1.0
Author: Crash Monitor Team
Inspired by CCP Games' EveLogLite

This tool monitors Eve Online for crashes and provides
real-time crash detection and logging capabilities.

Features:
• Real-time process monitoring
• Windows Event Log integration  
• Advanced crash detection
• EveLogLite compatibility
• Squirrel updater log filtering"""
        
        messagebox.showinfo("About", about_text)
        
    def on_closing(self) -> None:
        """Handle window closing."""
        if self.is_monitoring:
            if messagebox.askokcancel("Quit", "Monitoring is active. Stop monitoring and quit?"):
                self.stop_monitoring()
                self.root.destroy()
        else:
            self.root.destroy()


def main() -> None:
    """Main entry point."""
    root = tk.Tk()
    
    # Set modern theme if available
    try:
        style = ttk.Style()
        style.theme_use('vista')  # Use modern theme on Windows
    except Exception:
        pass
    
    app = CrashMonitorGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main()
