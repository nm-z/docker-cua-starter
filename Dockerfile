FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
  apt-get install -y \
  xfce4 \
  xfce4-goodies \
  x11vnc \
  xvfb \
  xdotool \
  imagemagick \
  sudo \
  software-properties-common \
  imagemagick \
  wget \
  gnupg2

RUN apt-get install -y \
  socat \
  dbus \
  dbus-x11

RUN apt-get remove -y light-locker xfce4-screensaver xfce4-power-manager || true

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# 4) Create launch script for Chrome with CDP
COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# 5) Create non-root user
RUN useradd -ms /bin/bash myuser \
  && echo "myuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
  && usermod -a -G messagebus myuser
USER myuser
WORKDIR /home/myuser

# 6) Set x11vnc password ("secret")
RUN x11vnc -storepasswd secret /home/myuser/.vncpass

ENV VNC_PORT=5900

# 7) Expose port 5900 and run Xvfb, x11vnc, Xfce (no login manager)
EXPOSE ${VNC_PORT}
CMD ["/bin/sh", "-c", "  Xvfb :99 -screen 0 1280x800x24 >/dev/null 2>&1 &   while ! xdpyinfo -display :99 >/dev/null 2>&1; do sleep 0.1; done &&   xpra start :1 --bind-tcp=0.0.0.0:14500 --html=on --auth=env --env=XPRA_PASSWORD=$XPRA_PASSWORD >/dev/null 2>&1 &   export DISPLAY=:99 &&   startxfce4 >/dev/null 2>&1 &   tail -f /dev/null"]
