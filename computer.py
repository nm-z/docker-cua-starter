import subprocess
import time
import urllib.error
import urllib.request

PORTS: dict[str, int] = {"vnc": 5900}

class DockerComputer:
    environment = "linux"

    def __init__(
        self,
        image="cua-env",
        id: int = 0,
        mem: str = "2G",
    ):
        self.image = image
        self.container_name = f"cua-env-{id}"
        self.display = ":99"
        self.vnc_port = PORTS["vnc"] + id
        self.mem = mem
        self._was_running = False

    def __enter__(self):
        is_running = bool(
            subprocess.run(
                ["docker", "ps", "-q", "-f", f"name={self.container_name}"],
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        self._was_running = is_running

        if not is_running:
            print("Starting Docker container...")
            vnc_port = self.vnc_port
            subprocess.check_call(
                [
                    "docker",
                    "run",
                    "-d",
                    "-m",
                    self.mem,
                    "--rm",
                    "--name",
                    self.container_name,
                    "-p",
                    f"{vnc_port}:{vnc_port}",
                    "-e",
                    f"VNC_PORT={vnc_port}",
                    "-e",
                    f"DISPLAY={self.display}",
                    self.image,
                ]
            )
            print("Waiting for docker desktop env to be ready...")
            time.sleep(5)

        print("Entering docker context")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"Error: {exc_val}")
            print(f"Traceback:\n{exc_tb}")

        if not self._was_running:
            print("Stopping docker container...")
            subprocess.check_call(["docker", "stop", self.container_name])
        print("Exiting docker context")

    def _exec(self, cmd: str) -> str:
        safe_cmd = cmd.replace('"', '\"')
        docker_cmd = f'docker exec {self.container_name} sh -c "{safe_cmd}"'
        return subprocess.check_output(docker_cmd, shell=True).decode(
            "utf-8", errors="ignore"
        )

    def screenshot(self) -> str:
        cmd = (
            f"export DISPLAY={self.display} && "
            "import -window root png:- | base64 -w 0"
        )
        return self._exec(cmd)

    def click(self, x: int, y: int, button: str = "left") -> None:
        button_map = {"left": 1, "middle": 2, "right": 3}
        b = button_map.get(button, 1)
        self._exec(f"DISPLAY={self.display} xdotool mousemove {x} {y} click {b}")

    def double_click(self, x: int, y: int) -> None:
        self._exec(
            f"DISPLAY={self.display} xdotool mousemove {x} {y} click --repeat 2 1"
        )

    def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        self._exec(f"DISPLAY={self.display} xdotool mousemove {x} {y}")
        clicks = abs(scroll_y)
        button = 4 if scroll_y < 0 else 5
        for _ in range(clicks):
            self._exec(f"DISPLAY={self.display} xdotool click {button}")

    def type(self, text: str) -> None:
        safe_text = text.replace("'", "'\\''")
        cmd = f"DISPLAY={self.display} xdotool type -- '{safe_text}'"
        self._exec(cmd)

    def wait(self, ms: int = 1000) -> None:
        time.sleep(ms / 1000)

    def move(self, x: int, y: int) -> None:
        self._exec(f"DISPLAY={self.display} xdotool mousemove {x} {y}")

    def keypress(self, keys: list[str]) -> None:
        mapping = {
            "ENTER": "Return",
            "LEFT": "Left",
            "RIGHT": "Right",
            "UP": "Up",
            "DOWN": "Down",
            "ESC": "Escape",
            "SPACE": "space",
            "BACKSPACE": "BackSpace",
            "TAB": "Tab",
        }
        mapped_keys = [mapping.get(key, key) for key in keys]
        combo = "+".join(mapped_keys)
        self._exec(f"DISPLAY={self.display} xdotool key {combo}")

    def drag(self, path: list[dict[str, int]]) -> None:
        if not path:
            return

        start = path[0]
        self._exec(
            f"DISPLAY={self.display} xdotool mousemove {start['x']} {start['y']} mousedown 1"
        )
        for step in path[1:]:
            self._exec(
                f"DISPLAY={self.display} xdotool mousemove {step['x']} {step['y']}"
            )
        self._exec(f"DISPLAY={self.display} xdotool mouseup 1")
