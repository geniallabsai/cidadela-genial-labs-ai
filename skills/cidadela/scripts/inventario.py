#!/usr/bin/env python3
"""Levantamento estrutural de base de código — agnóstico de linguagem.

Uso:
    python3 inventario.py [RAIZ] [--json]

Saída: resumo em markdown (ou JSON) com linguagens/LOC, manifestos e frameworks,
topologia de deploy (compose/k8s/Dockerfile/CI), pontos de entrada, testes,
alertas de segurança, sinais de multi-tenancy e cheiro de código gerado por IA.
Apenas stdlib; heurísticas de melhor esforço — o agente completa a leitura na Fase 1 da skill.
"""
import json
import os
import re
import sys
from collections import Counter

SKIP_DIRS = {'.git', 'node_modules', '.venv', 'venv', 'env', '.next', 'dist', 'build',
             'out', 'target', 'coverage', '.idea', '.vscode', 'vendor', 'Pods', 'tmp',
             '.pytest_cache', '.mypy_cache', '.turbo', '.cache', '.tox', '.nox',
             '.gradle', '.mvn', '__pycache__'}

LANG_EXT = {
    '.py': 'Python', '.js': 'JavaScript', '.mjs': 'JavaScript', '.cjs': 'JavaScript',
    '.jsx': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript', '.go': 'Go',
    '.rs': 'Rust', '.java': 'Java', '.kt': 'Kotlin', '.kts': 'Kotlin', '.cs': 'C#',
    '.php': 'PHP', '.rb': 'Ruby', '.swift': 'Swift', '.ex': 'Elixir', '.exs': 'Elixir',
    '.scala': 'Scala', '.c': 'C', '.h': 'C/C++', '.cpp': 'C++', '.cc': 'C++',
    '.hpp': 'C++', '.dart': 'Dart', '.vue': 'Vue', '.svelte': 'Svelte',
    '.sh': 'Shell', '.ps1': 'PowerShell', '.lua': 'Lua', '.zig': 'Zig',
}

COMPOSE_NAMES = {'docker-compose.yml', 'docker-compose.yaml', 'compose.yml', 'compose.yaml'}

FW_JS = {'react': 'React', 'next': 'Next.js', 'express': 'Express', 'fastify': 'Fastify',
         '@nestjs/core': 'NestJS', 'prisma': 'Prisma', '@prisma/client': 'Prisma',
         'drizzle-orm': 'Drizzle', 'mongoose': 'Mongoose', 'typeorm': 'TypeORM',
         'knex': 'Knex', 'sequelize': 'Sequelize', 'vue': 'Vue', '@angular/core': 'Angular',
         'svelte': 'Svelte', 'tailwindcss': 'Tailwind', 'apollo-server': 'Apollo'}
FW_PY = {'fastapi': 'FastAPI', 'starlette': 'Starlette', 'django': 'Django',
         'flask': 'Flask', 'celery': 'Celery', 'sqlalchemy': 'SQLAlchemy',
         'pydantic': 'Pydantic', 'tortoise-orm': 'Tortoise ORM', 'peewee': 'Peewee',
         'uvicorn': 'Uvicorn', 'gunicorn': 'Gunicorn'}
FW_GO = {'gin-gonic/gin': 'Gin', 'gorm.io/gorm': 'GORM', 'labstack/echo': 'Echo',
         'google.golang.org/grpc': 'gRPC', 'gorilla/mux': 'Mux'}

ENTRY_NAMES = {'main.go', 'main.py', 'app.py', 'index.js', 'index.ts', 'index.tsx',
               'server.js', 'server.ts', 'app.js', 'app.ts', 'main.c', 'main.cpp',
               'Program.cs', 'index.php', 'wsgi.py', 'asgi.py', 'manage.py', 'cli.js'}
ENTRY_PATH_RE = re.compile(r'(?:^|/)(?:src/(?:index|main|app)\.(?:ts|tsx|js|jsx|rs|go|java)|cmd/[A-Za-z0-9_\-]+/main\.go|public/index\.php)$')

