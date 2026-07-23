import time
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from solomon_knowledge_cards.storage.db import DatabaseManager
from solomon_knowledge_cards.migrator.importer import DoctrineImporter

class ChecklistHandler(FileSystemEventHandler):
    def __init__(self, importer: DoctrineImporter):
        self.importer = importer

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            print(f"File modified: {event.src_path}. Triggering re-import.")
            self._import_file(event.src_path)

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            print(f"File created: {event.src_path}. Triggering import.")
            self._import_file(event.src_path)

    def _import_file(self, filepath):
        try:
            # We re-import the file, migrator handles updates based on ID or creates new
            self.importer.import_file(filepath)
            print(f"Successfully imported: {filepath}")
        except Exception as e:
            print(f"Error importing {filepath}: {e}")

if __name__ == "__main__":
    db_path = os.environ.get("SOLOMON_DB_PATH", "solomon_mnemosyne.db")
    db_manager = DatabaseManager(db_path)
    importer = DoctrineImporter(db_manager)

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "openclaw-workspace", "checklists"))

    if not os.path.exists(path):
        print(f"Directory {path} does not exist. Nothing to watch.")
        sys.exit(0)

    event_handler = ChecklistHandler(importer)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"Watching {path} for checklist changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
