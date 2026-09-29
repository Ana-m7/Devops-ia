FROM docker.io/library/python:3.12-slim
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/app.py .
RUN useradd -m appuser
USER appuser
EXPOSE 5000
CMD ["python", "app.py"]
