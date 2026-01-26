FROM debian:trixie-slim

WORKDIR /home/openplc

RUN apt-get update && apt-get install --no-install-recommends -y git=1:2.47.3-0+deb13u1 netcat-traditional=1.10-50 python3-pip=25.1.1+dfsg-1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages \
    && git clone https://github.com/thiagoralves/OpenPLC_v3.git

WORKDIR /home/openplc/OpenPLC_v3
RUN ./install.sh docker 

COPY ./arm_plc.st /home/openplc/scripts/
COPY setup.sh /home/openplc
COPY start_plc.py /home/openplc
COPY run.sh /home/openplc

RUN chmod +x /home/openplc/setup.sh \
    && /home/openplc/setup.sh \
    && chmod +x /home/openplc/run.sh 
CMD ["/home/openplc/run.sh"]