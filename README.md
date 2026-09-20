# Projeto DevOps SDD — Task API

Projeto acadêmico para demonstrar SDD, CI/CD, Docker, SonarCloud e deploy automático em AWS EC2.

## Arquitetura e entregáveis

- API CRUD: FastAPI + SQLite;
- especificação: `docs/SDD.md`;
- testes: Pytest + cobertura;
- container: Docker e Docker Compose;
- scanner: SonarCloud com quality gate;
- pipeline: GitHub Actions;
- ambiente: uma EC2 Ubuntu.

## Rodar localmente

Com Docker:

```bash
docker compose up --build
```

Abra `http://localhost:8000/docs`. Para testar:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Preparar apresentação","description":"Registrar evidências"}'
curl http://localhost:8000/tasks
```

Sem Docker:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest --cov=app
uvicorn app.main:app --reload
```

## Passo a passo completo: GitHub, SonarCloud e AWS

### 1. Personalize o projeto

Edite os nomes dos integrantes neste README e substitua em `sonar-project.properties`:

- `SUBSTITUA_PELO_PROJECT_KEY` pelo Project Key do SonarCloud;
- `SUBSTITUA_PELA_ORGANIZATION` pela Organization Key do SonarCloud.

### 2. Crie o repositório GitHub

Crie um repositório vazio (por exemplo `projeto-devops-sdd`) e, na raiz deste projeto:

```bash
git init
git add .
git commit -m "feat: projeto DevOps SDD inicial"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/projeto-devops-sdd.git
git push -u origin main
```

O primeiro push falhará no Sonar até os passos 3 e 6 estarem configurados; isso é esperado.

### 3. Configure o SonarCloud

1. Entre em `https://sonarcloud.io` usando o GitHub.
2. Importe o repositório em **Analyze new project**.
3. Copie a Organization Key e Project Key para `sonar-project.properties` e faça commit/push.
4. Em **My Account > Security**, gere um token.
5. No GitHub, abra **Settings > Secrets and variables > Actions > New repository secret** e crie `SONAR_TOKEN`.
6. No SonarCloud, confirme que o Quality Gate está ativo. A pipeline só fará deploy se ele passar.

### 4. Crie a EC2

No console AWS, região de sua preferência:

1. EC2 > **Launch instance**;
2. nome: `task-api-devops`;
3. AMI: **Ubuntu Server 24.04 LTS**;
4. tipo: `t3.micro` (ou elegível ao free tier da conta);
5. crie/baixe uma chave `.pem` e guarde-a;
6. armazenamento: 8 GiB é suficiente;
7. Security Group com:
   - SSH/TCP 22: **My IP** (não deixe aberto para todos);
   - HTTP/TCP 80: `0.0.0.0/0` e `::/0`;
8. inicie a instância e anote o **Public IPv4**. Para um endereço estável, associe um Elastic IP.

Custos dependem da conta e região. Encerre os recursos após a avaliação se não precisar mais deles.

### 5. Instale Docker na EC2

No seu computador:

```bash
chmod 400 sua-chave.pem
ssh -i sua-chave.pem ubuntu@IP_PUBLICO
```

Dentro da EC2, você pode copiar e executar `scripts/setup-ec2.sh`, ou executar:

```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker ubuntu
sudo systemctl enable --now docker
exit
```

Conecte novamente e valide:

```bash
docker --version
```

### 6. Crie os segredos do GitHub Actions

Em **GitHub > repositório > Settings > Secrets and variables > Actions**, crie:

| Secret | Valor |
|---|---|
| `SONAR_TOKEN` | token gerado no SonarCloud |
| `EC2_HOST` | IPv4 público ou Elastic IP da EC2 |
| `EC2_USER` | `ubuntu` |
| `EC2_SSH_KEY` | conteúdo completo da chave `.pem`, incluindo BEGIN/END |
| `GHCR_TOKEN` | GitHub Personal Access Token classic com `read:packages` |

Crie o PAT em GitHub > Settings do usuário > Developer settings > Personal access tokens > Tokens (classic). Se o pacote GHCR ficar público, o token ainda simplifica o pull automatizado.

### 7. Execute a pipeline e valide

Faça um novo push:

```bash
git add .
git commit -m "ci: configurar ambiente"
git push
```

Em **Actions**, acompanhe `CI, Security and Deploy`. Depois do job verde, abra:

- `http://IP_PUBLICO/health` — deve retornar `{"status":"ok"}`;
- `http://IP_PUBLICO/docs` — interface Swagger para demonstrar o CRUD.

Na EC2, diagnóstico útil:

```bash
docker ps
docker logs --tail 100 task-api
curl http://localhost/health
```

## Evidências para a apresentação

Capture: repositório e commits da dupla; documento SDD; testes/cobertura; workflow verde; relatório/quality gate do SonarCloud; imagem no GHCR; EC2 em execução; `/health` e CRUD no Swagger. Explique que o deploy só acontece após testes e scanner aprovados.

## Integrantes

- Nome 1 — matrícula
- Nome 2 — matrícula
