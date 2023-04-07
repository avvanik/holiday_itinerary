FROM python:3.9

WORKDIR /code

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY _queries.py ./
COPY api.py ./
COPY connector.py ./

EXPOSE 8000