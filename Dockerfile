FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=1

RUN apt-get update && apt-get install -y \
    portaudio19-dev cmake pkg-config git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY src/realtime_translate_system /app/realtime_translate_system

ENV FLASK_APP=realtime_translate_system.app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

CMD ["flask", "run"]
