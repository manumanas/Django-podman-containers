from django.http import HttpResponse
import podman
from django.shortcuts import render
from datetime import datetime
import re
import subprocess
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import time
from .models import Container
from django.conf import settings

HOST_PUBLIC_KEY = settings.HOST_PUBLIC_KEY
HOST_ENDPOINT = settings.HOST_ENDPOINT


import os

def enable_autostart(container_name):

    service_dir = os.path.expanduser("~/.config/systemd/user")

    # create systemd folder
    subprocess.run(
        f"mkdir -p {service_dir}",
        shell=True
    )

    # generate systemd file
    subprocess.run(
        f"podman generate systemd --name {container_name} --files",
        shell=True
    )

    # move service file
    subprocess.run(
        f"mv container-{container_name}.service {service_dir}/",
        shell=True
    )

    # reload systemd
    subprocess.run(
        "systemctl --user daemon-reexec",
        shell=True
    )

    subprocess.run(
        "systemctl --user daemon-reload",
        shell=True
    )

    # enable autostart
    subprocess.run(
        f"systemctl --user enable container-{container_name}.service",
        shell=True
    )

    # allow boot start (runs once, safe if repeated)
    subprocess.run(
        "loginctl enable-linger $USER",
        shell=True
    )


client = podman.PodmanClient(
    base_url="unix:///run/user/1000/podman/podman.sock"
)


