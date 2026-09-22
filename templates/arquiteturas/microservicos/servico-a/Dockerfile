FROM python:3.12-slim
WORKDIR /app
COPY app.py .
ENV PORTA=8001
USER nobody
EXPOSE 8001
HEALTHCHECK --interval=10s --timeout=3s \
  CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8001/healthz')"
CMD ["python", "app.py"]
