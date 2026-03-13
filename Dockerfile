FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN apt install -y --no-install-recommends python3-venv python3-pip
RUN python -m venv .
RUN source bin/activate
RUN pip install --no-cache-dir -r requirements.txt

COPY monitor_airport.py *.json ./

CMD ["python", "monitor_airport.py"]
