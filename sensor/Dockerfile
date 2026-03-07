FROM debian:trixie-slim

WORKDIR /home/sensor

RUN apt-get update && apt-get install --no-install-recommends -y python3-rpi.gpio \
    && rm -rf /var/lib/apt/lists/* 

COPY sensor.py .
CMD ["python3","/home/sensor/sensor.py"]