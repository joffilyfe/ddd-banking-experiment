FROM python:3.7-alpine

COPY . /app
WORKDIR /app

RUN apk add --no-cache --virtual .build-deps \
        postgresql-libs make gcc musl-dev g++ postgresql-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm requirements.txt

ENV PYTHONUNBUFFERED 1

USER nobody
CMD ["uvicorn", "banking.api:app", "--host", "0.0.0.0"]
