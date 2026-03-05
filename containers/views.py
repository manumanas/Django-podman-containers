from django.http import HttpResponse
import podman
from django.shortcuts import render, redirect
from datetime import datetime
import subprocess
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import time
from .models import Container
import os
from django.conf import settings


HEADSCALE_URL = settings.HEADSCALE_URL
PREAUTH_KEY = settings.PREAUTH_KEY

# PODMAN CLIENT

client = podman.PodmanClient(
    base_url="unix:///run/user/1001/podman/podman.sock"
)


# AUTOSTART FUNCTION

def enable_autostart(container_name):

    service_dir = os.path.expanduser("~/.config/systemd/user")

    subprocess.run(f"mkdir -p {service_dir}", shell=True)

    subprocess.run(
        f"podman generate systemd --name {container_name} --files",
        shell=True
    )

    subprocess.run(
        f"mv container-{container_name}.service {service_dir}/",
        shell=True
    )

    subprocess.run("systemctl --user daemon-reexec", shell=True)
    subprocess.run("systemctl --user daemon-reload", shell=True)

    subprocess.run(
        f"systemctl --user enable container-{container_name}.service",
        shell=True
    )

    subprocess.run("loginctl enable-linger $USER", shell=True)


# AUTH VIEWS

def home(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    signin_error = ""
    signup_error = ""

    if request.method == "POST":

        action = request.POST.get("action")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if action == "signin":

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect("dashboard")

            if not User.objects.filter(username=username).exists():
                signin_error = "Account not found. Please sign up."
            else:
                signin_error = "Invalid password."

        elif action == "signup":

            if User.objects.filter(username=username).exists():
                signup_error = "Account already exists. Please sign in."
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password
                )
                login(request, user)
                return redirect("dashboard")

    return render(request, "containers/auth.html", {
        "signin_error": signin_error,
        "signup_error": signup_error
    })


def logout_view(request):
    logout(request)
    return redirect("home")


# DASHBOARD

@login_required(login_url="home")
def dashboard(request):

    msg = ""

    if request.method == "POST":

        container_name = request.POST.get("name")
        action = request.POST.get("action")

        # CREATE CONTAINER
        if action == "create":

            new_name = request.POST.get("new_name")

            try:
                client.containers.run(
                    "ubuntu-systemd",
                    command=["/sbin/init"],
                    detach=True,
                    tty=True,
                    stdin_open=True,
                    privileged=True,
                    name=new_name,
                    restart_policy={"Name": "always"},
                    volumes={
                        "/sys/fs/cgroup": {
                            "bind": "/sys/fs/cgroup",
                            "mode": "ro"
                        }
                    },
                    environment={
                        "container": "podman"
                    }
                )

                enable_autostart(new_name)

                time.sleep(3)

                # START TAILSCALED
                subprocess.run(
                    f"podman exec {new_name} systemctl start tailscaled",
                    shell=True
                )

                # subprocess.run(
                #     f"podman exec {new_name} systemctl enable tailscaled",
                #     shell=True
                # )

                time.sleep(3)

                # CONNECT TO HEADSCALE
                subprocess.run(
                    f"podman exec {new_name} bash -c 'tailscale up --login-server={HEADSCALE_URL} --authkey={PREAUTH_KEY} --hostname={new_name}'",
                    shell=True
                )

                # GET TAILSCALE IP
                result = subprocess.run(
                    f"podman exec {new_name} tailscale ip -4",
                    shell=True,
                    capture_output=True,
                    text=True
                )

                tailscale_ip = result.stdout.strip()

                Container.objects.create(
                    name=new_name,
                    tailscale_ip=tailscale_ip
                )

                msg = "Container created and connected to Headscale"

            except Exception as e:
                msg = "Error creating container"

        # OTHER ACTIONS
        else:
            try:
                container = client.containers.get(container_name)
            except Exception:
                container = None

            if container:
                if action == "start":
                    container.start()
                elif action == "stop":
                    container.stop()
                elif action == "delete":
                    container.remove(force=True)
                    Container.objects.filter(name=container_name).delete()
                elif action == "pause":
                    container.pause()
                elif action == "unpause":
                    container.unpause()

    # DASHBOARD DATA

    containers = client.containers.list(all=True)

    container_data = []

    for c in containers:

        if c.name == "headscale":
            continue

        created_raw = c.attrs.get("Created")

        try:
            dt = datetime.fromisoformat(created_raw)
            formatted_date = dt.strftime("%d/%m/%Y")
            formatted_time = dt.strftime("%I:%M %p")
        except:
            formatted_date = "-"
            formatted_time = "-"

        container_data.append({
            "name": c.name,
            "id": c.id[:12],
            "status": c.attrs.get("State"),
            "date": formatted_date,
            "time": formatted_time,
            "timezone": "IST (+05:30)"
        })

    images = client.images.list()

    image_data = []

    for img in images:
        try:
            repo_tags = img.tags if img.tags else ["<none>"]
            size_mb = round(img.attrs.get("Size", 0) / (1024 * 1024), 2)

            image_data.append({
                "id": img.id[:12],
                "tags": ", ".join(repo_tags),
                "size": f"{size_mb} MB"
            })

        except Exception:
            pass

    return render(request, "containers/dashboard.html", {
        "containers": container_data,
        "images": image_data,
        "message": msg
    })


# TERMINAL + LOGS

def terminal_page(request):
    return render(request, "containers/terminal.html")


def logs_page(request, name):
    return render(request, "containers/logs.html", {
        "container_name": name
    })
