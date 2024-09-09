FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY ./data ./data
COPY ./test ./test
COPY README.md .
COPY .env .

EXPOSE 5000

RUN pytest

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

CMD ["streamlit", "run", "src/app.py", "--server.port=5000", "--server.headless=true"]
