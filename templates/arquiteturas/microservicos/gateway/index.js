// Gateway de exemplo: roteia por prefixo, agrega /healthz. Zero dependência.
import http from "node:http";

const PORTA = Number(process.env.PORTA || 8080);
const ALVOS = {
  "/api/a": process.env.SERVICO_A || "http://servico-a:8001",
  "/api/b": process.env.SERVICO_B || "http://servico-b:8002",
};

function servir(res, status, corpo) {
  res.writeHead(status, { "content-type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(corpo));
}

function reencaminhar(res, alvo, caminho) {
  const up = http.get(alvo + caminho, (u) => {
    res.writeHead(u.statusCode || 502, { "content-type": "application/json" });
    u.pipe(res);
  });
  up.on("error", () => servir(res, 503, { erro: "serviço a jusante indisponível", caminho }));
}

async function healthz(res) {
  const servicos = {};
  for (const [chave, alvo] of Object.entries(ALVOS)) {
    try {
      const r = await fetch(alvo + "/healthz");
      servicos[chave] = r.ok ? "ok" : "degradado(" + r.status + ")";
    } catch {
      servicos[chave] = "fora";
    }
  }
  const ok = Object.values(servicos).every((v) => v === "ok");
  servir(res, ok ? 200 : 503, { gateway: "ok", servicos });
}

http
  .createServer((req, res) => {
    const chave = Object.keys(ALVOS).find((p) => req.url.startsWith(p));
    if (!chave) {
      if (req.url === "/healthz") return void healthz(res);
      return servir(res, 404, { erro: "rota não encontrada — use /api/a/... ou /api/b/..." });
    }
    reencaminhar(res, ALVOS[chave], req.url.slice(chave.length) || "/");
  })
  .listen(PORTA, () => console.log("gateway ouvindo em :" + PORTA));
