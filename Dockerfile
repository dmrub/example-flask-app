FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY static ./static
COPY templates ./templates
COPY app.py flask_reverse_proxy.py ./

ENV PORT 5000
#CMD ["python", "./app.py"]
CMD ["gunicorn", "--threads=5", "--workers=1", "--bind=0.0.0.0:5000", "app:app" ]
