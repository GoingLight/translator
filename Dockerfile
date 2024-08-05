FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y \
    pkg-config \
    libhdf5-dev \
    libgl1-mesa-glx \
    libgl1-mesa-dev \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app.py .
RUN mkdir -p /app/cache

EXPOSE 6050

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "6050"]