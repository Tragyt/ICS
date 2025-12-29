FROM debian:trixie-slim

RUN apt update && apt install -y unzip wget derby-tools netcat-openbsd

WORKDIR /tmp
RUN wget -O ScadaBR_Setup_Linux.zip https://github.com/ScadaBR/ScadaBR/releases/download/v1.2/ScadaBR_Setup_Linux.zip
RUN unzip ScadaBR_Setup_Linux.zip -d ScadaBR

WORKDIR /tmp/ScadaBR
RUN chmod +x install_scadabr.sh remove_scadabr.sh
RUN ./install_scadabr.sh silent

EXPOSE 8080

WORKDIR /app
RUN rm -rf /tmp/ScadaBR

COPY backup/ /backup
RUN ij /backup/import.del

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]