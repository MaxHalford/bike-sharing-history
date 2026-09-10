FROM python:3.13-slim

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ca-certificates git openssh-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt

COPY scrape ./scrape
COPY deploy ./deploy
COPY scripts ./scripts

CMD ["python", "scrape/scrape_city_branches.py", "--list-cities"]
