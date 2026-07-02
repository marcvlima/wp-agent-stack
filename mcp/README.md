# mcp

Notas e recomendações sobre servidores MCP úteis para desenvolvimento WordPress (ex:
`wordpress-mcp` da Automattic — endpoint, requisitos, armadilhas de setup). Ainda vazio
— documente aqui quando um servidor se provar útil além do projeto de origem.

**Importante:** diferente de skills/agents/hooks, servidores MCP **não** são arquivos
sob `.apm/` — no APM eles são declarados diretamente em `dependencies.mcp:` no
[`apm.yml`](../apm.yml) da raiz (referência de registry ou bloco self-defined com
`transport`/`command`/`url`). Esta pasta serve só para documentação/decisão de qual
servidor promover; a promoção em si acontece editando o `apm.yml`. Ver
[MCP as a primitive](https://microsoft.github.io/apm/producer/author-primitives/mcp-as-primitive/).
