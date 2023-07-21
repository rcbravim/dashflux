FROM python:3.10-slim-buster

# create venv
ENV VIRTUAL_ENV=/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
COPY . .

RUN apt-get update -qq \
    && apt-get install -y locales-all \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# init database
RUN flask init-db

EXPOSE 5000

ENTRYPOINT ["gunicorn"]
CMD ["-c", "gunicorn_config.py", "wsgi:app"]