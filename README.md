# Django Container Terminal Web Application

This project is a Django-based web application that provides a browser-based terminal interface and container management using Podman.

## Features

* Django + Channels (WebSockets)
* Browser terminal using xterm.js
* Container management via Podman
* Real-time logs and terminal access
* Multi-container dashboard

---

## System Requirements

* Python 3.10+
* Git
* Podman
* Linux (Ubuntu/Kubuntu recommended)

---

## Installation Steps

### 1. Install Dependencies

```bash
sudo apt update
sudo apt install git python3 python3-venv python3-pip podman -y
```

### 2. Start Podman Socket

```bash
systemctl --user start podman.socket
systemctl --user enable podman.socket
```

### 3. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 4. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Install Python Requirements

```bash
pip install -r requirements.txt
```

### 6. Database Migration

```bash
python manage.py migrate
```

### 7. Run Application (Daphne)

```bash
daphne -b 127.0.0.1 -p 8000 mysite.asgi:application
```

Open browser:

```
http://127.0.0.1:8000
```

---

## Development Workflow

Push changes:

```bash
git add .
git commit -m "message"
git push
```

Pull changes:

```bash
git pull
```

---

## Author

Manoj Kumar
