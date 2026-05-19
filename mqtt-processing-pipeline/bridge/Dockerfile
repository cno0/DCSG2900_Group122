FROM python:3.14.4-slim-trixie

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

# Create a non-root user for running the Python application
RUN useradd --create-home --shell /bin/bash bridge

USER bridge

CMD ["python", "-m", "bridge"]

