// Serviço B de exemplo (Node stdlib): contadores + /healthz.
import http from "node:http";

const PORTA = Number(process.env.PORTA || 8002);
const contadores = {};

http
  .createServer((req, res) => {
    const rota = new URL(req.url, "http://x").pathname;
    const responder = (status, corpo) => {
      res.writeHead(status, { "content-type": "application/json; charset=utf-8" });
      res.end(JSON.stringify(corpo));
    };
    if (rota === "/healthz") return responder(200, { ok: true, servico: "servico-b" });
    if (rota === "/stats") return responder(200, { servico: "servico-b", contadores });
    contadores[rota] = (contadores[rota] || 0) + 1;
    responder(200, { servico: "servico-b", vistoEm: rota });
  })
  .listen(PORTA, () => console.log("servico-b ouvindo em :" + PORTA));
