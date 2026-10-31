import os
import json
import threading
from datetime import datetime


class Persistence():
    def __init__(self, filename):
        self.filename = filename
        self.last_written = None
        # Reads return None and writes are skipped while paused, e.g. while shutting down
        self.paused = False
        # Serializes reads and writes, including from worker threads
        self.lock = threading.Lock()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def read(self):
        with self.lock:
            if self.paused or not os.path.exists(self.filename):
                return None
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)

    def write(self, data={}):
        json_data = json.dumps(data, indent=4)
        with self.lock:
            if self.paused:
                return
            # Often called every second by an update loop; only touch the disk when something changed
            if json_data == self.last_written:
                return
            # Write to a temp file and swap it in so a crash mid-write can't corrupt the data file
            temp_filename = f"{self.filename}.tmp"
            with open(temp_filename, 'w', encoding='utf-8') as file:
                file.write(json_data)
            os.replace(temp_filename, self.filename)
            self.last_written = json_data

    def quarantine(self):
        """
        Moves an unreadable data file aside so it can't be overwritten. Returns the new path,
        or None if there was no file.
        """
        with self.lock:
            if not os.path.exists(self.filename):
                return None
            backup = f"{self.filename}.corrupt-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            os.replace(self.filename, backup)
            self.last_written = None
            return backup
