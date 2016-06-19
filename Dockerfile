FROM ubuntu:16.04

MAINTAINER Andrew Campbell

RUN apt-get update -qy && apt-get install -y wget
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt-get update -qy
RUN apt-get install -y python3 python3-dev python3-pip gcc
RUN apt-get install -y postgresql python-psycopg2 libpq-dev

RUN mkdir /src
COPY . /src
RUN cd /src/ && pip3 install -r requirements.txt
WORKDIR /src/flytster

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "flytster.wsgi"]
