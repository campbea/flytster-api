FROM python:3

RUN apt-get update \
    && apt-get upgrade -y

RUN apt-get install -y python-psycopg2

RUN mkdir /src
COPY . /src/
RUN cd /src/ && pip3 install -r requirements.txt
WORKDIR /src/flytster

CMD ["gunicorn", "-b", "0.0.0.0:8000", "flytster.wsgi"]

# CMD ["sh", "../deploy/start.sh"]

EXPOSE 8000
