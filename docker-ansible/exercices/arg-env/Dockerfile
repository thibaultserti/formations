ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-alpine

ENV APP_PORT XXX

ENTRYPOINT [ "python3", "-m", "http.server", "${APP_PORT}" ]
