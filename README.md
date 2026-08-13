# EletroIA (MVP)

Plataforma de IA para projetos elétricos residenciais de baixa tensão no Brasil. Ver
`docs/architecture.md` para a visão completa e `docs/ai-safety.md` /
`docs/engineering-rules.md` / `docs/calculation-engine.md` para as camadas críticas de
segurança e engenharia.

## Como rodar

1. Copie `apps/api/.env.example` para `apps/api/.env` e preencha `ANTHROPIC_API_KEY` (se
   não preencher, o backend usa um provider de IA "mock" determinístico — tudo o resto
   funciona normalmente).
2. Suba o banco e rode as migrações:
   ```bash
   docker compose up -d db
   cd apps/api
   python -m venv .venv && .venv/Scripts/pip install -r requirements.txt   # Windows
   .venv/Scripts/alembic upgrade head
   ```
3. Suba tudo via Docker Compose:
   ```bash
   docker compose up -d
   ```
   Backend: http://localhost:8000/docs · Frontend: http://localhost:3000

**Nota (ambiente onde este MVP foi gerado):** o Docker Desktop estava instalado mas não
finalizou a inicialização do backend (WSL2) automaticamente — foi necessário iniciar a
distro `docker-desktop` manualmente (`wsl -d docker-desktop`) e mesmo assim o serviço
`com.docker.backend` não expôs o named pipe a tempo de rodar `docker compose up`
end-to-end nesta sessão. Se isso acontecer no seu ambiente: abra o Docker Desktop
manualmente pela primeira vez, aceite os termos/inicialização, e só então rode os
comandos acima.

## Testes (não dependem de Docker)

```bash
cd apps/api
.venv/Scripts/pytest -q
```

43 testes cobrindo o motor de cálculo, o motor de regras (incluindo o caso de segurança
"tomada dentro do box do chuveiro") e a defesa contra prompts adversariais ("red team").

```bash
cd apps/web
npm run build
```

## Estrutura

```
apps/web    Next.js — frontend (layout de 4 painéis)
apps/api    FastAPI — camadas de engenharia/regras/IA/dados
docs/       Documentação de arquitetura, regras, cálculo, IA e segurança
```
