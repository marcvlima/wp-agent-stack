# wp-agent-stack

Coleção reutilizável de assets de desenvolvimento agêntico para projetos WordPress:
**skills**, **agents**, **hooks** e **configurações de MCP**. Tudo aqui é agnóstico de
projeto — nasce de padrões validados em produção e é promovido para cá quando se prova
útil além do projeto de origem.

Empacotado como um pacote **[APM (Agent Package Manager)](https://github.com/microsoft/apm)**
real — instalável com um único comando em Claude Code, Cursor, GitHub Copilot, Windsurf
e (via flag explícita) Google Antigravity.

## Estrutura

```
wp-agent-stack/
├── apm.yml                 — manifesto do pacote APM (nome, versão, targets, deps)
├── apm.lock.yaml            — lockfile de dependências (reprodutibilidade)
├── .claude-plugin/          — manifesto sintetizado p/ instalação direta como plugin Claude Code
├── .github/plugin/          — manifesto sintetizado p/ ecossistema Copilot/GitHub
└── .apm/                    — árvore-fonte: TODOS os primitives são autorados aqui
    ├── skills/<nome>/SKILL.md (+ scripts/, references/, assets/, examples/)
    ├── agents/<nome>.agent.md
    ├── instructions/<nome>.instructions.md
    ├── prompts/<nome>.prompt.md   (também vira /comando)
    └── hooks/<nome>.json
```

`.apm/` é a única localização observada pelo instalador — primitives fora dela **não**
são empacotados nem instalados (validado com `apm pack --dry-run`).

## Primitives disponíveis

| Tipo | Nome | Descrição |
|---|---|---|
| skill | [`woocommerce-custom-product-filter`](.apm/skills/woocommerce-custom-product-filter/) | Guia completo para adicionar filtros customizados (busca por nome, meta, etc.) ao bloco Product Filters do WooCommerce, mantendo navegação 100% AJAX sem reload de página. |

`agents/`, `instructions/`, `prompts/` e `hooks/` ainda não têm nenhum primitive
promovido — adicione-os em `.apm/<tipo>/` seguindo o guia do
[APM Producer](https://microsoft.github.io/apm/producer/author-primitives/) quando um
padrão se provar útil além do projeto de origem.

## Como instalar num projeto

Requer o [CLI do APM](https://microsoft.github.io/apm/quickstart/) instalado
(`curl -sSL https://aka.ms/apm-unix | sh`).

```bash
cd /caminho/do/seu/projeto-wordpress

# instala em todos os targets configurados no apm.yml do projeto consumidor
# (ou auto-detectados pelo filesystem: .claude/, .cursor/, .github/, .windsurf/)
apm install marcvlima/wp-agent-stack

# ou apontando targets explicitamente
apm install marcvlima/wp-agent-stack --target claude,cursor,copilot,windsurf

# Google Antigravity é "explicit-only" no APM — precisa ser pedido à parte
apm install marcvlima/wp-agent-stack --target antigravity
```

Isso resolve o pacote, roda o scan de segurança embutido do APM, e faz deploy nativo dos
primitives — skills vão para `.claude/skills/` + `.agents/skills/` (convenção
cross-client [Agent Skills](https://agentskills.io) já lida nativamente por
Cursor/Copilot/Windsurf/Antigravity), agents/instructions/hooks são convertidos para o
formato de cada harness (`.cursor/`, `.github/`, `.windsurf/` etc.) por
`apm install`/`apm compile`. Roda `apm install --frozen` em CI para reproduzir o
`apm.lock.yaml` exatamente.

Para instalar só um primitive específico (sem os demais do pacote), use path-based
install: `apm install marcvlima/wp-agent-stack/.apm/skills/woocommerce-custom-product-filter`.

## Contribuindo (promovendo um asset de um projeto)

1. Valide o padrão em produção num projeto real primeiro.
2. Generalize (remova qualquer nome/detalhe específico do projeto de origem).
3. Adicione em `.apm/<tipo>/` seguindo a convenção do primitive (`SKILL.md`,
   `<nome>.agent.md`, `<nome>.instructions.md`, `<nome>.json` para hooks — ver
   [author-primitives](https://microsoft.github.io/apm/producer/author-primitives/)).
4. Bump de versão em `apm.yml` (semver: PATCH para ajustes, MINOR para primitive novo,
   MAJOR para mudança que quebra consumidores) — `includes: auto` já garante que o novo
   asset entra no pacote sem precisar declarar cada arquivo manualmente.
5. Documente na tabela acima.
6. Valide antes de commitar:
   ```bash
   apm compile --validate
   apm pack --dry-run --verbose   # confirma que só os arquivos certos entram no pacote
   ```
