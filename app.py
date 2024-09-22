from flask import Flask, render_template
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

app = Flask(__name__)


def load_config():
    with open('config/projects.yaml', 'r') as file:
        projects = yaml.safe_load(file)['projects']
    with open('config/social_links.yaml', 'r') as file:
        social_links = yaml.safe_load(file)['social_links']
    return projects, social_links


projects, social_links = load_config()


class ConfigEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global projects, social_links
        projects, social_links = load_config()
        print("Configurations reloaded")


def start_watcher():
    event_handler = ConfigEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path='config/', recursive=False)
    observer.start()


watcher_thread = threading.Thread(target=start_watcher)
watcher_thread.daemon = True
watcher_thread.start()


@app.route('/')
def index():
    return render_template('index.html', projects=projects, social_links=social_links)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
