FROM python:3.13

EXPOSE 5000

RUN apt-get update && apt-get install -y postgresql-client

WORKDIR /app

COPY ./webauth/logingateway/app ./logingateway/app
COPY ./webauth/common/templates/ ./logingateway/app/templates/
COPY ./webauth/common/*.py ./logingateway/common/ 

COPY ./webauth/logingateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./webauth/logingateway/entrypoint.sh /tmp/entrypoint.sh
RUN chmod +x /tmp/entrypoint.sh

WORKDIR /app/logingateway/app/
ENTRYPOINT ["sh", "/tmp/entrypoint.sh"]