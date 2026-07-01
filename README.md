# wp-agent-stack

Coleção reutilizável de assets de desenvolvimento agêntico para projetos WordPress:
**skills**, **agents**, **hooks** e **configurações de MCP**. Tudo aqui é agnóstico de
projeto — nasce de padrões validados em produção e é promovido para cá quando se prova
útil além do projeto de origem.

## Estrutura

```
wp-agent-stack/
├── skills/     — guias acionáveis (SKILL.md + código/config de referência)
├── agents/     — definições de subagentes especializados
├── hooks/      — hooks de automação (settings.json snippets + scripts)
└── mcp/        — configurações/documentação de servidores MCP úteis
```

## Skills disponíveis

| Skill | Descrição |
|---|---|
| [`woocommerce-custom-product-filter`](skills/woocommerce-custom-product-filter/) | Guia completo para adicionar filtros customizados (busca por nome, meta, etc.) ao bloco Product Filters do WooCommerce, mantendo navegação 100% AJAX sem reload de página. |

## Como usar num projeto

Ainda não há um mecanismo de instalação automatizado (tipo "plugin registry"). Por
enquanto, para usar uma skill num projeto WordPress:

```bash
# copiar a skill para o projeto
cp -R skills/<nome-da-skill> /caminho/do/projeto/.claude/skills/<nome-da-skill>

# ou, se preferir manter sincronizado com este repo:
git submodule add https://github.com/marcvlima/wp-agent-stack.git .claude/wp-agent-stack
ln -s ../wp-agent-stack/skills/<nome-da-skill> .claude/skills/<nome-da-skill>
```

Para `agents/` e `hooks/`, o padrão é análogo — copiar para `.claude/agents/` ou incluir
o snippet relevante no `settings.json` do projeto.

## Contribuindo (promovendo um asset de um projeto)

1. Valide o padrão em produção num projeto real primeiro.
2. Generalize (remova qualquer nome/detalhe específico do projeto de origem).
3. Adicione aqui na pasta correspondente, com um `SKILL.md`/`README.md` autoexplicativo.
4. Documente na tabela acima (ou na pasta correspondente).
