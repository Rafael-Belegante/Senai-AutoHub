# Senai AutoHub -- Repositório de Materiais

Sistema web para armazenamento e gerenciamento de materiais educacionais
do **SENAI**, estruturado com:

-   **FastAPI**
-   **SQLAlchemy**
-   **Jinja2 Templates**

Com três níveis de acesso:

-   **Admin** --- gerencia usuários, materiais e backup.
-   **Professor** --- gerencia alunos e materiais.
-   **Aluno** --- acessa e pesquisa materiais.

------------------------------------------------------------------------

## 1. Requisitos

-   Python **3.10+**
-   Pip + Virtualenv

Instalação das dependências:

``` bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

------------------------------------------------------------------------

## 2. Inicialização do Banco + Admin Padrão

Antes de rodar o sistema:

``` bash
python -m app.db.init_db
```

Isso cria o banco (`senai_autohub.db`) e o **usuário admin inicial**
caso ele não exista.

### Admin padrão (pode ser configurado via `.env`)

-   **Email:** `admin@senai.autohub`
-   **Senha:** `Admin123!`

Para customizar, crie um arquivo `.env` na raiz:

``` env
SECRET_KEY=sua-chave-segura
CSRF_SECRET=outra-chave-segura
DATABASE_URL=sqlite:///./senai_autohub.db
ADMIN_EMAIL=admin@senai.autohub
ADMIN_PASSWORD=SenhaForte123!
```

------------------------------------------------------------------------

## 3. Rodando o Servidor

Após instalar dependências e inicializar o banco:

``` bash
uvicorn app.main:app --reload
```

Acesse:

    http://127.0.0.1:8000

Documentação automática:

    http://127.0.0.1:8000/docs

------------------------------------------------------------------------

## 4. Principais Rotas

### Autenticação

  Método   Rota             Descrição
  -------- ---------------- -------------------
  GET      `/auth/login`    Tela de login
  POST     `/auth/login`    Autentica usuário
  GET      `/auth/logout`   Logout

------------------------------------------------------------------------

### Materiais (Admin + Professor)

  Rota                       Descrição
  -------------------------- ------------------------
  `/materials/dashboard`     Dashboard de materiais
  `/materials/new`           Criar material
  `/materials/{id}/edit`     Editar
  `/materials/{id}/delete`   Excluir

------------------------------------------------------------------------

### Admin --- Usuários

  Rota                                Tipo       Descrição
  ----------------------------------- ---------- ------------------
  `/admin/users`                      GET        Listar usuários
  `/admin/users/new`                  GET/POST   Criar usuário
  `/admin/users/{id}/edit`            GET/POST   Editar usuário
  `/admin/users/{id}/toggle-active`   POST       Ativar/desativar

------------------------------------------------------------------------

### Admin --- Backup

  Rota                  Tipo   Descrição
  --------------------- ------ -----------------
  `/admin/backup`       GET    Tela de backup
  `/admin/backup/run`   POST   Executar backup

------------------------------------------------------------------------

### Professor/Admin --- Alunos

  Rota                      Tipo       Descrição
  ------------------------- ---------- -----------------
  `/students/manage`        GET        Listar alunos
  `/students/new`           GET/POST   Criar aluno
  `/students/{id}/edit`     GET/POST   Editar aluno
  `/students/{id}/delete`   POST       Desativar aluno

------------------------------------------------------------------------

### Público --- Alunos

  Rota               Descrição
  ------------------ --------------------
  `/`                Lista de materiais
  `/material/{id}`   Abrir material

------------------------------------------------------------------------

## 5. Estrutura Básica

    senai_autohub/
    │
    ├── app/
    │   ├── main.py
    │   ├── models/
    │   ├── routes/
    │   ├── services/
    │   ├── core/
    │   └── db/
    │
    ├── templates/
    ├── static/
    ├── uploads/materials/
    ├── backups/
    │
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

## 6. Resumo do Processo de Execução

1.  Criar ambiente virtual\
2.  Instalar dependências\
3.  Iniciar banco e admin padrão\
4.  Rodar servidor FastAPI\
5.  Logar com admin, configurar usuários e usar o sistema

Pronto para uso em ambiente local, podendo ser adaptado facilmente para
produção.
