FROM python:alpine3.6

WORKDIR /app

COPY ./requirements.txt /app

RUN apk update && \
    apk add --no-cache --virtual build-deps gcc python3-dev musl-dev jpeg-dev zlib-dev libffi-dev && \
    apk add --no-cache postgresql-dev &&  pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del build-deps

COPY ./ /app

ENTRYPOINT ["python", "src/app.py"]