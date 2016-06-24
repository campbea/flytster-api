FROM python:3.5

MAINTAINER Andrew Campbell

RUN apt-get update -qy && \
    apt-get install -y libpq-dev socat wget git python-psycopg2

RUN mkdir /src
COPY . /src
RUN cd /src/ && pip install -r requirements.txt
WORKDIR /src/flytster

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "flytster.wsgi"]
