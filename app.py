# app.py
import os
import tkinter as tk
from tkinter import ttk, messagebox
from headcount import HeadcountDetector
from analyzer import HeadcountAnalyzer
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HeadcountApp:
    def __init__(self, root):
        self.root = root
        self.root.title("University Headcount System")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        self.detector = HeadcountDetector()
        self.analyzer = HeadcountAnalyzer()
        
        self.detection_running = False
        self.current_log = None
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tab control
        tab_control = ttk.Notebook(main_frame)
        
        # Detection tab
        detection_tab = ttk.Frame(tab_control)
        tab_control.add(detection_tab, text="Headcount Detection")
        
        # Analysis tab
        analysis_tab = ttk.Frame(tab_control)
        tab_control.add(analysis_tab, text="Data Analysis")
        
        tab_control.pack(fill=tk.BOTH, expand=True)
        
        # === Detection Tab ===
        detection_frame = ttk.LabelFrame(detection_tab, text="Camera Detection", padding=10)
        detection_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Location input
        ttk.Label(detection_frame, text="Location Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar(value="Classroom")
        ttk.Entry(detection_frame, textvariable=self.location_var, width=30).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Camera selection
        ttk.Label(detection_frame, text="Camera:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.camera_var = tk.IntVar(value=0)
        ttk.Combobox(detection_frame, textvariable=self.camera_var, values=[0, 1, 2, 3], width=5).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Confidence threshold
        ttk.Label(detection_frame, text="Confidence Threshold:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.confidence_var = tk.DoubleVar(value=0.5)
        confidence_scale = ttk.Scale(detection_frame, from_=0.1, to=0.9, variable=self.confidence_var, orient=tk.HORIZONTAL, length=200)
        confidence_scale.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Label(detection_frame, textvariable=self.confidence_var).grid(row=2, column=2, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(detection_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Detection", command=self.start_detection)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Detection", command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(detection_frame, textvariable=self.status_var, font=('', 10, 'italic'))
        status_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        # === Analysis Tab ===
        analysis_frame = ttk.LabelFrame(analysis_tab, text="Headcount Analysis", padding=10)
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log selection
        ttk.Label(analysis_frame, text="Select Log:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.log_var = tk.StringVar()
        self.log_combobox = ttk.Combobox(analysis_frame, textvariable=self.log_var, width=40)
        self.log_combobox.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Refresh logs button
        refresh_button = ttk.Button(analysis_frame, text="↻", width=3, command=self.refresh_logs)
        refresh_button.grid(row=0, column=2, padx=5)
        
        # Analysis buttons
        analysis_button_frame = ttk.Frame(analysis_frame)
        analysis_button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(analysis_button_frame, text="Generate Report", command=self.generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(analysis_button_frame, text="Visualize Data", command=self.visualize_data).pack(side=tk.LEFT, padx=5)
        
        # Results frame for visualization
        self.results_frame = ttk.LabelFrame(analysis_frame, text="Results", padding=10)
        self.results_frame.grid(row=2, column=0, columnspan=3, sticky=tk.NSEW, pady=10)
        analysis_frame.grid_rowconfigure(2, weight=1)
        analysis_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize logs list
        self.refresh_logs()
        
    def refresh_logs(self):
        """Refresh the list of available logs"""
        logs = self.analyzer.get_available_logs()
        self.log_combobox['values'] = logs
        if logs:
            self.log_combobox.current(len(logs) - 1)  # Select most recent
            
    def start_detection(self):
        """Start the headcount detection process"""
        if self.detection_running:
            return
            
        # Get parameters
        location = self.location_var.get()
        camera = self.camera_var.get()
        confidence = self.confidence_var.get()
        
        # Update detector settings
        self.detector = HeadcountDetector(camera_id=camera, confidence=confidence)
        
        # Update UI
        self.start_button['state'] = tk.DISABLED
        self.stop_button['state'] = tk.NORMAL
        self.status_var.set(f"Running detection for {location}...")
        self.detection_running = True
        
        # Start detection in a separate thread
        self.detection_thread = threading.Thread(target=self._run_detection_thread, args=(location,))
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
    def _run_detection_thread(self, location):
        """Run detection in a background thread"""
        try:
            self.current_log = self.detector.run_detection(location)
            
            # Update UI from main thread
            self.root.after(0, self._detection_completed)
        except Exception as e:
            # Update UI from main thread
            self.root.after(0, lambda: self._detection_error(str(e)))
            
    def _detection_completed(self):
        """Called when detection completes successfully"""
        self.detection_running = False
        self.start_button['state'] = tk.NORMAL
        self.stop_button['state'] = tk.DISABLED
        self.status_var.set(f"Detection completed. Log saved.")
        self.refresh_logs()
        
    def _detection_error(self, error_msg):
        """Called when detection encounters an error"""
        self.detection_running = False
        self.start_button['state'] = tk.NORMAL
        self.stop_button['state'] = tk.DISABLED
        self.status_var.set(f"Error: {error_msg}")
        messagebox.showerror("Detection Error", f"An error occurred: {error_msg}")
        
    def stop_detection(self):
        """Stop the headcount detection"""
        # We can't directly stop the OpenCV loop, but we'll set a flag
        self.detection_running = False
        self.status_var.set("Stopping detection (press 'q' in the camera window)...")
        
    def generate_report(self):
        """Generate an analysis report for the selected log"""
        selected_log = self.log_var.get()
        if not selected_log:
            messagebox.showwarning("No Log Selected", "Please select a log file to analyze.")
            return
            
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        # Generate report
        report = self.analyzer.generate_report(selected_log)
        
        # Display report
        report_text = tk.Text(self.results_frame, wrap=tk.WORD, height=15)
        report_text.pack(fill=tk.BOTH, expand=True)
        report_text.insert(tk.END, report)
        report_text.config(state=tk.DISABLED)
        
    def visualize_data(self):
        """Visualize the selected log data"""
        selected_log = self.log_var.get()
        if not selected_log:
            messagebox.showwarning("No Log Selected", "Please select a log file to analyze.")
            return
            
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        # Get analysis data
        analysis = self.analyzer.analyze_log(selected_log)
        if not analysis:
            messagebox.showerror("Analysis Error", "Could not analyze the selected log file.")
            return
            
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 4))
        df = analysis['data']
        stats = analysis['stats']
        
        # Plot data
        ax.plot(df['timestamp'], df['count'], marker='o', linestyle='-', color='blue')
        ax.axhline(y=stats['average_count'], color='r', linestyle='--', alpha=0.7, 
                   label=f"Average: {stats['average_count']:.1f}")
        
        # Annotate peak
        max_idx = df['count'].idxmax()
        ax.annotate(f"Peak: {df['count'].max()}",
                    xy=(df.loc[max_idx, 'timestamp'], df.loc[max_idx, 'count']),
                    xytext=(10, 20),
                    textcoords='offset points',
                    arrowprops=dict(arrowstyle='->'))
        
        # Format plot
        ax.set_title(f"Headcount Analysis - {os.path.basename(selected_log)}")
        ax.set_xlabel("Time")
        ax.set_ylabel("Number of People")
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.xticks(rotation=45)
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = HeadcountApp(root)
    root.mainloop()