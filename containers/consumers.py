import asyncio
import os
import pty
import subprocess
import signal
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class TerminalConsumer(AsyncWebsocketConsumer):  #continues communications

    async def connect(self):
        self.container_name = self.scope["url_route"]["kwargs"]["name"]
        await self.accept()

        self.master_fd, self.slave_fd = pty.openpty()

        # IMPORTANT: remove -t
        self.process = subprocess.Popen(
            [
                "podman",
                "exec",
                "-it",
                self.container_name,
                "bash",
                "-i",
            ],  
            stdin=self.slave_fd,
            stdout=self.slave_fd,
            stderr=self.slave_fd,
            preexec_fn=os.setsid,
        )

        os.close(self.slave_fd)

        await asyncio.sleep(0.2)

        os.write(
            self.master_fd,
            f'export PS1="root@{self.container_name}:\\w# "\n'.encode()
        )

        self.read_task = asyncio.create_task(self.read_pty())

    async def disconnect(self, close_code):
        try:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
        except:
            pass

        try:
            os.close(self.master_fd)
        except:
            pass

        if hasattr(self, "read_task"):
            self.read_task.cancel()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            if "input" in data:
                os.write(self.master_fd, data["input"].encode())

    async def read_pty(self):
        loop = asyncio.get_running_loop()

        while True:
            try:
                data = await loop.run_in_executor(
                    None,
                    os.read,
                    self.master_fd,
                    1024
                )

                if data:
                    await self.send(bytes_data=data)

            except Exception:
                break



class LogsConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.container_name = self.scope["url_route"]["kwargs"]["name"]
        await self.accept()

        loop = asyncio.get_running_loop()

        # -------- SEND FULL LOGS INSTANTLY --------
        history = await loop.run_in_executor(
            None,
            lambda: subprocess.check_output(
                ["podman", "logs", self.container_name],
                text=True
            )
        )

        await self.send(text_data=history)

        # -------- NOW STREAM ONLY NEW LOGS --------
        self.process = subprocess.Popen(
            ["podman", "logs", "-f", "--since", "1s", self.container_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        asyncio.create_task(self.stream_logs())

    async def disconnect(self, close_code):
        if hasattr(self, "process"):
            self.process.kill()

    async def stream_logs(self):
        loop = asyncio.get_running_loop()

        while True:
            line = await loop.run_in_executor(
                None,
                self.process.stdout.readline
            )

            if not line:
                break

            await self.send(text_data=line)



class StatusConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

        self.task = asyncio.create_task(self.send_status_loop())

    async def disconnect(self, close_code):
        if hasattr(self, "task"):
            self.task.cancel()

    async def send_status_loop(self):
        import podman

        client = podman.PodmanClient(
            base_url="unix:///run/user/1000/podman/podman.sock"
        )

        while True:
            containers = client.containers.list(all=True)

            data = []

            for c in containers:
                data.append({
                    "name": c.name,
                    "status": c.status
                })

            await self.send(text_data=json.dumps(data))

            await asyncio.sleep(2)   # update every 2 seconds
