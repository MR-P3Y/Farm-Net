FROM python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

WORKDIR /build

RUN python -m venv "${VIRTUAL_ENV}"

COPY pyproject.toml ./
COPY requirements.lock ./
COPY app ./app

RUN pip install pip==26.1.2 \
    && pip install --requirement requirements.lock \
    && pip install --no-deps .


FROM python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

RUN groupadd --gid 10001 farmnet \
    && useradd --uid 10001 --gid farmnet --no-create-home --shell /usr/sbin/nologin farmnet \
    && mkdir -p /app /srv/farmnet/media \
    && chown -R farmnet:farmnet /app /srv/farmnet

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=farmnet:farmnet alembic.ini ./
COPY --chown=farmnet:farmnet alembic ./alembic
COPY --chown=farmnet:farmnet app ./app
COPY --chown=farmnet:farmnet scripts ./scripts

USER 10001:10001

EXPOSE 8000
STOPSIGNAL SIGTERM

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/ready', timeout=3).read()"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-proxy-headers"]
