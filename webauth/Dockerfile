FROM python:3.13

EXPOSE 5000

RUN apt-get update && apt-get install -y postgresql-client

WORKDIR /app

COPY ./webauth/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./webauth/entrypoint.sh /tmp/entrypoint.sh
RUN chmod +x /tmp/entrypoint.sh

ENTRYPOINT ["sh", "/tmp/entrypoint.sh"]