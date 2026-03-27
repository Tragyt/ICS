FROM python:3.13

EXPOSE 5000

RUN apt-get update && apt-get install --no-install-recommends -y postgresql-client=17+278 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./app ./logingateway/app
COPY ./common/templates/ ./logingateway/app/templates/
COPY ./common/*.py ./logingateway/common/ 

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./entrypoint.sh /tmp/entrypoint.sh
RUN chmod +x /tmp/entrypoint.sh

WORKDIR /app/logingateway/app/
ENTRYPOINT ["sh", "/tmp/entrypoint.sh"]