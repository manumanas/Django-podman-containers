# from django.shortcuts import render

# # Create your views here.
# from django.http import HttpResponse
# import podman

# client = podman.PodmanClient(
#     base_url="unix:///run/user/1000/podman/podman.sock"
# )

# # def start_container(request):
# #     container = client.containers.run(
# #         "docker.io/library/ubuntu",
# #         command = "sleep infinity",
# #         detach=True,
# #         name="myubuntu"
# #     )
# #     return HttpResponse("Ubuntu container has started")

# # correct use of start by using exception handling:
# def start_container(request):
#     try:
#         container = client.containers.get("myubuntu")

#         if container.status != "running":
#             container.start()
#             msg = "Container started"
#         else:
#             msg = "Already running"

#     except:
#         container = client.containers.run(
#             "docker.io/library/ubuntu",
#             command=["sleep", "999999"],
#             detach=True,
#             name="myubuntu"
#         )
#         msg = "Container created and started"

#     return HttpResponse(msg)

# def stop_container(request):
#     container = client.containers.get("myubuntu")
#     container.stop()
#     return HttpResponse("Stopped")


# def kill_container(request):
#     container = client.containers.get("myubuntu")
#     container.kill()
#     return HttpResponse("Killed")

# def list_containers(request):
#     containers = client.containers.list()
#     names = [c.name for c in containers]
#     return HttpResponse("<br>".join(names))

# def remove_container(request):
#     container = client.containers.get("myubuntu")
#     container.remove(force=True)
#     return HttpResponse("Container removed")

# def home(request):
#     return HttpResponse("Containers Home Page")
#----------------------------------------------------------------------------------

# from django.shortcuts import render
# from django.http import HttpResponse
# import podman
# from podman.errors import NotFound

# client = podman.PodmanClient(
#     base_url="unix:///run/user/1000/podman/podman.sock"
# )

# def start_container(request):
#     try:
#         container = client.containers.get("myubuntu")

#         if container.status != "running":
#             container.start()
#             msg = "Container started"
#         else:
#             msg = "Already running"

#     except NotFound:
#         client.containers.run(
#             "docker.io/library/ubuntu",
#             command=["sleep", "999999"],
#             detach=True,
#             name="myubuntu"
#         )
#         msg = "Container created and started"

#     return HttpResponse(msg)


# def stop_container(request):
#     try:
#         container = client.containers.get("myubuntu")
#         container.stop()
#         return HttpResponse("Stopped")
#     except NotFound:
#         return HttpResponse("Container does not exist")


# def kill_container(request):
#     try:
#         container = client.containers.get("myubuntu")
#         container.kill()
#         return HttpResponse("Killed")
#     except NotFound:
#         return HttpResponse("Container does not exist")


# def remove_container(request):
#     try:
#         container = client.containers.get("myubuntu")
#         container.remove(force=True)
#         return HttpResponse("Container removed")
#     except NotFound:
#         return HttpResponse("Container does not exist")


# def list_containers(request):
#     containers = client.containers.list(all=True)

#     output = ""
#     for c in containers:
#         output += f"{c.name} - {c.status}<br>"

#     return HttpResponse(output)


# def home(request):
#     return HttpResponse("Containers Home Page")
# #-----------------------------------------------------------------------------------



# def dashboard(request):
#     logs = None

#     if request.method == "POST":
#         action = request.POST.get("action")

#         try:
#             container = client.containers.get("myubuntu")
#         except Exception:
#             container = None

#         if action == "start":
#             if container:
#                 if container.status != "running":
#                     container.start()
#             else:
#                 client.containers.run(
#                     "docker.io/library/ubuntu",
#                     command=["sleep", "999999"],
#                     detach=True,
#                     name="myubuntu"
#                 )

#         elif action == "stop" and container:
#             container.stop()

#         elif action == "delete" and container:
#             container.remove(force=True)

#         elif action == "logs" and container:
#             logs = container.logs().decode()

#     containers = client.containers.list(all=True)

