FROM python:3.10-alpine3.16

WORKDIR /app
RUN apk add --no-cache gcc musl-dev
RUN python -m pip install --upgrade pip

RUN pip3 install web3

COPY app.py .
COPY allowlist .
RUN chown nobody allowlist
USER nobody
EXPOSE 80

ENTRYPOINT ["python3", "-u", "./app.py"]
