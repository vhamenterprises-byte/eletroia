# Deploy — EletroIA (Neon + Render + Vercel)

Este caminho evita depender do Docker Desktop local: o banco fica na nuvem (Neon) desde
o início, então o backend roda tanto localmente quanto em produção contra o mesmo tipo de
conexão.

## 1. Banco de dados (Neon)

1. Crie uma conta grátis em https://neon.tech (aceita login com GitHub/Google).
2. Crie um projeto (ex.: `eletroia`).
3. No painel do projeto, copie a **connection string** (formato
   `postgresql://usuario:senha@ep-xxxx.neon.tech/eletroia?sslmode=require`).
4. Me envie essa string (ou cole em `apps/api/.env` como `DATABASE_URL=...`) — eu rodo as
   migrações (`alembic upgrade head`) contra ela e já deixo o schema pronto.

## 2. Repositório no GitHub

Vercel e Render fazem deploy contínuo a partir de um repositório Git. Crie um repositório
vazio (ex.: `eletroia`) na sua conta do GitHub e me passe a URL — eu adiciono o remote e
faço o primeiro push (o Git Credential Manager do Windows deve abrir uma janela de login
do GitHub no seu navegador na hora do push; isso é normal e é você autenticando, não eu).

## 3. Backend (Render)

1. Crie uma conta grátis em https://render.com.
2. **New + → Blueprint**, aponte para o repositório — o arquivo `render.yaml` na raiz já
   descreve o serviço (`eletroia-api`, Docker, `apps/api/Dockerfile`).
3. Preencha as variáveis de ambiente pedidas: `DATABASE_URL` (a string do Neon),
   `ANTHROPIC_API_KEY` (sua chave da Anthropic), `CORS_ORIGINS` (deixe em branco por
   enquanto — voltamos aqui depois de ter a URL do Vercel).
4. Deploy. A URL final será algo como `https://eletroia-api.onrender.com`.

## 4. Frontend (Vercel)

1. Crie uma conta grátis em https://vercel.com (login com GitHub facilita a importação).
2. **Add New → Project**, importe o mesmo repositório.
3. Em **Root Directory**, selecione `apps/web`.
4. Em **Environment Variables**, adicione `NEXT_PUBLIC_API_URL` = URL do Render (passo 3).
5. Deploy. A URL final será algo como `https://eletroia.vercel.app`.

## 5. Fechar o CORS

Volte ao Render, edite `CORS_ORIGINS` do serviço `eletroia-api` para a URL do Vercel (ex.:
`https://eletroia.vercel.app`), e re-deploy o backend. Sem esse passo o frontend em
produção não consegue chamar a API (bloqueio de CORS).

## Depois disso

Qualquer `git push` na branch principal atualiza automaticamente o Vercel e o Render.
