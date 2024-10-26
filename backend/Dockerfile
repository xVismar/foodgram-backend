FROM python:3.9

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir
RUN apt-get update
RUN apt-get install -y nano
RUN mkdir -p data/media_data/recipes/

COPY . .


CMD ["sh", "entrypoint.sh"]
