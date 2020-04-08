import sys, time, shutil, os, re
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler


class ClassMaterialEventHandler(RegexMatchingEventHandler):
    def __init__(self, *args, **kwargs):
        super(ClassMaterialEventHandler, self).__init__(*args, **kwargs)
        self.last_created = None
        self.last_modified = None

        # Change this to choose another target directory
        self.target_dir = "C:\\Users\Hung Nguyen\Desktop\Readings and works\\3rd Year\Second Sem"


    def get_class_path(self, path):
        """
        Find the folder for the right class and session.
        If it doesn't exist, create a new one and return the absolute path.
        """
        pattern = r"(?P<name>\w\w?[1-9]{3})_(?P<week>[1-9]|1[0-5])_(?P<session>[1-2])_?.*"
        class_detail = re.match(pattern, path.split("\\")[-1])
        class_name = class_detail.group("name").upper()
        class_week = class_detail.group("week")
        class_session = class_detail.group("session")
        session_number = "_".join([class_week, class_session])

        for root, dirs, files in os.walk(self.target_dir):
            if root == self.target_dir:
                dirs = list(filter(lambda folder: folder == class_name, dirs))
                if not dirs:
                    to_dir = os.path.join(self.target_dir, class_name, session_number)
                    os.makedirs(to_dir)
                    return to_dir
            if root == os.path.join(self.target_dir, class_name):
                to_dir = os.path.join(root, session_number)
                if not session_number in dirs:
                    os.mkdir(to_dir)
                return to_dir


    def on_created(self, event):
        path = event.src_path
        if path != self.last_created:
            self.last_created = path
            print("Created", path)


    def on_modified(self, event):
        path = event.src_path
        if path != self.last_modified:
            self.last_modified = path
            to_path = self.get_class_path(path)
            shutil.move(path, to_path)
            print(f"Moved to {to_path}")


    def on_deleted(self, event):
        path = event.src_path
        if path == self.last_created:
            self.last_created = None
        if path == self.last_modified:
            self.last_modified = None
        print("Deleted", path)


if __name__ == "__main__":
    # Assumes the file is always named: classname_week_session_abc.*
    # For example: "B111_1_2_marketing_reading.pdf"
    event_handler = ClassMaterialEventHandler(regexes=['.*\w\w?[1-9]{3}_([1-9]|1[0-5])_[1-2]_?.*'])
    watch_path = "C:\\Users\Hung Nguyen\Downloads"   # Change this to watch another directory
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
