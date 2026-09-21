FROM golang:1.22-alpine AS build
WORKDIR /src
COPY go.mod ./
RUN go mod download || true
COPY . .
RUN CGO_ENABLED=0 go build -o /out/app .
FROM alpine:3.20
RUN adduser -D -u 10001 app
COPY --from=build /out/app /usr/local/bin/app
USER app
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
CMD ["/usr/local/bin/app"]
