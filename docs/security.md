# Segurança — EletroIA (MVP)

## Implementado nesta entrega

- `.env`/`.env.*` no `.gitignore` — segredos (incluindo `ANTHROPIC_API_KEY`) nunca
  commitados; `apps/api/.env.example` documenta as variáveis esperadas.
- CORS restrito à origem do frontend de desenvolvimento (`app/main.py`).
- Validação de payload via Pydantic em todas as rotas (`app/schemas/schemas.py`).
- Isolamento de containers via `docker-compose.yml` (Postgres não exposto além do
  necessário para desenvolvimento local).
- IDs primários como UUID (não sequenciais/adivinháveis).

## Não implementado nesta entrega (pendências explícitas)

- Autenticação/autorização (login, sessões, RBAC por papel — OWNER/ADMIN/ENGINEER/...).
  Hoje qualquer chamada à API atua como o usuário informado no payload — **não usar em
  produção sem autenticação real**.
- Multi-tenancy (isolamento de dados entre organizações).
- Upload de arquivos (planta em PDF/imagem/DWG/DXF) — quando implementado, deve validar
  tipo/tamanho, escanear conteúdo malicioso e usar URLs assinadas para storage.
- Rate limiting.
- Política de retenção/exclusão de dados e exportação (LGPD) — ver seção 42 do prompt
  mestre.
- Preenchimento automático de `AuditLog` em todas as mutações (o modelo existe, mas o
  `orchestrator.py` ainda não grava entradas de auditoria a cada geração/edição).

Essas pendências devem ser resolvidas antes de expor a plataforma publicamente ou usá-la
com dados reais de terceiros.
