FROM python:3.12-slim
WORKDIR /app
COPY app.py .
ENV PORTA=8010 TENANTS_DEMO=acme,contoso
USER nobody
EXPOSE 8010
HEALTHCHECK --interval=10s --timeout=3s \
  CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8010/healthz')"
CMD ["python", "app.py"]
