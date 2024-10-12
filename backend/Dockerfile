# FROM python:3.9

# WORKDIR /app

# RUN pip install --upgrade pip

# COPY requirements.txt .

# RUN pip install -r requirements.txt --no-cache-dir

# COPY . .

# # CMD ["gunicorn", "--bind", "0.0.0.0:8080", "foodgram_backend.wsgi"]
# CMD ["sh", "entrypoint.sh"]


FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

COPY ../data/ ../data
COPY backend/ .

CMD ["sh", "entrypoint.sh"]