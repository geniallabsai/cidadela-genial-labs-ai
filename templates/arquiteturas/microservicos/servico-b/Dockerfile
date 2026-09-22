FROM node:20-alpine
WORKDIR /app
COPY package.json index.js .
USER node
EXPOSE 8002
HEALTHCHECK --interval=10s --timeout=3s \
  CMD node -e "fetch('http://localhost:8002/healthz').then(r => { if (!r.ok) process.exit(1); })"
CMD ["node", "index.js"]
