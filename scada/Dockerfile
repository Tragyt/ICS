FROM debian:trixie-slim

RUN apt-get update && apt-get install --no-install-recommends -y unzip=6.0-29 wget=1.25.0-2 derby-tools=10.14.2.0-3 netcat-openbsd=1.229-1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN wget -q -O ScadaBR_Setup_Linux.zip https://github.com/ScadaBR/ScadaBR/releases/download/v1.2/ScadaBR_Setup_Linux.zip \
    && unzip ScadaBR_Setup_Linux.zip -d ScadaBR

WORKDIR /tmp/ScadaBR
RUN chmod +x install_scadabr.sh remove_scadabr.sh \
    && ./install_scadabr.sh silent

EXPOSE 8080

WORKDIR /app
RUN rm -rf /tmp/ScadaBR

COPY backup/ /backup
RUN ij /backup/import.del

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]