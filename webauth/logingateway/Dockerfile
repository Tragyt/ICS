FROM python:3.13

EXPOSE 5000

RUN apt-get update && apt-get install --no-install-recommends -y postgresql-client=17+278 sudo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./webauth/logingateway/app ./logingateway/app
COPY ./webauth/common/templates/ ./logingateway/app/templates/
COPY ./webauth/common/*.py ./logingateway/common/ 

COPY ./webauth/logingateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./webauth/logingateway/entrypoint.sh /tmp/entrypoint.sh
RUN sudo chmod +x /tmp/entrypoint.sh

WORKDIR /app/logingateway/app/
ENTRYPOINT ["sh", "/tmp/entrypoint.sh"]