FROM python:3.9-alpine3.13
LABEL maintainer="nalu.com"

ENV PYTHONBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY . /app
copy ./scripts /scripts


WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-deps \
        build-base postgresql-dev musl-dev linux-headers && \
    /py/bin/pip install -r requirements.txt && \
    apk del .tmp-deps && \
    adduser --disabled-password --no-create-home app && \
    mkdir -p /app/staticfiles && \
    chown -R app:app /app/staticfiles && \
    chmod -R 755 /app/staticfiles && \
    mkdir -p /app/media && \
    chown -R app:app /app/media && \
    chmod -R 755 /app/media && \
    chmod -R +x /scripts 


ENV PATH="/scripts:/py/bin:$PATH"

USER app

CMD ["run.sh"]
