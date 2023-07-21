FROM python:3.10-slim-buster
WORKDIR /app
COPY . .

RUN apt-get update -qq \
    && apt-get install -y locales-all \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# database
RUN flask init-db

EXPOSE 5000

ENTRYPOINT ["gunicorn"]
CMD ["-c", "gunicorn_config.py", "wsgi:app"]