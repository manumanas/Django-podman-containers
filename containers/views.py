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


client = podman.PodmanClient(
    base_url="unix:///run/user/1000/podman/podman.sock"
)

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
                    "docker.io/library/ubuntu",
                    command=["bash"],
                    detach=True,
                    tty=True,
                    stdin_open=True,
                    name=new_name
                )
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

    return render(request, "containers/dashboard.html", {
        "containers": container_data,
        # "logs": logs,
        "message": msg
    })

def terminal_page(request):
    return render(request, "containers/terminal.html")

def logs_page(request, name):
    return render(request, "containers/logs.html", {
        "container_name": name
    })




