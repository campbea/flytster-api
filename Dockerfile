FROM python:3.5
MAINTAINER Andrew Campbell

# install app dependencies
RUN apt-get update -qy && \
    apt-get install -y libpq-dev postgresql postgresql-contrib nginx

# install requirements here for caching
COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt && \
    groupadd -r django && \
    useradd -r -g django django

COPY . /app
WORKDIR /app/flytster

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "flytster.wsgi"]



# FROM python:3.5
#
# MAINTAINER Andrew Campbell
#
# RUN apt-get update -qy && \
#     apt-get install -y libpq-dev socat wget git python-psycopg2
#
# RUN mkdir /src
# COPY . /src
# RUN cd /src/ && pip install -r requirements.txt
# WORKDIR /src/flytster
#
# EXPOSE 8000
#
# CMD ["gunicorn", "-b", "0.0.0.0:8000", "flytster.wsgi"]
