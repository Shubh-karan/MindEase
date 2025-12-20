FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /code/.deepface && chmod -R 777 /code/.deepface
ENV DEEPFACE_HOME=/code/.deepface

RUN chmod -R 777 /code

EXPOSE 7860

CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120"]

CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120", "--access-logfile", "-"]