FROM python:3.12.2

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY crapome.org.txt .
COPY PPIprophet/ PPIprophet/

ENTRYPOINT ["python", "main.py"]
