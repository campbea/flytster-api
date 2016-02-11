FROM python:3

RUN apt-get update  && \
    apt-get -y install gettext postgresql-client libpq-dev --no-install-recommends

RUN mkdir /src
COPY . /src/
RUN cd /src/ && pip3 install -r requirements.txt
WORKDIR /src/flytster
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "flytster.wsgi"]
