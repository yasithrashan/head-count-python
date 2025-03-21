# analyzer.py
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

class HeadcountAnalyzer:
    def __init__(self, logs_dir='data/logs'):
        """Initialize the headcount analyzer"""
        self.logs_dir = logs_dir
        
    def get_available_logs(self):
        """Get a list of available log files"""
        log_files = glob.glob(f"{self.logs_dir}/*.csv")
        return [os.path.basename(f) for f in log_files]
        
    def analyze_log(self, log_file):
        """Analyze a specific log file"""
        # Full path to the log file
        file_path = os.path.join(self.logs_dir, log_file) if not log_file.startswith(self.logs_dir) else log_file
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: Log file {file_path} not found")
            return None
            
        # Read the CSV
        try:
            df = pd.read_csv(file_path)
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Basic statistics
            stats = {
                'total_observations': len(df),
                'time_period': f"{df['timestamp'].min()} to {df['timestamp'].max()}",
                'average_count': df['count'].mean(),
                'max_count': df['count'].max(),
                'min_count': df['count'].min(),
                'peak_time': df.loc[df['count'].idxmax(), 'timestamp'],
            }
            
            return {
                'stats': stats,
                'data': df
            }
            
        except Exception as e:
            print(f"Error analyzing log file: {e}")
            return None
            
    def visualize_log(self, log_file, save_path=None):
        """Create visualization of headcount data"""
        analysis = self.analyze_log(log_file)
        if not analysis:
            return False
            
        df = analysis['data']
        stats = analysis['stats']
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Plot headcount over time
        plt.plot(df['timestamp'], df['count'], marker='o', linestyle='-', color='blue')
        
        # Add horizontal line for average
        plt.axhline(y=stats['average_count'], color='r', linestyle='--', alpha=0.7, 
                   label=f"Average: {stats['average_count']:.1f}")
        
        # Annotate peak
        max_idx = df['count'].idxmax()
        plt.annotate(f"Peak: {df['count'].max()}",
                    xy=(df.loc[max_idx, 'timestamp'], df.loc[max_idx, 'count']),
                    xytext=(10, 20),
                    textcoords='offset points',
                    arrowprops=dict(arrowstyle='->'))
        
        # Format plot
        plt.title(f"Headcount Analysis - {os.path.basename(log_file)}")
        plt.xlabel("Time")
        plt.ylabel("Number of People")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save or show
        if save_path:
            plt.savefig(save_path)
            print(f"Visualization saved to {save_path}")
        else:
            plt.show()
            
        return True
        
    def generate_report(self, log_file=None):
        """Generate a text report of headcount analysis"""
        # If no log specified, use the most recent
        if not log_file:
            logs = self.get_available_logs()
            if not logs:
                print("No log files found")
                return
            log_file = max(logs, key=lambda x: os.path.getmtime(os.path.join(self.logs_dir, x)))
            
        # Analyze the log
        analysis = self.analyze_log(log_file)
        if not analysis:
            return
            
        stats = analysis['stats']
        
        # Generate report text
        report = f"""
        ============================================
        HEADCOUNT ANALYSIS REPORT
        ============================================
        Log file: {log_file}
        
        Time period: {stats['time_period']}
        Total observations: {stats['total_observations']}
        
        STATISTICS:
        - Average count: {stats['average_count']:.2f} people
        - Maximum count: {stats['max_count']} people
        - Minimum count: {stats['min_count']} people
        - Peak time: {stats['peak_time']}
        
        ============================================
        Report generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
        ============================================
        """
        
        print(report)
        return report

# For direct execution
if __name__ == "__main__":
    analyzer = HeadcountAnalyzer()
    logs = analyzer.get_available_logs()
    
    if logs:
        print("Available logs:")
        for i, log in enumerate(logs):
            print(f"{i+1}. {log}")
            
        selection = input("\nSelect a log to analyze (number) or press Enter for most recent: ")
        
        if selection.strip():
            try:
                selected_log = logs[int(selection) - 1]
                analyzer.generate_report(selected_log)
                analyzer.visualize_log(selected_log)
            except (ValueError, IndexError):
                print("Invalid selection")
        else:
            analyzer.generate_report()
            
    else:
        print("No log files found. Run the headcount detector first.")