def home(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    signin_error = ""
    signup_error = ""

    if request.method == "POST":

        action = request.POST.get("action")

        username = request.POST.get("username")
        password = request.POST.get("password")

        # ---------- SIGN IN ----------
        if action == "signin":

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect("dashboard")

            # user not found
            if not User.objects.filter(username=username).exists():
                signin_error = "Account not found. Please sign up."

            else:
                signin_error = "Invalid password."

        # ---------- SIGN UP ----------
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


def get_container_logs(container_name):
    try:
        result = subprocess.run(
            ["podman", "logs", container_name],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return str(e)

@login_required(login_url="home")
def dashboard(request):
    logs = None
    msg = ""

    if request.method == "POST":
        container_name = request.POST.get("name")
        action = request.POST.get("action")

        # 1. Only try to create if the action is actually 'create'
        if action == "create":
            new_name = request.POST.get("new_name")
            try:
                client.containers.run(
                    "ubuntu-systemd",   # your custom image
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
                setup_wireguard(new_name)
                
                time.sleep(3)

                # connect_peers(new_name)

                msg = "Container created and started"
            except Exception:
                msg = "Container name already exists or error occurred"

        # 2. For all other actions, find the existing container
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

                    try:
                        record = Container.objects.get(name=container_name)
                        record.delete()

                        rebuild_host_wg_config()

                    except Container.DoesNotExist:
                        pass
                elif action == "pause":
                    container.pause()
                elif action == "unpause":
                    container.unpause()
                # elif action == "logs":
                #     raw_logs = " ".join(line.decode() if isinstance(line, bytes) else str(line)
                #         for line in container.logs()
                #     )
                #     logs = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '' ,raw_logs)


        #dashboard ui purpose in dashmoard.html in templates
    containers = client.containers.list(all=True)

    container_data = []
    for c in containers:
        created_raw = c.attrs.get("Created")
        # Handle potential parsing errors safely
        try:
            dt = datetime.fromisoformat(created_raw) # or handle 'Z' if needed
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


    #dashboard ui purpose in dashmoard.html in templates

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
        # "logs": logs,
        "images": image_data,
        "message": msg
    })

def terminal_page(request):
    return render(request, "containers/terminal.html")

def logs_page(request, name):
    return render(request, "containers/logs.html", {
        "container_name": name
    })

def setup_wireguard(new_name):
    ip = get_next_ip()
    subprocess.run(f"podman exec {new_name} mkdir -p /etc/wireguard", shell=True)

    subprocess.run(
        f"podman exec {new_name} bash -c 'wg genkey | tee /etc/wireguard/privatekey'",
        shell=True
    )

    subprocess.run(
        f"podman exec {new_name} bash -c 'cat /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey'",
        shell=True
    )

    result = subprocess.run(
        f"podman exec {new_name} cat /etc/wireguard/privatekey",
        shell=True,
        capture_output=True,
        text=True
    )

    private_key = result.stdout.strip()

    config = f"""
            [Interface]
            Address = {ip}/24
            ListenPort = 51820
            PrivateKey = {private_key}

            [Peer]
            PublicKey = {HOST_PUBLIC_KEY}
            AllowedIPs = 10.10.0.0/24
            Endpoint = {HOST_ENDPOINT}
            PersistentKeepalive = 25
            """
    

    pub_result = subprocess.check_output(          #publickey
    f"podman exec {new_name} cat /etc/wireguard/publickey",
    shell=True,
    text=True
    ).strip()

    # save to DB
    Container.objects.create(
        name=new_name,
        wireguard_ip=ip,
        public_key=pub_result
    )

    subprocess.run(
        f"podman exec {new_name} bash -c \"echo '{config}' > /etc/wireguard/wg0.conf\"",
        shell=True
    )
    subprocess.run(
    f"podman exec {new_name} bash -c \"echo {ip} > /etc/wireguard/ip.txt\"",
    shell=True
)

    # START WIREGUARD
    subprocess.run(
        f"podman exec {new_name} wg-quick up wg0",
        shell=True

    ) 

    add_peer_to_host(new_name, ip)


HOST_WG_CONF = "/etc/wireguard/wg0.conf"
WG_INTERFACE = "wg0"

HOST_PRIVATE_KEY = settings.HOST_PRIVATE_KEY

def rebuild_host_wg_config():

    interface_block = f"""
[Interface]
Address = 10.10.0.1/24
ListenPort = 51820
PrivateKey = {HOST_PRIVATE_KEY}
"""

    peer_blocks = ""

    containers = Container.objects.all()

    for c in containers:
        peer_blocks += f"""
[Peer]
PublicKey = {c.public_key}
AllowedIPs = {c.wireguard_ip}/32
"""

    full_config = interface_block + peer_blocks

    # write config
    subprocess.run(
        f"sudo bash -c \"echo '{full_config}' > {HOST_WG_CONF}\"",
        shell=True
    )

    # restart WG
    subprocess.run(f"sudo wg-quick down {WG_INTERFACE}", shell=True)
    subprocess.run(f"sudo wg-quick up {WG_INTERFACE}", shell=True)

def add_peer_to_host(new_name, ip):
    rebuild_host_wg_config()

#ip generation

def get_next_ip():
    used_ips = Container.objects.values_list("wireguard_ip", flat=True)

    base = "10.10.0."
    for i in range(2, 255):
        candidate = base + str(i)
        if candidate not in used_ips:
            return candidate

    raise Exception("No IPs available")



# def get_next_ip():
#     client = podman.PodmanClient(
#         base_url="unix:///run/user/1000/podman/podman.sock"
#     )

#     containers = client.containers.list(all=True)

#     base_ip = 2 + len(containers)

#     return f"10.10.0.{base_ip}"

# def connect_peers(new_name):

#     # print("CONNECT PEERS CALLED:", new_container)

#     containers = subprocess.check_output(
#         "podman ps --format '{{.Names}}'",
#         shell=True,
#         text=True
#     ).splitlines()

#     # get new container data
#     try:
#         new_pub = subprocess.check_output(
#             f"podman exec {new_name} cat /etc/wireguard/publickey",
#             shell=True,
#             text=True
#         ).strip()

#         new_ip = subprocess.check_output(
#             f"podman exec {new_name} cat /etc/wireguard/ip.txt",
#             shell=True,
#             text=True
#         ).strip()
#     except:
#         print("New container not ready")
#         return

#     for name in containers:

#         if name == new_name:
#             continue

#         # check if container has wireguard
#         check = subprocess.run(
#             f"podman exec {name} test -f /etc/wireguard/publickey",
#             shell=True
#         )

#         if check.returncode != 0:
#             continue   # skip non-WG containers

#         try:
#             old_pub = subprocess.check_output(
#                 f"podman exec {name} cat /etc/wireguard/publickey",
#                 shell=True,
#                 text=True
#             ).strip()

#             old_ip = subprocess.check_output(
#                 f"podman exec {name} cat /etc/wireguard/ip.txt",
#                 shell=True,
#                 text=True
#             ).strip()
#         except:
#             continue

#         # write peer both sides
#         subprocess.run(
#             f"""podman exec {name} bash -c "printf '\\n[Peer]\\nPublicKey = {new_pub}\\nAllowedIPs = {new_ip}/32\\n' >> /etc/wireguard/wg0.conf" """,
#             shell=True
#         )

#         subprocess.run(
#             f"""podman exec {new_name} bash -c "printf '\\n[Peer]\\nPublicKey = {old_pub}\\nAllowedIPs = {old_ip}/32\\n' >> /etc/wireguard/wg0.conf" """,
#             shell=True
#         )

#         subprocess.run(f"podman exec {name} wg-quick down wg0", shell=True)
#         subprocess.run(f"podman exec {name} wg-quick up wg0", shell=True)

#     subprocess.run(f"podman exec {new_name} wg-quick down wg0", shell=True)
#     subprocess.run(f"podman exec {new_name} wg-quick up wg0", shell=True)


