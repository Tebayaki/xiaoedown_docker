FROM python:3.10-alpine

WORKDIR /app/

COPY main.py requirements.txt /app/

RUN pip install -r requirements.txt && \
    rm requirements.txt && \
    apk update && \
    apk add --no-cache ffmpeg

ENTRYPOINT [ "python", "main.py" ]

