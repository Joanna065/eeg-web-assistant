FROM python:3.8

WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:${pwd}"

COPY ./ ./

RUN mkdir -p .storage/logs/
RUN pip install -e .

CMD ["/bin/bash", "-c"]
