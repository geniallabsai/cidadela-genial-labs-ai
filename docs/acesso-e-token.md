# Acesso e token (registro)

O Genial Labs funciona com **token de acesso pessoal**: cada pessoa que se cadastra no site
oficial recebe uma chave ligada à conta dela e é com ela que instala e atualiza o sistema na
máquina. É o que garante que quem está usando sabe quem é, recebe as versões certas e tem um
caminho de suporte real.

## Como o modelo funciona

1. **Cadastro** no site oficial (nome + e-mail). Sem cartão, sem pegadinha: o cadastro é o que
   gera a chave.
2. **Token pessoal** na hora, formato `GL-…`, vinculado àquela conta.
3. **Instalação com token** — o instalador valida a chave no servidor e baixa o pacote.
4. **Atualizações continuam com token** (`genial update`): o que chega no seu terminal é sempre
   a versão certa da sua conta, sem fork nem cópia flutuando pela internet.

## Instalação com token (forma oficial)

```bash
curl -fsSL https://raw.githubusercontent.com/geniallabsai/genial-labs/main/install.sh | bash -s -- --token SEU_TOKEN_AQUI
```

Token inválido ou expirado ⇒ mensagem clara no terminal com o link para regenerar no site.

## Estado atual: beta público aberto

Hoje (**v1.0.x**) a instalação está **aberta, sem token**: qualquer pessoa instala com a linha
do [Iniciação rápida](iniciacao-rapida.md). O token chega **junto com o site oficial**
(veja [Roadmap](roadmap.md)). A forma do comando acima já está definida de propósito — quando o
site lançar, quem já usa nada muda além de adicionar `--token`.

## Boas práticas com o token

- O token é **pessoal**: não compartilhe, não cole em grupo de conversa.
- **Não commit** ele em repositório — irônico, né?: o secret-scan que o próprio Genial Labs
  instala nos seus projetos é exatamente o tipo de gate que grita com isso.
- Perdeu ou vazou? **Regenera no site** — o antigo para de valer imediatamente.
- Uma pessoa, um token, N máquinas próprias: usar o mesmo token nas suas máquinas é normal.

## Por que esse modelo

- **Fonte única de verdade:** atualização flui do Genial Labs para o seu terminal, não de
  cópia em cópia.
- **Suporte rastreável:** quando você chama ajuda, a gente sabe a exata versão instalada.
- **Futuro comercial justo:** planos (gratuito / pro / time) serão definidos por conta
  cadastrada — ninguém paga pelo que não registrou, ninguém registra pelo que não vai usar.
