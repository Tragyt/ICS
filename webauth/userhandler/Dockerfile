FROM python:3.13

EXPOSE 5000

RUN apt-get update && apt-get install -y postgresql-client

WORKDIR /app

COPY ./webauth/userhandler/app ./userhandler/app
COPY ./webauth/common/templates/ ./userhandler/app/templates/
COPY ./webauth/common/*.py ./userhandler/common/ 

COPY ./webauth/userhandler/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./webauth/userhandler/entrypoint.sh /tmp/entrypoint.sh
RUN chmod +x /tmp/entrypoint.sh

WORKDIR /app/userhandler/app/
ENTRYPOINT ["sh", "/tmp/entrypoint.sh"]