#     container_data = []
#     for c in containers:
#         container_data.append({
#         "name": c.name,
#         "status": c.attrs.get("State"),
#         "created": c.attrs.get("Created")
# })


#     return render(request, "containers/dashboard.html", {
#         "containers": container_data,
#         "logs": logs
#     })











#------------------------------------------------------------------------------
# from django.http import HttpResponse
# import podman
# from django.shortcuts import render
# from datetime import datetime
# import re

# client = podman.PodmanClient(
#     base_url="unix:///run/user/1000/podman/podman.sock"
# )
# def dashboard(request):
#     logs = None

#     if request.method == "POST":
#         container_name = request.POST.get("name")
#         action = request.POST.get("action")

#         if action == "create":
#             new_name = request.POST.get("new_name")

#         try:
#             client.containers.run(
#             "docker.io/library/ubuntu",
#             command=["bash"],
#             detach=True,
#             tty=True,
#             stdin_open=True,
#             name=new_name)
            
#             msg = "Container created and started"

#         except Exception:
#              msg = "Container name already exists"

#         try:
#             container = client.containers.get(container_name)
#         except Exception:
#             container = None

#         if container:
#             if action == "start":
#                 container.start()

#             elif action == "stop":
#                 container.stop()

#             elif action == "delete":
#                 container.remove(force=True)

#             elif action == "logs":
#                 raw_logs = " ".join(line.decode() if isinstance(line, bytes) else str(line)
#                     for line in container.logs()
#                 )
#                 # remove ANSI escape sequences
#                 logs = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '' ,raw_logs)

#                 # remove OSC sequences (window title codes)
#                 # logs = re.sub(r'\x1B\].*?\x07', '', logs)

#             elif action == "pause" and container:
#                 container.pause()

#             elif action == "unpause" and container:
#                  container.unpause()


#     containers = client.containers.list(all = True)

#     container_data = []
#     for c in containers:
#         created_raw = c.attrs.get("Created")

#         dt = datetime.fromisoformat(created_raw)

#         formatted_date = dt.strftime("%d/%m/%Y")
#         formatted_time = dt.strftime("%I:%M %p")

#         container_data.append({
#             "name": c.name,
#             "status": c.attrs.get("State"),
#             "date": formatted_date,
#             "time": formatted_time,
#             "timezone": "IST (+05:30)"
#         })


#     return render(request, "containers/dashboard.html", {
#         "containers": container_data,
#         "logs": logs
#     })

# def terminal_page(request):
#     return render(request, "containers/terminal.html")
#------------------------------------------------------------------------------


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


HOST_PUBLIC_KEY = "6cuKRk+7PQjrgLms8hRTrhNa7TiRoiZY3O5K4Jog41k="
HOST_ENDPOINT = "192.168.10.191:51820"


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
                elif action == "pause":
                    container.pause()
                elif action == "unpause":
                    container.unpause()
                # elif action == "logs":
                #     raw_logs = " ".join(line.decode() if isinstance(line, bytes) else str(line)
                #         for line in container.logs()
                #     )
                #     logs = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '' ,raw_logs)

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

def add_peer_to_host(new_name, ip):

    pub = subprocess.check_output(
        f"podman exec {new_name} cat /etc/wireguard/publickey",
        shell=True,
        text=True
    ).strip()

    peer_block = f"""
[Peer]
PublicKey = {pub}
AllowedIPs = {ip}/32
"""

    subprocess.run(
        f"sudo bash -c \"echo '{peer_block}' >> {HOST_WG_CONF}\"",
        shell=True
    )

    subprocess.run(f"sudo wg-quick down {WG_INTERFACE}", shell=True)
    subprocess.run(f"sudo wg-quick up {WG_INTERFACE}", shell=True)


#ip generation

def get_next_ip():
    client = podman.PodmanClient(
        base_url="unix:///run/user/1000/podman/podman.sock"
    )

    containers = client.containers.list(all=True)

    base_ip = 2 + len(containers)

    return f"10.10.0.{base_ip}"

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


