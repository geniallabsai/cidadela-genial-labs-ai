#!/usr/bin/env python3
"""Grafo mermaid dos serviços detectados (Docker Compose + Kubernetes).

Uso: python3 grafico-servicos.py [RAIZ]
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inventario import walk, parse_compose, scan_k8s, COMPOSE_NAMES  # noqa: E402

DB_HINT = re.compile(r'db|database|postgres|mysql|mongo|redis|cache|queue|rabbit|kafka', re.I)


def main():
    root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else '.'
    files = walk(root)
    nodes = {}      # id -> (label, kind, origem)   kind: 'db' | 'sv' | 'k8s'
    edges = []
    compose_files = [f for f in files if os.path.basename(f) in COMPOSE_NAMES and f.count('/') <= 1]
    for cf in compose_files:
        svcs = parse_compose(os.path.join(root, cf))
        for name, meta in svcs.items():
            nid = 'c_' + re.sub(r'[^A-Za-z0-9]', '', name)
            label = '%s (%s)' % (name, meta['image']) if meta['image'] else name
            kind = 'db' if DB_HINT.search(name) or (meta['image'] and DB_HINT.search(meta['image'])) else 'sv'
            nodes[nid] = (label, kind, cf)
            for dep in meta['depends_on']:
                did = 'c_' + re.sub(r'[^A-Za-z0-9]', '', dep)
                edges.append('%s -.->|depends_on| %s' % (nid, did))
    for k in scan_k8s(files, root):
        if k['kind'] in ('Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob', 'Service', 'Ingress'):
            nid = 'k_' + re.sub(r'[^A-Za-z0-9]', '', k['kind']) + '_' + re.sub(r'[^A-Za-z0-9]', '', k['name'])
            nodes[nid] = (k['kind'] + ': ' + k['name'], 'k8s', k['arquivo'])

    if not nodes:
        print('Nenhum serviço detectado (sem compose/k8s com padrão reconhecido).')
        print('Determine a topologia manualmente na Fase 1 e desenhe o grafo de deploy no relatório.')
        return 0

    out = ['```mermaid', 'flowchart TD']
    have_compose = any(n.startswith('c_') for n in nodes)
    have_k8s = any(n.startswith('k_') for n in nodes)
    if have_compose:
        out.append('  subgraph compose["Docker Compose"]')
        for nid, (label, kind, src) in nodes.items():
            if nid.startswith('c_'):
                if kind == 'db':
                    out.append('    %s[("%s")]' % (nid, label))
                else:
                    out.append('    %s["%s"]' % (nid, label))
        out.append('  end')
    if have_k8s:
        out.append('  subgraph k8s["Kubernetes"]')
        for nid, (label, kind, src) in nodes.items():
            if nid.startswith('k_'):
                out.append('    %s["%s"]' % (nid, label))
        out.append('  end')
    for e in edges:
        out.append('  ' + e)
    out.append('```')
    print('\n'.join(out))
    print()
    print('Fonte: %s' % '; '.join(sorted({nodes[n][2] for n in nodes})))
    return 0


if __name__ == '__main__':
    sys.exit(main())
