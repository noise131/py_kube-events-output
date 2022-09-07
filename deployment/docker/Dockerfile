FROM docker.io/library/python:3.10.5-alpine3.15

COPY ./ /kube-events-output

WORKDIR /kube-events-output

RUN set -uex; \
        pip3 install -r requirements.txt;

CMD [ "python3", "main.py" ]
