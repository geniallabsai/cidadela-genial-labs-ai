// Worker de exemplo (zero dependência): /saude e /eco, KV opcional.
const responder = (status, corpo) => new Response(JSON.stringify(corpo), {
  status,
  headers: { "content-type": "application/json; charset=utf-8" },
});

const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, POST, OPTIONS",
  "access-control-allow-headers": "content-type",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (url.pathname === "/" || url.pathname === "/saude") {
      return responder(200, { ok: true, de: "cloudflare-worker", ambiente: env.ENV || "local" });
    }
    if (url.pathname === "/eco" && request.method === "POST") {
      let dados;
      try { dados = await request.json(); } catch { return responder(400, { erro: "JSON inválido" }); }
      if (env.STORAGE) await env.STORAGE.put("eco:" + Date.now(), JSON.stringify(dados));
      return responder(200, { eco: dados });
    }
    return responder(404, { erro: "rota não encontrada" });
  },
};
