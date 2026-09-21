# Mapa de Linguagens — adaptar a skill a qualquer stack

## Tabela de referência
| Stack | Manifesto(s) | Entradas típicas | Testes | Sinal de multi-unidade |
|-------|-------------|------------------|--------|------------------------|
| Python | pyproject.toml, setup.py, requirements.txt | main.py, app.py, manage.py, wsgi/asgi.py | pytest (test_*.py, tests/) | múltiplos apps Django; uvicorn/fastapi por pasta |
| JavaScript/TypeScript | package.json (+ lock) | index.js/ts(x), server.js/ts, app.js, src/index.ts(x) | jest/vitest ( *.test/spec ), playwright, cypress | workspaces (pnpm/npm/yarn), nx, turborepo, lerna |
| Go | go.mod, go.work | cmd/*/main.go, main.go | go test (*_test.go) | go.work multi-module; vários cmd/ |
| Rust | Cargo.toml, Cargo.lock | src/main.rs, src/lib.rs | cargo test (tests/, #[test]) | workspace members; vários bins |
| Java | pom.xml, build.gradle(.kts) | @SpringBootApplication, Main-Class | JUnit (*Test.java, src/test) | Maven <modules>; Gradle subprojects |
| Kotlin | build.gradle.kts, settings.gradle.kts | main fun em module | JUnit/kotest | Gradle multi-module |
| C# / .NET | *.csproj, *.sln | Program.cs, Startup | xUnit/NUnit (*Tests.csproj) | solution com vários projects |
| PHP | composer.json | index.php, artisan (Laravel), console.php | PHPUnit (tests/) | vários composer.json (apps separados) |
| Ruby | Gemfile, gemspec | config.ru, bin/rails, app.rb | RSpec/Minitest (spec/, *_spec.rb) | Rails engine; múltiplos Gemfile |
| Swift | Package.swift, *.xcodeproj | @main, App struct | swift test / XCTest | SPM products; alvos separados |
| Elixir | mix.exs | lib/*_application.ex | ExUnit (test/) | apps em umbrella |
| Dart/Flutter | pubspec.yaml | main.dart, lib/ | flutter test | packages/ (monorepo) |
| Scala | build.sbt | object main | sbt test | multi-project sbt |
| C/C++ | CMakeLists.txt, Makefile | main.c/cpp | ctest, googletest | alvos separados no CMake |

Se a mesma árvore mistura stacks, trate cada subtá como subprojeto e some as topologias no relatório.

## Protocolo Genérico (stack fora da tabela)
Quando nenhum manifesto conhecido for encontrado, descubra a stack por este rito, nesta ordem:
1. **Manifesto:** qualquer arquivo de definição de projeto no topo (build.*, project*, *.json com dependências, Makefile com targets de build).
2. **Ponto de entrada:** procure `main`, `index`, `app`, `server`, `cli` nas pastas raiz, `src/`, `cmd/`, `lib/`, `bin/`.
3. **Testes:** diretórios `test`, `tests`, `spec` e padrões de nomeação local; comando de teste no README/Makefile/CI.
4. **Infra:** Dockerfile, compose, k8s, Terraform, scripts de deploy, CI (GitHub/GitLab/Jenkins/etc.).
5. **Superfícies públicas:** rotas registradas, handlers, listeners, jobs agendados.

Feito isso, o resto do método (topologia, rubrica, veredito, cirurgia, ofensiva, blindagem) é idêntico em qualquer linguagem: **arquitetura e segurança não dependem de sintaxe, dependem de fronteiras, dados, rede e deploy**. Faça no máximo UMA pergunta ao humano para confirmar a stack — e registre a resposta no relatório para a próxima auditoria.
