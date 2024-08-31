import requests
import winsound
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import threading

def check_earthquakes(threshold=5.5, processed_ids=set(), listbox=None, start_time=None):
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        for feature in data['features']:
            earthquake_id = feature['id']
            magnitude = feature['properties']['mag']
            place = feature['properties']['place']
            timestamp = feature['properties']['time']
            depth = feature['geometry']['coordinates'][2]
            
            # Check if the earthquake is new (after the start time) and has not been processed yet
            if magnitude >= threshold and earthquake_id not in processed_ids and timestamp > start_time:
                alert_user(magnitude, place, timestamp, depth, listbox)
                processed_ids.add(earthquake_id)  # Mark this earthquake as processed
    except requests.exceptions.RequestException as e:
        print(f"Error fetching earthquake data: {e}")

def alert_user(magnitude, place, timestamp, depth, listbox):
    # Convert the timestamp to a readable format
    time_of_event = datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S UTC')
    alert_message = f"Magnitude: {magnitude}, Location: {place}, Time: {time_of_event}, Depth: {depth} km"
    
    # Display the alert in the Listbox
    if listbox is not None:
        listbox.insert(tk.END, alert_message)
    
    # Play a beep sound for the alert
    winsound.Beep(1000, 1000)
    
    # Display a popup alert
    show_popup_alert(magnitude, place, time_of_event, depth)

def show_popup_alert(magnitude, place, time_of_event, depth):
    # Create a new top-level window
    alert_window = tk.Toplevel()
    alert_window.title("Earthquake Alert!")

    # Display the alert message in the popup
    message = f"Earthquake Alert!\n\nMagnitude: {magnitude}\nLocation: {place}\nTime: {time_of_event}\nDepth: {depth} km"
    tk.Label(alert_window, text=message, padx=20, pady=20).pack()

    # Set the size and position of the alert window
    alert_window.geometry("300x150+500+300")

    # Automatically close the popup after a certain period (e.g., 10 seconds)
    alert_window.after(10000, alert_window.destroy)

def start_monitoring(listbox):
    THRESHOLD_MAGNITUDE = 5.5
    POLL_INTERVAL = 60  # seconds
    processed_earthquake_ids = set()  # Initialize an empty set to track processed earthquake IDs
    start_time = int(time.time() * 1000)  # Record the start time in milliseconds

    while True:
        check_earthquakes(THRESHOLD_MAGNITUDE, processed_earthquake_ids, listbox, start_time)
        time.sleep(POLL_INTERVAL)

def create_gui():
    root = tk.Tk()
    root.title("Real-Time Earthquake Alerts")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    listbox = tk.Listbox(frame, width=100)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)

    scrollbar = tk.Scrollbar(frame, orient="vertical")
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    # Start monitoring in a separate thread
    monitoring_thread = threading.Thread(target=start_monitoring, args=(listbox,))
    monitoring_thread.daemon = True
    monitoring_thread.start()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
