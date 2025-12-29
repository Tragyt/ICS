FROM debian:trixie-slim

WORKDIR /home/openplc

RUN apt update && apt install -y git sudo netcat-traditional python3-pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

RUN git clone https://github.com/thiagoralves/OpenPLC_v3.git
WORKDIR /home/openplc/OpenPLC_v3
RUN ./install.sh docker 

COPY ./arm_plc.st /home/openplc/scripts/
COPY setup.sh /home/openplc
COPY start_plc.py /home/openplc
COPY run.sh /home/openplc

RUN sudo chmod +x /home/openplc/setup.sh
RUN /home/openplc/setup.sh

RUN sudo chmod +x /home/openplc/run.sh
CMD ["/home/openplc/run.sh"]