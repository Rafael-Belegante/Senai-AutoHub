
# Senai AutoHub

Repositório de materiais (documentos e vídeos) para o SENAI, com três perfis:

- **Admin**: gerencia usuários e materiais, executa backup.
- **Professor**: cadastra materiais e, posteriormente, alunos.
- **Aluno**: acessa, pesquisa e abre materiais disponíveis.

Projeto baseado em **FastAPI + SQLAlchemy + Jinja2**, preparado para evoluir para produção.

---

## 1. Requisitos

- Python 3.10+
- Pip / Virtualenv

Instalação de dependências:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2. Estrutura básica

- `app/` – código da aplicação (rotas, modelos, serviços).
- `templates/` – HTML com Jinja2.
- `static/` – CSS e JS.
- `uploads/materials/` – arquivos enviados.
- `backups/` – base para rotina de backup (scripts futuros).

---

## 3. Inicialização do banco e admin padrão

Antes de rodar a API, inicialize o banco e crie o admin padrão:

```bash
python -m app.db.init_db
```

Isso cria o arquivo `senai_autohub.db` e o usuário admin (se não existir).

### Admin padrão

> **IMPORTANTE: troque esses valores em produção (via `.env`).**

- E-mail: `admin@senai.autohub`
- Senha: `Admin123!`

Você pode sobrescrever em um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=chave-muito-segura-aqui
CSRF_SECRET=outra-chave-bem-segura
DATABASE_URL=sqlite:///./senai_autohub.db
ADMIN_EMAIL=admin@senai.autohub
ADMIN_PASSWORD=SuaSenhaForteAqui123!
```

---

## 4. Rodando o servidor

Após instalar dependências e inicializar o banco:

```bash
uvicorn app.main:app --reload
```

Acesse em: http://127.0.0.1:8000

Rotas principais:

- `/` – lista de materiais com busca e filtro por tipo.
- `/auth/login` – tela de login.
- `/materials/dashboard` – dashboard do professor/admin.
- `/materials/new` – cadastro de novo material.
- `/admin/users` – listagem de usuários (somente admin).

Swagger/OpenAPI: http://127.0.0.1:8000/docs

---

## 5. Fluxo de acesso

1. **Primeiro login**: somente o **admin padrão** consegue acessar (não existe mais ninguém no sistema).
2. Admin autentica em `/auth/login`.
3. Admin cria professores (futuras rotas/procedimentos – já há listagem em `/admin/users` para visualização).
4. Professores logam e passam a cadastrar materiais e, futuramente, alunos (via convites/tokens).

> Como não há rota pública de cadastro, **nenhum aluno ou professor** consegue se criar sozinho.  
> Isso garante que **apenas o admin padrão** tem acesso inicial ao sistema.

---

## 6. Produção / Hardening

Para uso real, recomenda-se:

- Usar banco PostgreSQL com URL em `DATABASE_URL`.
- Servir via servidor ASGI robusto (ex.: uvicorn + nginx).
- Ativar `secure=True` no cookie de sessão (já previsto em `core/security.py`).
- Configurar domínios permitidos em CORS.
- Implementar rotinas de:
  - Backup agendado (`backups/`).
  - Criação/edição de usuários via painel admin.
  - Rate limiting para login.

---

## 7. Próximos passos sugeridos

- Implementar fluxo completo de **convite de aluno** usando `InviteToken`.
- Criar telas para o admin cadastrar/editar **professores** pelo front.
- Implementar telas de visualização de materiais acessados pelos alunos (auditoria).

Este projeto já está pronto para ser rodado em ambiente de homologação e adaptado para produção.
