# Arquitetura — EletroIA (MVP)

## Visão geral

```
apps/web   Next.js + TypeScript + Tailwind — UI (layout de 4 painéis)
apps/api   FastAPI (Python) — todas as camadas de engenharia/IA/dados
docker-compose.yml   Postgres + api + web para desenvolvimento local
```

## Camadas (backend, `apps/api/app`)

1. **Interpretação** — hoje limitada a cadastro manual de ambientes/cargas via API
   (`api/routes/projects.py`, `api/routes/loads.py`). Visão computacional de planta
   (PDF/DWG/DXF/imagem) é um próximo passo, não implementado nesta entrega.
2. **Engenharia** (`engineering/calculations/`) — funções determinísticas puras (potência,
   corrente, queda de tensão, seleção de condutor/disjuntor). Nunca chamadas por um LLM
   como substituto — são a única fonte de números técnicos do sistema.
3. **Normas** (`engineering/rules/`) — `RulesEngine` + regras concretas
   (`nbr5410.py`), cada uma com `rule_code`, severidade e função `evaluate()` pura.
4. **IA** (`ai/`) — `AIProvider` abstrato (`provider.py`), implementação Claude
   (`claude_provider.py`) e stub determinístico para testes (`mock_provider.py`).
   `interview.py` conduz a entrevista pergunta-a-pergunta; `chat.py` responde perguntas
   do usuário citando apenas fatos (`RuleResult`/`Calculation`) reais do projeto;
   `safety.py` intercepta tentativas de contornar regras/normas antes de qualquer
   chamada ao modelo (defesa em profundidade, ver `docs/ai-safety.md`).
5. **Validação profissional** — modelada nos dados (`status` do projeto, severidade
   `AZUL`), mas o fluxo completo de revisão/aprovação por profissional habilitado
   (seção 30/31 do prompt mestre) ainda não está implementado.

`engineering/orchestrator.py` conecta as camadas 2 e 3: a partir das cargas cadastradas,
gera circuitos, quadro, condutores, disjuntores e roda todas as regras aplicáveis,
persistindo `Calculation` e `RuleResult` para auditabilidade completa.

## Modelo de dados

Ver `apps/api/app/models/`. Subconjunto implementado da seção 39 do prompt mestre: User,
Project, Room, Load, Circuit, Panel, Breaker, Conductor, ProtectionDevice, Calculation,
Rule, RuleResult, NormativeReference, AuditLog (schema de auditoria criado, mas ainda não
preenchido automaticamente em todas as mutações — próximo passo).

## Fora de escopo nesta entrega

- Visão computacional (OCR, parsing de PDF/imagem/DWG/DXF).
- Editor CAD gráfico arrastável / diagrama unifilar exportável.
- Multi-tenancy completo, RBAC granular, marketplace de profissionais, billing.
- Emissão/integração de ART.

## Rodando localmente

```bash
docker compose up -d db
cd apps/api && alembic upgrade head
docker compose up -d api web
```

Backend em `http://localhost:8000` (docs em `/docs`), frontend em `http://localhost:3000`.
Defina `ANTHROPIC_API_KEY` em `apps/api/.env` (copie de `.env.example`) para usar o Claude
real; sem a chave, o sistema usa `MockAIProvider` (determinístico, sem chamadas de rede).
