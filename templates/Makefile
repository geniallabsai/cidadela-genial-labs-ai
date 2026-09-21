# Baseline Genial Labs — comandos ajustados ao stack no scaffold
run: ; {{COMANDO_RUN}}
test: ; {{COMANDO_TEST}}
docker-build: ; docker build -t local:dev .
docker-up: ; docker compose up --build -d
docker-down: ; docker compose down
backup-db: ; docker compose exec -T db pg_dump -U genial genial | gzip > backup-$(shell date +%F).sql.gz
k8s-apply: ; kubectl apply -f k8s/
.PHONY: run test docker-build docker-up docker-down backup-db k8s-apply
