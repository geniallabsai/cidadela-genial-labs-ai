#!/usr/bin/env python3
"""Blindagem mecanica e idempotente — aplica as correcoes deterministicas do veredito da auditoria.

Uso:
    python3 blindagem.py [RAIZ] [--dry-run]

Fluxo: inventario (--json) -> aplica o que e mecanico -> reinventa -> relatorio ANTES/DEPOIS.
Cada edicao leva o marcador GENIAL-BLINDA e nunca se repete; o que nao e mecanico vira item
manual para as Fases 4-6 da skill cidadela (decisao de engenharia, nao regex). Apenas stdlib.
"""
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
MK = "GENIAL-BLINDA"


def inventario(raiz):
    r = subprocess.run([sys.executable, os.path.join(AQUI, "inventario.py"), "--json", raiz],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        sys.stderr.write(r.stderr or r.stdout)
        sys.exit(1)
    return json.loads(r.stdout)


def mapa_veredito(inv):
    return {r["componente"]: r["veredito"] for r in inv["veredito"]}


class Store(object):
    def __init__(self, dry):
        self.dry = dry
        self.buf = {}

    def ler(self, p):
        if self.dry:
            if p not in self.buf:
                self.buf[p] = open(p, encoding="utf-8").read() if os.path.isfile(p) else None
            return self.buf[p]
        return open(p, encoding="utf-8").read() if os.path.isfile(p) else None

    def gravar(self, p, t):
        if self.dry:
            self.buf[p] = t
        else:
            d = os.path.dirname(p)
            if d and not os.path.isdir(d):
                os.makedirs(d)
            open(p, "w", encoding="utf-8").write(t)

    def novo(self, p, t):
        if self.dry:
            if self.buf.get(p) is None:
                self.buf[p] = t
        elif not os.path.isfile(p):
            d = os.path.dirname(p)
            if d and not os.path.isdir(d):
                os.makedirs(d)
            open(p, "w", encoding="utf-8").write(t)


class Log(object):
    def __init__(self):
        self.aplicados, self.skips, self.manuais = [], [], []


def aplicar(st, raiz, p, mk, old, new, log, label):
    t = st.ler(p)
    if t is None:
        log.manuais.append((label, "arquivo ausente"))
        return
    if mk in t:
        log.skips.append(label)
        return
    c = t.count(old)
    if c != 1:
        log.manuais.append((label, "ancora aparece %dx (esperado 1x)" % c))
        return
    st.gravar(p, t.replace(old, new))
    log.aplicados.append((label, os.path.relpath(p, raiz)))


def criar(se, raiz, st, p, t, log, label):
    if st.ler(p) is not None:
        log.skips.append(label)
        return
    se.add(p)
    st.gravar(p, t)
    log.aplicados.append((label, os.path.relpath(p, raiz)))


def pkg_json(p):
    try:
        return json.loads(open(p, encoding="utf-8").read())
    except Exception:
        return None


def blinda_node(raiz, entry, st, log):
    rel_e = os.path.relpath(entry, raiz)
    rel = lambda q: q  # noqa

    # 1) falhas nao tratadas derrubam com mensagem legivel
    aplicar(st, raiz, entry, "unhandledRejection",
            "import jwt from 'jsonwebtoken';\n",
            "import jwt from 'jsonwebtoken';\n"
            "\n// %s: crash de promise sem tratamento vira saida limpa\n"
            "process.on('unhandledRejection', (err: unknown) => {\n"
            "  console.error('unhandledRejection:', err);\n"
            "  process.exit(1);\n"
            "});\n" % MK, log, "handler unhandledRejection")

    # 2) CORS * -> allowlist por ambiente
    aplicar(st, raiz, entry, "ALLOWED_ORIGINS",
            "res.setHeader('Access-Control-Allow-Origin', '*');",
            "// %s: CORS por allowlist (era *)\n"
            "  const origem = req.headers.origin || '';\n"
            "  const permitidas = (process.env.ALLOWED_ORIGINS || 'http://localhost:5173').split(',');\n"
            "  if (permitidas.includes(origem)) { res.setHeader('Access-Control-Allow-Origin', origem); }" % MK,
            log, "CORS allowlist")

    # 3) segredo de JWT em env com fail-fast
    aplicar(st, raiz, entry, "JWT_SECRET nao definido",
            "const JWT_SECRET = 'supersecret123';",
            "// %s: segredo vem do ambiente (falha cedo, nao na producao)\n"
            "if (!process.env.JWT_SECRET) {\n"
            "  throw new Error('JWT_SECRET nao definido no ambiente');\n"
            "}\n"
            "const JWT_SECRET = process.env.JWT_SECRET;" % MK,
            log, "JWT secret em env")

    # 4) token com expiracao curta
    aplicar(st, raiz, entry, "expiresIn",
            "const token = jwt.sign({ id: u.id }, 'secret');",
            "const token = jwt.sign({ id: u.id }, JWT_SECRET, { expiresIn: '15m' }); // %s: expiracao curta" % MK,
            log, "JWT expiresIn 15m")

    # 5) segredo saindo pelo log
    aplicar(st, raiz, entry, "sem credenciais no log",
            "console.log('login feito', token, senha);",
            "console.log('login ok'); // %s: sem credenciais no log" % MK,
            log, "log sem segredo")

    # 6) segredo de pagamento em env
    aplicar(st, raiz, entry, "STRIPE_KEY",
            "const STRIPE = 'sk_live_abcdefghijklmnop';",
            "const STRIPE = process.env.STRIPE_KEY || ''; // %s: chave de pagamento em env" % MK,
            log, "STRIPE em env")

    # 7) eval -> whitelist numerica
    aplicar(st, raiz, entry, "expressao invalida",
            "  return eval(expr);",
            "// %s: exec de string arbitraria virou whitelist numerica\n"
            "  if (!/^\\d[\\d+\\-*/(). ]*$/.test(String(expr))) { throw new Error('expressao invalida'); }\n"
            "  return Function('return (' + String(expr) + ')')();" % MK,
            log, "whitelist no lugar de exec arbitrario")

    # 8) healthz (antes dos middlewares finais)
    aplicar(st, raiz, entry, "/healthz",
            "export default app;",
            "// %s: rota de saude (docker/k8s/serverless dependem dela)\n"
            "app.get('/healthz', (_req: any, res: any) => { res.json({ ok: true }); });\n\n"
            "export default app;" % MK,
            log, "rota /healthz")

    # 9) 404 + middleware central de erro
    aplicar(st, raiz, entry, "rota nao encontrada",
            "export default app;",
            "// %s: 404 e erro central (nada vaza stack trace)\n"
            "app.use((_req: any, res: any) => { res.status(404).json({ erro: 'rota nao encontrada' }); });\n"
            "app.use((err: any, _req: any, res: any, _next: any) => {\n"
            "  console.error(err && err.message ? err.message : err);\n"
            "  res.status(500).json({ erro: 'falha interna' });\n"
            "});\n\n"
            "export default app;" % MK,
            log, "404 + erro central")

    # 10) porta em env + auto-listen so quando executado direto + shutdown limpo
    aplicar(st, raiz, entry, "ouvindo em :",
            "process.exit(1);\n});",
            "process.exit(1);\n});\n"
            "\n// %s: porta em env; escuta so quando executado direto (testes importam sem bind)\n"
            "const porta = Number(process.env.PORT || 3000);\n"
            "export const portaPadrao = porta;\n"
            "if (typeof module !== 'undefined' && typeof require !== 'undefined' && require.main === module) {\n"
            "  const server = app.listen(porta, () => { console.log('api ouvindo em :' + porta); });\n"
            "  process.on('SIGTERM', () => { server.close(() => process.exit(0)); });\n"
            "}" % MK,
            log, "porta env + shutdown")

    # 11) package.json: deps de seguranca, engines >=18, scripts
    pkgp = os.path.join(raiz, "package.json")
    j = pkg_json(pkgp)
    if j:
        deps = j.setdefault("dependencies", {})
        dev = j.setdefault("devDependencies", {})
        muda = False
        if "express-rate-limit" not in deps:
            deps["express-rate-limit"] = "^7.4.0"; muda = True
        if "helmet" not in deps:
            deps["helmet"] = "^7.1.0"; muda = True
        if "@types/express" not in dev:
            dev["@types/express"] = "^4.17.21"; muda = True
        if "@types/node" not in dev:
            dev["@types/node"] = "^20.11.0"; muda = True
        scr = j.setdefault("scripts", {})
        for k, v in (("build", "tsc"), ("typecheck", "tsc --noEmit"),
                     ("test", "npm run build && node --test")):
            if k not in scr:
                scr[k] = v; muda = True
        eng = j.get("engines") or {}
        if str(eng.get("node", "")) != ">=18":
            j["engines"] = dict(list(eng.items()) + [("node", ">=18")]); muda = True
        if muda:
            st.gravar(pkgp, json.dumps(j, indent=2) + "\n")
            log.aplicados.append(("package.json (rate limit, helmet, engines, scripts)", "package.json"))

    # 12) tsconfig: strict + interop
    tsp = os.path.join(raiz, "tsconfig.json")
    t = st.ler(tsp)
    if t:
        tj = json.loads(t)
        co = tj.setdefault("compilerOptions", {})
        antes = json.dumps(co, sort_keys=True)
        co["strict"] = True
        co["esModuleInterop"] = True
        co["skipLibCheck"] = True
        if json.dumps(co, sort_keys=True) != antes:
            st.gravar(tsp, json.dumps(tj, indent=2) + "\n")
            log.aplicados.append(('tsconfig "strict": true', "tsconfig.json"))
        else:
            log.skips.append("tsconfig strict")

    # 13) .env.example a partir do .env (sem valores)
    env = os.path.join(raiz, ".env")
    ex = os.path.join(raiz, ".env.example")
    linhas = []
    if os.path.isfile(env):
        for l in open(env, encoding="utf-8").read().splitlines():
            if l.strip() and not l.startswith("#") and "=" in l:
                linhas.append(l.split("=")[0].strip() + "=")
    for extra in ("PORT=3000", "JWT_SECRET=troque-esta-chave", "ALLOWED_ORIGINS=http://localhost:5173"):
        k = extra.split("=")[0]
        if not any(x.startswith(k + "=") for x in linhas):
            linhas.append(extra)
    if linhas and st.ler(ex) is None:
        se = set()
        criar(se, raiz, st, ex, "\n".join(linhas) + "\n", log, ".env.example")
    if os.path.isfile(env):
        log.manuais.append(("remover .env do git (historico)", ".env"))

    # 14) Dockerfile multi-stage com healthcheck
    df = ("# %s: build reprodutivel + saude verificada pela plataforma\n"
          "FROM node:20-alpine AS build\nWORKDIR /app\n"
          "COPY package*.json ./\nRUN npm install\n"
          "COPY tsconfig.json ./\nCOPY src ./src\nRUN npm run build\n\n"
          "FROM node:20-alpine\nWORKDIR /app\nENV NODE_ENV=production\n"
          "COPY package*.json ./\nRUN npm install --omit=dev\n"
          "COPY --from=build /app/dist ./dist\nEXPOSE 3000\n"
          "HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:3000/healthz || exit 1\n"
          'CMD ["node", "dist/server.js"]\n' % MK)
    se = set()
    criar(se, raiz, st, os.path.join(raiz, "Dockerfile"), df, log, "Dockerfile + healthcheck")

    # 15) docker-compose com variaveis obrigatorias
    dc = ("# %s\nservices:\n  api:\n    build: .\n"
          '    ports:\n      - "${PORT:-3000}:3000"\n'
          "    environment:\n      - PORT=3000\n"
          "      - JWT_SECRET=${JWT_SECRET:?defina JWT_SECRET}\n"
          "      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-http://localhost:5173}\n"
          "    healthcheck:\n"
          '      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:3000/healthz"]\n'
          "      interval: 30s\n      timeout: 3s\n      retries: 3\n" % MK)
    se = set()
    criar(se, raiz, st, os.path.join(raiz, "docker-compose.yml"), dc, log, "docker-compose + healthcheck")

    # 16) CI com gates
    ci = ("name: gates\non: [push, pull_request]\njobs:\n  gates:\n"
          "    runs-on: ubuntu-latest\n    steps:\n"
          "      - uses: actions/checkout@v4\n"
          "      - uses: actions/setup-node@v4\n        with:\n          node-version: 20\n"
          "      - run: npm install\n      - run: npm run typecheck\n      - run: npm test\n")
    se = set()
    criar(se, raiz, st, os.path.join(raiz, ".github", "workflows", "ci.yml"), ci, log, "CI gates")

    # 17) teste de fumaca (stdlib node:test; roda no CI)
    tt = ("import test from 'node:test';\nimport assert from 'node:assert';\n"
          "import { createRequire } from 'node:module';\n\n"
          "const require = createRequire(import.meta.url);\n"
          "const mod = require('../dist/server.js');\n\n"
          "test('healthz responde ok', async () => {\n"
          "  const srv = mod.default.listen(0);\n"
          "  await new Promise((r) => srv.once('listening', r));\n"
          "  const porta = srv.address().port;\n"
          "  const resp = await fetch(`http://127.0.0.1:${porta}/healthz`);\n"
          "  assert.strictEqual(resp.status, 200);\n"
          "  const corpo = await resp.json();\n"
          "  assert.strictEqual(corpo.ok, true);\n"
          "  srv.close();\n});\n")
    se = set()
    criar(se, raiz, st, os.path.join(raiz, "test", "smoke.test.mjs"), tt, log, "teste de fumaca (healthz)")


def blinda_django(raiz, st, log):
    settings = None
    for cand in ("settings.py", os.path.join("myapp", "settings.py"), os.path.join("config", "settings.py")):
        p = os.path.join(raiz, cand)
        if os.path.isfile(p):
            settings = p
            break
    if not settings:
        log.manuais.append(("Django: settings.py nao localizado", ""))
        return
    t = st.ler(settings)
    if t is None or "DEBUG = True" not in t:
        log.skips.append("django DEBUG")
        return
    if "import os" not in t:
        t = "import os\n" + t
    t2 = t.replace("DEBUG = True",
                   'DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"  # %s: DEBUG via ambiente' % MK, 1)
    st.gravar(settings, t2)
    log.aplicados.append(("Django DEBUG via ambiente", os.path.relpath(settings, raiz)))
    log.manuais.append(("hash de senhas (PBKDF2/bcrypt) e query parametrizada", "Fase 4"))


def achar_entry(raiz):
    ordem = ["src/server.ts", "src/index.ts", "src/app.ts", "index.ts", "server.ts", "app.ts",
             "src/index.js", "src/server.js", "index.js", "server.js", "app.js"]
    for rel in ordem:
        p = os.path.join(raiz, rel)
        if os.path.isfile(p):
            return p
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv[1:]
    raiz = os.path.abspath(args[0]) if args else "."
    if not os.path.isdir(raiz):
        sys.stderr.write("diretorio nao existe: %s\n" % raiz)
        return 1

    inv_antes = inventario(raiz)
    antes = mapa_veredito(inv_antes)
    st = Store(dry)
    log = Log()
    fws = " ".join(str(x) for x in inv_antes.get("frameworks", [])).lower()
    entry = achar_entry(raiz)
    pkg = pkg_json(os.path.join(raiz, "package.json")) or {}
    deps = (pkg.get("dependencies") or {})

    stack = " + ".join(str(x) for x in inv_antes.get("frameworks", [])) or "sem framework claro"
    langs = sorted(inv_antes.get("linguagens", {}).keys())
    print("BLINDAGEM CIDADELA%s" % (" (DRY-RUN)" if dry else ""))
    print("projeto : %s" % raiz)
    print("stack   : %s · linguagens: %s" % (stack, ", ".join(langs) or "-"))
    print("topologia: %s" % inv_antes.get("topologia", "?"))
    print("-" * 72)

    if entry and ("express" in fws or "express" in deps):
        blinda_node(raiz, entry, st, log)
    elif "django" in fws or os.path.isfile(os.path.join(raiz, "manage.py")):
        blinda_django(raiz, st, log)
    else:
        log.manuais.append(("stack fora das correcoes automaticas", "usar Fases 4-6 da skill cidadela"))

    # items manuais padrao (decisao, nao regex)
    if entry and os.path.isfile(entry):
        t = st.ler(entry) or ""
        if "password === " in t or "=== senha" in t or "senha ===" in t:
            log.manuais.append(("hash de senha (hoje: comparacao direta)", os.path.relpath(entry, raiz)))
        if '" + req.params' in t or 'WHERE id = "' in t or '" + req.query' in t:
            log.manuais.append(("query parametrizada (concatenacao visivel)", os.path.relpath(entry, raiz)))
        if "const usuarios = []" in t or "const items = []" in t:
            log.manuais.append(("estado em memoria -> banco/fila antes de escalar", os.path.relpath(entry, raiz)))

    print("APLICADOS (%d):" % len(log.aplicados))
    for nome, onde in log.aplicados:
        print("  ok   %s [%s]" % (nome, onde))
    if log.skips:
        print("JA BEM (%d): %s" % (len(log.skips), ", ".join(sorted(set(log.skips)))))
    print("MANUAIS — decisao de engenharia, Fases 4-6 (%d):" % len(log.manuais))
    for nome, onde in log.manuais:
        print("  -    %s%s" % (nome, (" [%s]" % onde) if onde else ""))
    print("-" * 72)

    if dry:
        print("DRY-RUN: nenhum arquivo foi tocado.")
        return 0

    inv_depois = inventario(raiz)
    depois = mapa_veredito(inv_depois)
    comps = list(dict.fromkeys(list(antes.keys()) + list(depois.keys())))
    print("AUDITORIA ANTES -> DEPOIS:")
    for c in comps:
        a, d = antes.get(c, "-"), depois.get(c, "-")
        seta = "  =" if a == d else " ->"
        print("  %-38s %-9s%s %-9s" % (c[:38], a, seta, d))
    mig_a = sum(1 for v in antes.values() if v == "MIGRAR")
    mig_d = sum(1 for v in depois.values() if v == "MIGRAR")
    bli_a = sum(1 for v in antes.values() if v == "BLINDAR")
    bli_d = sum(1 for v in depois.values() if v == "BLINDAR")
    print("-" * 72)
    print("RESUMO: MIGRAR %d->%d · BLINDAR %d->%d · restante da lista acima." % (mig_a, mig_d, bli_a, bli_d))
    print("PROXIMO: 'genial doctor %s' relê o estado; itens MANUAIS seguem para as Fases 4-6." % raiz)
    return 0


if __name__ == "__main__":
    sys.exit(main())
