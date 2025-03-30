# Docker Computer Use Agent Starter

OpenAI's computer use works doesn't work with *just* screenshots from Playwright because screenshots from Playwright don't include select options, alerts, etc. So to reliably use computer use, you need to be able to see the entire screen.

This repo contains a Docker image that runs a full desktop environment with VNC access and Chrome CDP enabled. It also contains a simple Python API that is designed to work with OpenAI's Computer Use Agent tool call function types.

Use this as a starting point for your own computer use agent, where you can use Computer Use to control the entire Ubuntu desktop, and Playwright to control the browser programmatically.

## Features

- Zero dependencies
- Ubuntu 24.04 base with XFCE desktop environment
- Chrome browser with CDP enabled
- VNC server for remote viewing
- Python API for browser automation
- Support for multiple concurrent instances

## Quick Start

Build the Docker image:

```bash
docker build -t cua-env .
```

Use the Python API [computer.py](docker/computer.py):

```python
with DockerComputer() as computer:
    # computer automation commands
    computer.type("Hello World")
    computer.click(100, 100)
    computer.screenshot()  # Returns base64 PNG

    # Control the browser with Playwright
    browser = playwright.chromium.connect_over_cdp(
        computer.chrome_cdp_endpoint_url
    )
```

## Ports

- VNC: 5900 + id (default = 0)
- Chrome CDP: 9222 + id (default = 0)

For multiple instances, you can pass an `id` argument to the `DockerComputer` constructor. This increments the port numbers by that amount.

```python
with DockerComputer(id=1) as computer:
    # VNC: 5901
    # Chrome CDP: 9223

    # computer automation commands
    computer.type("Hello World")
    computer.click(100, 100)
    computer.screenshot()  # Returns base64 PNG

    # Control the browser with Playwright
    browser = playwright.chromium.connect_over_cdp(
        computer.chrome_cdp_endpoint_url
    )


with DockerComputer(id=2) as computer:
    # VNC: 5902
    # Chrome CDP: 9224

    # computer automation commands
    computer.type("Hello World")
    computer.click(100, 100)
    computer.screenshot()  # Returns base64 PNG

    # Control the browser with Playwright
    browser = playwright.chromium.connect_over_cdp(
        computer.chrome_cdp_endpoint_url
    )
```

## Available Methods

Methods are compatible with the OpenAI Computer Use Agent tool call function types.

- `click(x, y, button="left")` - Click at coordinates
- `double_click(x, y)` - Double click at coordinates
- `type(text)` - Type text
- `move(x, y)` - Move mouse to coordinates
- `scroll(x, y, scroll_x, scroll_y)` - Scroll at coordinates
- `keypress(keys)` - Press keyboard keys
- `drag(path)` - Drag mouse along path
- `screenshot()` - Take screenshot (returns base64 PNG)
- `wait(ms=1000)` - Wait specified milliseconds

## Resource Limits

- Memory: 2GB per container
- Display: 1280x720

## Acknowledgements

OpenAI's own [CUA Sample App](https://github.com/openai/openai-cua-sample-app) was used as a starting point for the `docker/computer.py` file.
