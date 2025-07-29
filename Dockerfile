FROM python:3.10

WORKDIR /usr/src/app

COPY . .

RUN pip install .

ENTRYPOINT ["/bin/bash", "docker_run.sh"]
