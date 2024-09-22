import os
import shutil

project_structure = {
    'config': {
        'projects.yaml': """projects:
  - name: "Nano Block Explorer"
    description: "A block explorer for the Nano cryptocurrency."
    url: "https://nanoblockexplorer.example.com"
    image: "images/block_explorer.png"
  - name: "Nano Monitoring Tool"
    description: "Real-time monitoring for the Nano network."
    url: "https://nanomonitor.example.com"
    image: "images/monitoring_tool.png"
""",
        'social_links.yaml': """social_links:
  - platform: "GitHub"
    url: "https://github.com/gr0vity"
    icon: "images/github_icon.png"
  - platform: "Twitter"
    url: "https://twitter.com/gr0vity"
    icon: "images/twitter_icon.png"
"""
    },
    'static': {
        'css': {
            'styles.css': """body {
    font-family: 'Roboto', sans-serif;
    margin: 0;
    padding: 0;
}

.projects {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
}

.project {
    width: 300px;
    margin: 20px;
    text-align: center;
}

.project img {
    max-width: 100%;
    height: auto;
}

footer {
    text-align: center;
    padding: 20px;
}

footer a {
    margin: 0 10px;
}

footer img {
    width: 32px;
    height: 32px;
}
"""
        },
        'images': {
            'block_explorer.png': '',  # Placeholder for your image
            'monitoring_tool.png': '',  # Placeholder for your image
            'github_icon.png': '',  # Placeholder for your image
            'twitter_icon.png': '',  # Placeholder for your image
        }
    },
    'templates': {
        'base.html': """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title if title else "gr0vity's Projects" }}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <link href="https://fonts.googleapis.com/css?family=Roboto&display=swap" rel="stylesheet">
</head>
<body>
    {% block content %}{% endblock %}
    <footer>
        {% for link in social_links %}
            <a href="{{ link.url }}"><img src="{{ url_for('static', filename=link.icon) }}" alt="{{ link.platform }}"></a>
        {% endfor %}
    </footer>
</body>
</html>
""",
        'index.html': """{% extends "base.html" %}
{% block content %}
<h1>My Projects</h1>
<div class="projects">
    {% for project in projects %}
    <div class="project">
        <img src="{{ url_for('static', filename=project.image) }}" alt="{{ project.name }}">
        <h2>{{ project.name }}</h2>
        <p>{{ project.description }}</p>
        <a href="{{ project.url }}">Learn More</a>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""
    },
    'app.py': """from flask import Flask, render_template
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
    app.run(debug=True)
""",
    'requirements.txt': """Flask
PyYAML
watchdog
""",
    'Dockerfile': """FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
""",
    'docker-compose.yml': """version: '3'
services:
  web:
    build: .
    volumes:
      - .:/app
    ports:
      - "5000:5000"
"""
}


def create_project(structure, root='.'):
    for name, content in structure.items():
        path = os.path.join(root, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_project(content, root=path)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)


def create_placeholder_images():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as e:
        print(f"Pillow is not installed. Skipping image creation. {e}")
        return

    images = {
        'static/images/block_explorer.png': 'Block Explorer',
        'static/images/monitoring_tool.png': 'Monitoring Tool',
        'static/images/github_icon.png': 'GitHub',
        'static/images/twitter_icon.png': 'Twitter',
    }

    for path, text in images.items():
        img = Image.new('RGB', (200, 200), color=(73, 109, 137))
        draw = ImageDraw.Draw(img)
        font_size = 20
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Use textbbox instead of textsize
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        position = ((200 - text_width) / 2, (200 - text_height) / 2)
        draw.text(position, text, fill=(255, 255, 255), font=font)
        img.save(path)


if __name__ == '__main__':
    # Clean up existing project if it exists
    existing_items = ['config', 'static', 'templates', 'app.py',
                      'requirements.txt', 'Dockerfile', 'docker-compose.yml']
    if any(os.path.exists(item) for item in existing_items):
        confirm = input("Existing project files detected. Overwrite? (y/n): ")
        if confirm.lower() != 'y':
            exit()
        for item in existing_items:
            if os.path.isdir(item):
                shutil.rmtree(item, ignore_errors=True)
            elif os.path.isfile(item):
                os.remove(item)
    # Create project structure
    create_project(project_structure)
    # Create placeholder images
    create_placeholder_images()
    print("Project setup is complete.")