SECRETS = [
    (re.compile(r'\bAKIA[0-9A-Z]{16}\b'), 'chave de acesso AWS'),
    (re.compile(r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----'), 'chave privada embutida'),
    (re.compile(r'\bgh[pousr]_[A-Za-z0-9]{36,}\b'), 'token GitHub'),
    (re.compile(r'\bAIza[0-9A-Za-z\-_]{35}\b'), 'chave Google API'),
    (re.compile(r'\bxox[baprs]-[A-Za-z0-9\-]{10,}\b'), 'token Slack'),
    (re.compile(r'\bsk_live_[A-Za-z0-9]{10,}\b'), 'chave estilo Stripe live'),
    (re.compile(r'\bsk-ant-[A-Za-z0-9_\-]{20,}\b'), 'chave estilo Anthropic'),
    (re.compile(r'\bhsk_[A-Za-z0-9]{30,}\b'), 'chave estilo OpenAI/HuggingFace'),
]

K8S_KINDS = ('Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob', 'Service', 'Ingress')
K8S_RE = re.compile(r'kind:\s*(%s)\b[ \t]*\n\s*metadata:\s*\n[ \t]+name:\s*["\']?([A-Za-z0-9._\-]+)' % '|'.join(K8S_KINDS))
URL_HOST_RE = re.compile(r'(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|amqp|redis|rediss)://[^/@\s"\']*@([A-Za-z0-9._\-]+)|(?:postgres(?:ql)?|mysql|mariadb|mongodb(?:\+srv)?|amqp|redis|rediss)://([A-Za-z0-9._\-]+)(?::\d+)?[/\s"\']')
HTTP_RE = re.compile(r'http://[A-Za-z0-9.\-]+(?::\d+)?(/\S*)?')

MT_CORE_RE = re.compile(r'tenant', re.I)
MT_ALT_TERMS = ('org_id', 'orgId', 'account_id', 'accountId', 'workspace_id',
                'workspaceId', 'client_id', 'clientId')

AI_PATTERNS = (
    ('eval/exec/deserialização', re.compile(r'\beval\s*\(|\bexec\s*\(|pickle\.loads?\b|yaml\.load\(|marshal\.loads|readObject\(')),
    ('shell injetável', re.compile(r'subprocess\.[A-Za-z]+\([^)]*shell\s*=\s*True|os\.system\s*\(')),
    ('CORS aberto (*)', re.compile(r'Access-Control-Allow-Origin:\s*["\']?\*|allowOrigins?\(\s*["\']\*', re.I)),
    ('debug ligado', re.compile(r'\bdebug\s*=\s*True\b|"DEBUG"\s*:\s*true\b|DEBUG_MODE\s*[:=]', re.I)),
    ('JWT em uso', re.compile(r'jwt\.(?:decode|encode)|create_access_token|jsonwebtoken|PyJWT|from\s+jose', re.I)),
    ('JWT fraco/padrão', re.compile(r'algs?\W{0,6}none|secret\s*[:=]\s*["\'](?:dev|changeme|secret|super|abc|123)\w{0,10}["\']', re.I)),
    ('HTML direto (XSS)', re.compile(r'innerHTML\s*=|dangerouslySetInnerHTML')),
    ('SQL por concatenação', re.compile(r'(?:SELECT|INSERT|UPDATE|DELETE)\s+[^"\']{0,80}["\']\s*\+\s*\w|f["\'][^"\']*\b(?:SELECT|INSERT|UPDATE|DELETE)\b', re.I)),
    ('catch vazio', re.compile(r'except[^:]*:\s*\n\s*(?:pass|\.\.\.)|catch\s*\([^)]*\)\s*\{\s*\}', re.M)),
    ('segredo em log/print', re.compile(r'(?:print|console\.log|System\.out\.println|fmt\.Println|logger?\.(?:info|warn|error|debug))\([^)]*(?:password|passwd|secret|token|senha|credencial|api[_-]?key)', re.I)),
    ('any/ignora tipo', re.compile(r':\s*any\b|as any\b|<any>\b')),
    ('toda de IA (TODO/HACK pendente)', re.compile(r'\b(TODO|FIXME|HACK)\b')),
)
RE_WEBHOOK = re.compile(r'webhook', re.I)
RE_SIGN = re.compile(r'hmac|signature|assinatura|signed[_-]?payload|x-signature', re.I)


def norm(p):
    return p.replace(os.sep, '/')


def walk(root):
    files = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for f in fns:
            files.append(norm(os.path.relpath(os.path.join(dp, f), root)))
    return files


def read_text(path, cap=300000):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
            return fh.read(cap)
    except OSError:
        return ''


def loc_of(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
            n = 0
            for _ in fh:
                n += 1
                if n > 100000:
                    break
            return n
    except OSError:
        return 0


def parse_compose(path):
    """Heurístico: {servico: {'image': str|None, 'depends_on': [..]}}."""
    services = {}
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
            lines = fh.read(300000).splitlines()
    except OSError:
        return services
    i = 0
    while i < len(lines) and not re.match(r'^services:\s*$', lines[i]):
        i += 1
    if i >= len(lines):
        return services
    i += 1
    end = i
    while end < len(lines):
        ln = lines[end]
        if ln.strip() and not ln.lstrip().startswith('#') and not ln[:1].isspace():
            break
        end += 1
    block = lines[i:end]
    indents = [len(l) - len(l.lstrip()) for l in block if l.strip() and not l.lstrip().startswith('#')]
    min_ind = min(indents) if indents else 2
    cur = None
    dep_mode = False
    dep_indent = 0
    for ln in block:
        if not ln.strip() or ln.lstrip().startswith('#'):
            continue
        ind = len(ln) - len(ln.lstrip())
        if ind == min_ind:
            m = re.match(r'^[ \t]*([A-Za-z0-9_.\-]+):\s*(.*)$', ln)
            if m:
                cur = m.group(1)
                services[cur] = {'image': None, 'depends_on': []}
                dep_mode = False
            continue
        if cur is None:
            continue
        stripped = ln.strip()
        m_inline = re.match(r'depends_on:\s*\[(.*)\]\s*$', stripped)
        if m_inline:
            items = [x.strip().strip('"\'') for x in m_inline.group(1).split(',') if x.strip()]
            services[cur]['depends_on'].extend(items)
        elif stripped.startswith('image:'):
            services[cur]['image'] = stripped.split(':', 1)[1].strip().strip('"\'')
        elif stripped.startswith('depends_on:'):
            dep_mode = True
            dep_indent = ind
        elif dep_mode:
            if ind > dep_indent and stripped.startswith('-'):
                services[cur]['depends_on'].append(stripped[1:].strip())
            else:
                dep_mode = False
    return services


def scan_k8s(files, root):
    found, seen, checked = [], set(), 0
    for rel in files:
        if not (rel.endswith('.yml') or rel.endswith('.yaml')):
            continue
        checked += 1
        if checked > 300:
            break
        txt = read_text(os.path.join(root, rel), 100000)
        if 'kind:' not in txt or 'metadata:' not in txt:
            continue
        for m in K8S_RE.finditer(txt):
            key = (m.group(1), m.group(2))
            if key not in seen:
                seen.add(key)
                found.append({'kind': m.group(1), 'name': m.group(2), 'arquivo': rel})
    return found


def scan_multitenancy(files, root):
    """Sinais de multi-tenancy (heurístico, best-effort)."""
    re_alt = {t: re.compile(r'\b%s\b' % re.escape(t)) for t in MT_ALT_TERMS}
    re_rls = re.compile(r'create\s+(?:row\s+level\s+security\s+|inline\s+)?policy\b', re.I)
    re_sp = re.compile(r'search_path', re.I)
    re_host = re.compile(r'(subdomain|x-forwarded-host|forwarded[\s_-]*host|request\.host|host\.split)', re.I)
    re_hdr = re.compile(r'(headers?|header)\b[^\n]{0,60}(x-tenant|tenant[-_]?id)', re.I)
    re_dsn = re.compile(r'(dsn|connection[_-]?string|database[_-]?url)', re.I)
    re_cache = re.compile(r'cache\.(?:set|get|delete|add|incr|expire)|redis\.(?:set|get|hset|hget)|cache_key')
    re_claim = re.compile(r'(claims?|jwt)[^\n]{0,80}tenant', re.I)

    st = {'mencoes': 0, 'alt': {t: 0 for t in MT_ALT_TERMS}, 'rls': [], 'search_path': [],
          'host': [], 'header': [], 'dsn': [], 'claims': 0, 'cache_com': 0, 'cache_sem': 0,
          'cache_ex': [], 'evidencias': []}
    sig_exts = set(LANG_EXT) | {'.sql'}
    n = 0
    for rel in files:
        if os.path.splitext(rel)[1] not in sig_exts:
            continue
        n += 1
        if n > 4000:
            break
        txt = read_text(os.path.join(root, rel), 200000)
        for i, line in enumerate(txt.splitlines(), 1):
            lt = line.lower()
            core = bool(MT_CORE_RE.search(lt))
            if core:
                st['mencoes'] += 1
                if len(st['evidencias']) < 6:
                    st['evidencias'].append('%s:%d — %s' % (rel, i, line.strip()[:90]))
            for t, rx in re_alt.items():
                if rx.search(line):
                    st['alt'][t] += 1
            if re_rls.search(lt) and any(k in lt for k in ('tenant', 'org', 'account')):
                if len(st['rls']) < 5:
                    st['rls'].append('%s:%d' % (rel, i))
            if re_sp.search(lt):
                if len(st['search_path']) < 5:
                    st['search_path'].append('%s:%d' % (rel, i))
            if re_host.search(line) and (core or any(re_alt[t].search(line) for t in MT_ALT_TERMS)):
                if len(st['host']) < 5:
                    st['host'].append('%s:%d — %s' % (rel, i, line.strip()[:80]))
            if re_hdr.search(line):
                if len(st['header']) < 5:
                    st['header'].append('%s:%d — %s' % (rel, i, line.strip()[:80]))
            if re_dsn.search(lt) and (core or 'org' in lt or 'account' in lt):
                if len(st['dsn']) < 5:
                    st['dsn'].append('%s:%d' % (rel, i))
            if re_claim.search(lt):
                st['claims'] += 1
            if re_cache.search(line):
                if core:
                    st['cache_com'] += 1
                else:
                    st['cache_sem'] += 1
                    if len(st['cache_ex']) < 3 and st['mencoes'] >= 3:
                        st['cache_ex'].append('%s:%d — %s' % (rel, i, line.strip()[:80]))
    total = st['mencoes'] + sum(st['alt'].values())
    if len(st['dsn']) >= 2:
        model = 'banco por tenant (suspeito)'
    elif len(st['search_path']) >= 2:
        model = 'schema por tenant (suspeito)'
    elif total >= 10:
        model = 'linhas compartilhadas com discriminador (provável)'
    elif total >= 1:
        model = 'sinais fracos — confirmar manualmente (pode ser single-tenant)'
    else:
        model = 'nenhum sinal automático'
    st['modelo'] = model
    return st


def scan_ai_smells(files, root):
    """Cheiro de vulnerabilidade típico de código gerado por IA (best-effort)."""
    cnt = Counter()
    ex = {label: [] for label, _ in AI_PATTERNS}
    wh = sig = 0
    n = 0
    for rel in files:
        if os.path.splitext(rel)[1] not in LANG_EXT:
            continue
        n += 1
        if n > 4000:
            break
        txt = read_text(os.path.join(root, rel), 200000)
        for line in txt.splitlines():
            lt = line.lower()
            wh += len(RE_WEBHOOK.findall(lt))
            sig += len(RE_SIGN.findall(lt))
            for label, rx in AI_PATTERNS:
                if rx.search(line):
                    cnt[label] += 1
                    if len(ex[label]) < 3:
                        ex[label].append(rel + ':' + str(0) )
    # segunda passada leve para exemplificar com linha (limitada, reusa arquivos já contados)
    done = set()
    n = 0
    for rel in files:
        if os.path.splitext(rel)[1] not in LANG_EXT:
            continue
        n += 1
        if n > 1500 or n > len(files):
            break
        txt = read_text(os.path.join(root, rel), 200000)
        for i, line in enumerate(txt.splitlines(), 1):
            for label, rx in AI_PATTERNS:
                if ex[label] and len(ex[label]) < 3 and rx.search(line):
                    ex[label][-1] = '%s:%d — %s' % (rel, i, line.strip()[:80])
                    done.add((label, i))
    maps = [f for f in files if f.endswith('.map')]
    return {'totais': dict(cnt), 'exemplos': ex, 'webhooks': wh, 'assinaturas': sig, 'maps': len(maps)}


def main():
    args = [a for a in sys.argv[1:] if a != '--json']
    as_json = '--json' in sys.argv[1:]
    root = os.path.abspath(args[0]) if args else '.'
    if not os.path.isdir(root):
        print('raiz não encontrada: %s' % root, file=sys.stderr)
        return 1
    files = walk(root)
    code_files = [f for f in files if os.path.splitext(f)[1] in LANG_EXT]

    # ---- linguagens / LOC ----
    lang_files = Counter()
    lang_loc = Counter()
    big = []
    for rel in code_files:
        lang = LANG_EXT[os.path.splitext(rel)[1]]
        lang_files[lang] += 1
        full = os.path.join(root, rel)
        try:
            size = os.path.getsize(full)
        except OSError:
            size = 0
        if size < 2_000_000:
            n = loc_of(full)
            lang_loc[lang] += n
            big.append((n, rel))
    big.sort(reverse=True)

    # ---- manifestos & frameworks ----
    manifests = Counter()
    for rel in files:
        base = os.path.basename(rel)
        if base in COMPOSE_NAMES:
            manifests['compose'] += 1
        elif base == 'package.json':
            manifests['package.json'] += 1
        elif base in ('pyproject.toml', 'setup.py', 'requirements.txt'):
            manifests['python-manifest'] += 1
        elif base == 'go.mod':
            manifests['go.mod'] += 1
        elif base == 'Cargo.toml':
            manifests['Cargo.toml'] += 1
        elif base == 'pom.xml':
            manifests['pom.xml'] += 1
        elif base in ('build.gradle', 'build.gradle.kts'):
            manifests['gradle'] += 1
        elif base.endswith('.csproj'):
            manifests['csproj'] += 1
        elif base.endswith('.sln'):
            manifests['sln'] += 1
        elif base == 'composer.json':
            manifests['composer.json'] += 1
        elif base == 'Gemfile':
            manifests['Gemfile'] += 1
        elif base == 'mix.exs':
            manifests['mix.exs'] += 1
        elif base == 'pubspec.yaml':
            manifests['pubspec.yaml'] += 1
        elif base == 'CMakeLists.txt':
            manifests['CMakeLists.txt'] += 1
        elif base in ('package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'uv.lock',
                      'poetry.lock', 'Cargo.lock', 'go.sum', 'Gemfile.lock'):
            manifests['lockfile'] += 1
        elif base in ('pnpm-workspace.yaml', 'turbo.json', 'nx.json', 'lerna.json',
                      'rush.json', 'go.work'):
            manifests['monorepo-signal'] += 1

    frameworks = []
    pkg = os.path.join(root, 'package.json')
    if os.path.isfile(pkg):
        try:
            data = json.loads(read_text(pkg))
            deps = dict(data.get('dependencies') or {})
            deps.update(data.get('devDependencies') or {})
            for k, label in FW_JS.items():
                if k in deps and label not in frameworks:
                    frameworks.append(label)
            if data.get('workspaces'):
                frameworks.append('monorepo(workspaces)')
        except (ValueError, AttributeError):
            pass
    pyproj = os.path.join(root, 'pyproject.toml')
    if os.path.isfile(pyproj):
        txt = read_text(pyproj)
        for k, label in FW_PY.items():
            if re.search(r'["\']%s["\']' % re.escape(k), txt) and label not in frameworks:
                frameworks.append(label)
    gomod = os.path.join(root, 'go.mod')
    if os.path.isfile(gomod):
        txt = read_text(gomod)
        for k, label in FW_GO.items():
            if k in txt and label not in frameworks:
                frameworks.append(label)
    gradle = None
    for name in ('build.gradle', 'build.gradle.kts'):
        if os.path.isfile(os.path.join(root, name)):
            gradle = name
            break
    if gradle:
        txt = read_text(os.path.join(root, gradle))
        if re.search(r'spring(-boot)?\b', txt, re.I) and 'Spring' not in frameworks:
            frameworks.append('Spring')
    pom = os.path.join(root, 'pom.xml')
    if os.path.isfile(pom):
        txt = read_text(pom)
        if 'spring-boot-starter-parent' in txt and 'Spring' not in frameworks:
            frameworks.append('Spring')
        mods = re.findall(r'<module>\s*([^<]+?)\s*</module>', txt)
        if mods:
            frameworks.append('maven-multi-module(%d)' % len(mods))
    if os.path.isfile(os.path.join(root, 'Gemfile')):
        txt = read_text(os.path.join(root, 'Gemfile'))
        if re.search(r'^\s*gem\s+[\'"]rails[\'"]', txt, re.M) and 'Rails' not in frameworks:
            frameworks.append('Rails')
    comp = os.path.join(root, 'composer.json')
    if os.path.isfile(comp):
        txt = read_text(comp)
        if 'laravel/framework' in txt and 'Laravel' not in frameworks:
            frameworks.append('Laravel')

    # ---- topologia de deploy ----
    compose_files = [f for f in files if os.path.basename(f) in COMPOSE_NAMES and f.count('/') <= 1]
    compose_services = {}
    for cf in compose_files:
        svcs = parse_compose(os.path.join(root, cf))
        for name, meta in svcs.items():
            meta['arquivo'] = cf
            compose_services[name] = meta
    k8s = scan_k8s(files, root)
    k8s_workloads = [k for k in k8s if k['kind'] in ('Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob')]
    dockerfiles = [f for f in files if 'dockerfile' in os.path.basename(f).lower()]
    multi_unit_signals = []
    if compose_services:
        multi_unit_signals.append('compose: %d serviços (%s)' % (len(compose_services), ', '.join(sorted(compose_services))))
    if k8s_workloads:
        multi_unit_signals.append('k8s: %d workloads' % len(k8s_workloads))
    n_pkg = len([f for f in files if os.path.basename(f) == 'package.json'])
    if n_pkg >= 2:
        multi_unit_signals.append('%d package.json na árvore' % n_pkg)
    if manifests.get('pom.xml', 0) >= 2 or manifests.get('go.mod', 0) >= 2:
        multi_unit_signals.append('vários módulos de build')
    n_units = len(compose_services) + len(k8s_workloads)
    if n_units >= 2:
        topo = 'MÚLTIPLOS DEPLOYAVÉIS — verificar independência (Fase 1)'
    elif n_units == 1:
        topo = 'ÚNICO DEPLOYAVEL detectado — monolito (verificar se há módulos internos)'
    else:
        topo = 'Nenhum artefato de deploy detectado (provável processo único / monolito) — confirmar na Fase 1'

    # estado compartilhado suspeito
    hosts = set()
    for rel in files:
        base = os.path.basename(rel)
        is_code = os.path.splitext(base)[1] in LANG_EXT
        is_cfg = base.endswith(('.ini', '.toml', '.properties', '.yaml', '.yml', '.cfg')) or base.startswith('.env')
        if not (is_code or is_cfg):
            continue
        txt = read_text(os.path.join(root, rel), 60000)
        for m in URL_HOST_RE.finditer(txt):
            host = m.group(1) or m.group(2)
            if host and host not in ('localhost', '127.0.0.1'):
                hosts.add(host)
    shared_state = sorted(h for h in hosts if h in compose_services or h in {k['name'] for k in k8s})

    # ---- CI, entrypoints, testes ----
    ci = []
    wf_dir = os.path.join(root, '.github', 'workflows')
    if os.path.isdir(wf_dir):
        ci.append('.github/workflows (%d workflows)' % len(os.listdir(wf_dir)))
    for sig in ('.gitlab-ci.yml', 'Jenkinsfile', 'bitbucket-pipelines.yml', 'azure-pipelines.yml', '.circleci/config.yml'):
        if sig in files:
            ci.append(sig)

    entries = []
    for f in files:
        base = os.path.basename(f)
        if base in ENTRY_NAMES and f.count('/') <= 3:
            entries.append(f)
        elif ENTRY_PATH_RE.search(f) and f.count('/') <= 4:
            entries.append(f)

    test_buckets = Counter()
    for f in files:
        if re.search(r'\.(test|spec)\.[jt]sx?$', f):
            test_buckets['jest/vitest (js/ts)'] += 1
        elif re.search(r'(?:^|/)tests?/', f):
            test_buckets['diretório tests/'] += 1
        elif re.search(r'test_[^/]+\.py$|[^/]+_test\.py$', f):
            test_buckets['python'] += 1
        elif re.search(r'[^/]+_test\.go$', f):
            test_buckets['go'] += 1
        elif re.search(r'[^/]+Test\.java$|(?:^|/)src/test/', f):
            test_buckets['java'] += 1
        elif re.search(r'[^/]+_spec\.rb$|(?:^|/)spec/', f):
            test_buckets['ruby/rspec'] += 1
        elif re.search(r'[^/]+Tests?\.csproj$|\.Tests\.', f):
            test_buckets['csharp'] += 1
    total_tests = sum(test_buckets.values())

    # ---- multitenancy e cheiro de IA ----
    mt = scan_multitenancy(files, root)
    ai = scan_ai_smells(files, root)

    # ---- alertas de segurança ----
    env_files = [f for f in files if (os.path.basename(f) == '.env' or os.path.basename(f).startswith('.env.'))
                 and os.path.basename(f) not in ('.env.example', '.env.sample', '.env.template')]
    secret_hits = []
    n_secret_scanned = 0
    for rel in code_files:
        n_secret_scanned += 1
        if n_secret_scanned > 4000:
            break
        txt = read_text(os.path.join(root, rel), 200000)
        for i, line in enumerate(txt.splitlines(), 1):
            for pat, label in SECRETS:
                if pat.search(line):
                    secret_hits.append('%s:%d — %s' % (rel, i, label))
    http_refs = 0
    http_examples = []
    n_http_scanned = 0
    for rel in code_files:
        n_http_scanned += 1
        if n_http_scanned > 4000:
            break
        txt = read_text(os.path.join(root, rel), 200000)
        for line in txt.splitlines():
            for m in HTTP_RE.finditer(line):
                tok = m.group(0)
                if re.search(r'localhost|127\.0\.0\.1|0\.0\.0\.0|example\.com|schema\.org', tok):
                    continue
                http_refs += 1
                if len(http_examples) < 5:
                    http_examples.append('%s: %s' % (rel, tok[:80]))

    result = {
        'raiz': root,
        'total_arquivos': len(files),
        'linguagens': {l: {'arquivos': lang_files[l], 'linhas': lang_loc[l]} for l in lang_files},
        'manifestos': dict(manifests),
        'frameworks': frameworks,
        'topologia': topo,
        'unidades': {
            'compose': compose_services,
            'k8s': k8s,
            'dockerfiles': dockerfiles,
        },
        'multi_unidade_sinais': multi_unit_signals,
        'hosts_de_estado': sorted(hosts),
        'estado_compartilhado_suspeito': shared_state,
        'ci': ci,
        'entrypoints': sorted(set(entries)),
        'testes': dict(test_buckets),
        'total_testes_aprox': total_tests,
        'multitenancy': mt,
        'codigo_ia': ai,
        'seguranca': {
            'env_commitados': env_files,
            'segredos_possiveis': secret_hits[:10],
            'http_naotls_em_codigo': http_refs,
            'http_exemplos': http_examples,
        },
        'maiores_arquivos': [{'linhas': n, 'arquivo': r} for n, r in big[:10]],
    }

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    lines = []
    lines.append('# Levantamento — %s' % root)
    lines.append('')
    lines.append('## Resumo')
    tot_loc = sum(lang_loc.values())
    lines.append('- Arquivos: %d · Código: %d linhas em %d linguagens' % (len(files), tot_loc, len(lang_files)))
    lines.append('- Topologia preliminar: **%s**' % topo)
    for s in multi_unit_signals:
        lines.append('  - %s' % s)
    lines.append('')
    lines.append('## Linguagens')
    lines.append('| Linguagem | Arquivos | Linhas |')
    lines.append('|-----------|----------|--------|')
    for l in sorted(lang_files, key=lambda x: -lang_loc[x]):
        lines.append('| %s | %d | %d |' % (l, lang_files[l], lang_loc[l]))
    lines.append('')
    lines.append('## Manifestos & Frameworks')
    lines.append('- Manifestos: %s' % (', '.join('%s×%d' % (k, v) for k, v in sorted(manifests.items())) or 'nenhum detectado'))
    lines.append('- Frameworks: %s' % (', '.join(frameworks) or 'nenhum detectado'))
    lines.append('')
    lines.append('## Topologia de Deploy')
    lines.append('- Dockerfiles: %d' % len(dockerfiles))
    for cf in compose_files:
        svcs = parse_compose(os.path.join(root, cf))
        img = {n: (m['image'] or '?') for n, m in svcs.items()}
        lines.append('- Compose `%s`: serviços [%s] (imagens: %s)' % (cf, ', '.join(sorted(svcs)), '; '.join('%s→%s' % x for x in sorted(img.items()))))
    if k8s:
        lines.append('- Kubernetes: %s' % ', '.join('%s:%s (%s)' % (k['kind'], k['name'], k['arquivo']) for k in k8s))
    else:
        lines.append('- Kubernetes: nenhum manifesto com kind/metadata detectado')
    lines.append('- CI: %s' % (', '.join(ci) or 'não detectado'))
    if hosts:
        lines.append('- Hosts de estado em configs/código: %s' % ', '.join(sorted(hosts)))
    if shared_state:
        lines.append('- ⚠️ **Estado compartilhado suspeito:** %s (hostname igual a um serviço de deploy — checar banco compartilhado entre unidades)' % ', '.join(shared_state))
    lines.append('')
    lines.append('## Pontos de Entrada')
    lines.append('- %s' % (', '.join(sorted(set(entries))) or 'nenhum padrão reconhecido — localizar manualmente'))
    lines.append('')
    lines.append('## Testes')
    lines.append('- Arquivos de teste (aprox.): %d %s' % (total_tests, ('· ' + ', '.join('%s×%d' % (k, v) for k, v in sorted(test_buckets.items()))) if total_tests else '(nenhum detectado)'))
    lines.append('')
    lines.append('## Sinais Multitenancy')
    if mt['modelo'] == 'nenhum sinal automático':
        lines.append('- Nenhum sinal automático (single-tenant ou stack fora das heurísticas) — confirmar na Fase 1')
    else:
        lines.append('- Modelo estimado: **%s**' % mt['modelo'])
        alt_txt = ', '.join('%s×%d' % (k, v) for k, v in sorted(mt['alt'].items()) if v) or '—'
        lines.append('- Menções "tenant": %d · termos alternativos: %s' % (mt['mencoes'], alt_txt))
        for label, key in (('RLS/policies', 'rls'), ('search_path (schema por tenant)', 'search_path'),
                            ('Resolução por host/subdomain', 'host'), ('Header de tenant', 'header'),
                            ('DSN/connection por tenant', 'dsn')):
            if mt[key]:
                lines.append('- %s: %s' % (label, '; '.join(mt[key][:5])))
        if mt['cache_com'] or mt['cache_sem']:
            lines.append('- Cache com escopo de tenant: %d · sem escopo visível: %d%s' % (
                mt['cache_com'], mt['cache_sem'],
                (' — exemplos: %s' % '; '.join(mt['cache_ex'][:3])) if mt['cache_sem'] and mt['mencoes'] >= 3 else ''))
        if mt['claims']:
            lines.append('- Claims/JWT com tenant: %d ocorrências' % mt['claims'])
        if mt['evidencias']:
            lines.append('- Evidências (amostra):')
            for e in mt['evidencias']:
                lines.append('  - %s' % e)
    lines.append('')
    lines.append('## Alertas de Segurança')
    lines.append('- `.env` na árvore (possível secret commitado): %s' % (', '.join(env_files) if env_files else 'nenhum'))
    if secret_hits:
        lines.append('- Segredos possíveis em código:')
        for h in secret_hits[:10]:
            lines.append('  - %s' % h)
    else:
        lines.append('- Segredos possíveis em código: nenhum padrão batido')
    lines.append('- `http://` não-localhost em código: %d ocorrências' % http_refs)
    for h in http_examples:
        lines.append('  - %s' % h)
    lines.append('')
    lines.append('## Código gerado por IA — cheiro de vulnerabilidade')
    if any(ai['totais'].values()):
        for label, _rx in AI_PATTERNS:
            nv = ai['totais'].get(label, 0)
            if nv:
                exs = [e for e in ai['exemplos'].get(label, []) if ':' in e and not e.endswith(':0')]
                lines.append('- **%s**: %d ocorrência(s)%s' % (label, nv, (' — ex.: %s' % '; '.join(exs[:3])) if exs else ''))
    else:
        lines.append('- Nenhum padrão-alvo batido (bom sinal; a Fase 5 ofensiva continua obrigatória)')
    lines.append('- Webhooks: %d menç(ões) · verificação de assinatura (hmac/signature): %d' % (ai['webhooks'], ai['assinaturas']))
    if ai['webhooks'] and not ai['assinaturas']:
        lines.append('  ⚠️ Webhook sem assinatura aparente — probe de evento forjado é obrigatória (ofensiva.md §2)')
    if ai['maps']:
        lines.append('- Source maps: %d arquivo(s) .map — verificar se servidos em produção (canal 10 de vazamento)' % ai['maps'])
    lines.append('- Prioridade da Fase 5: "segredo em log/print", "SQL por concatenação", "JWT fraco/padrão", "catch vazio" (nesta ordem, se >0).')
    lines.append('')
    lines.append('## Maiores Arquivos (top 10 por linhas)')
    for n, r in big[:10]:
        lines.append('- %6d  %s' % (n, r))
    lines.append('')
    lines.append('## Fallback manual (sem Python)')
    lines.append('```bash')
    lines.append('find . -type d -name node_modules -prune -o -type f -print | wc -l')
    lines.append('grep -rn "AKIA\\|PRIVATE KEY\\|gh[pousr]_" --include="*.py" --include="*.js" --include="*.ts" --include="*.go" . | head')
    lines.append('ls docker-compose*.yml compose*.yml 2>/dev/null && grep -A30 "^services:" docker-compose.yml')
    lines.append('find . -name "Dockerfile*" -o -name "*.tf" -o -name "*.csproj" -o -name "go.mod" | head -50')
    lines.append('grep -rin "tenant\\|RLS\\|search_path" --include="*.py" --include="*.js" --include="*.ts" --include="*.go" --include="*.sql" . | head -30')
    lines.append('grep -rn "eval(" --include="*.js" --include="*.ts" --include="*.py" . | head')
    lines.append('grep -rln "webhook" --include="*.js" --include="*.py" --include="*.go" --include="*.ts" . | head')
    lines.append('```')
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    sys.exit(main())
