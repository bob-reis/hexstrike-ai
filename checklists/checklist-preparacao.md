# Checklist de Preparação para Pentests

Lista de tarefas prévias a qualquer engajamento, consolidando práticas discutidas (estruturação, registro, automação e integração de ferramentas).

## 1. Organização Inicial
- [ ] Confirmar autorização formal (NDA, carta de escopo, regras de engajamento).
- [ ] Criar repositório/branch do projeto (Git ou equivalente) e registrar autoria.
- [ ] Estruturar diretório base `~/pentests/<cliente>/<data>/` com pastas:
  - `recon/`
  - `exploitation/`
  - `evidence/`
  - `reports/`
  - `notes/`
  - `payloads/` (opcional, para BOAZ ou artefatos).
- [ ] Criar arquivo de log estruturado `notes/log.csv` com cabeçalho (data/hora, ferramenta, comando, resumo, caminho da evidência).
- [ ] Criar diário de sessões `notes/claude-session-YYYYMMDD.md` (um por dia ou por sessão de trabalho).
- [ ] Opcional: inicializar ambiente Python/virtualenv específico do cliente.

## 2. Configuração de Serviços (HexStrike / BOAZ / Villager)
- [ ] Verificar que `hexstrike_env` está atualizado (`pip install -r requirements.txt`).
- [ ] Iniciar HexStrike com suporte externo: `HEXSTRIKE_HOST=0.0.0.0 python3 hexstrike_server.py --port 8888`.
- [ ] Checar logs (`hexstrike.log`) e limpar arquivos antigos, se necessário.
- [ ] Confirmar pasta BOAZ (`/opt/hexstrike-ai/BOAZ_beta`) e dependências instaladas (`requirements.sh`).
- [ ] Garantir `.env` do Villager configurado (provider LLM, chaves, host/portas) e wrappers (`villager_mcp_wrapper.sh`) executáveis.
- [ ] Opcional: instalar dependências extras (ex.: `matplotlib`) se exigidas por Villager.
- [ ] Registrar versões das ferramentas em `reports/versions.md`.

## 3. Configuração MCP / Clientes
- [ ] Atualizar `~/.config/Claude/claude_desktop_config.json` (ou configs equivalentes no 5ire/Cursor) com entradas:
  - `hexstrike-ai-v2` → `/opt/hexstrike-ai/hexstrike_mcp_wrapper.sh --server http://<ip>:8888`
  - `boaz-mcp` → `python3 /opt/BOAZ-MCP/boaz_mcp_server.py` (com `BOAZ_PATH`)
  - `villager-proper` → `/opt/villager-ai-hexstrike-integration/villager_mcp_wrapper.sh`
- [ ] Testar `list_tools` de cada MCP (via Claude/5ire) para garantir handshake sem erros.
- [ ] Se o cliente for Windows (p. ex. 5ire), configurar wrappers via SSH (`ssh user@vm .../wrapper.sh`).
- [ ] Registrar em `notes/log.csv` a data/hora de validação MCP.

## 4. Logs, Evidence e Captura
- [ ] Configurar rotação de logs conforme necessidade (`logrotate` ou manual).
- [ ] Criar diretório `evidence/screenshots/` e `evidence/logs/`.
- [ ] Definir formato de nome para arquivos (ex.: `YYYYMMDD-HHMM-<ferramenta>.log`).
- [ ] Preparar comandos com `tee`/redirecionamento para salvar saídas automaticamente em `recon/` ou `exploitation/`.
- [ ] Registrar as primeiras entradas de `log.csv` (setup, validações, versões).
- [ ] Criar arquivo `reports/report-draft.md` com seções padrão (resumo, recon, análise, exploração, pós-exploração, recomendações).
- [ ] Criar `reports/monitoring.md` para anotar status de logs/alertas diários.

## 5. Gestão de Chaves e Credenciais
- [ ] Armazenar chaves API (OpenAI, DeepSeek, GitHub) em local seguro (.env, vault).
- [ ] Registrar em `notes/credentials.txt` (ou solução segura) as fontes autorizadas; nunca inserir tokens em repositórios.
- [ ] Habilitar/validar ferramentas de gestão de segredos (1Password, Vault, etc.).
- [ ] Configurar tokens do GitHub (se usar funcionalidades do Villager) e documentar permissões concedidas.

## 6. Planejamento Técnico
- [ ] Anotar escopo detalhado em `notes/scope.md` (IPs, domínios, APIs, thick clients, restrições).
- [ ] Definir metodologia e ferramentas para cada fase (ex.: Recon -> HexStrike/katana; Web -> `checklists/checklist-web.md`).
- [ ] Criar matriz de responsabilidade (quem executa qual etapa, prazos).
- [ ] Preparar planilha `payloads/payloads-tracker.csv` para BOAZ (loader, encoding, hash, alvo).
- [ ] Se necessário, preparar lab/teste isolado (VMs, containers, snapshots).

## 7. Health Checks Rápidos
- [ ] HexStrike: `curl http://<ip>:8888/health` e registrar no log.
- [ ] Villager: `./villager_mcp_wrapper.sh --help` (sem erros), logs limpos (sem ANSI).
- [ ] BOAZ: `python3 /opt/BOAZ-MCP/boaz_mcp_server.py --help` ou executar ferramenta `boaz_list_loaders` via MCP.
- [ ] Ferramentas externas: `nmap --version`, `sqlmap --version`, `burpsuite` (caso aplicável).

## 8. Checklist em Produção
- [ ] Vincular cada checklist específico (API, Web, Thick Client) ao projeto; duplicar/riscar itens conforme andamento.
- [ ] Atualizar `checklists/status.md` com progresso (percentual por fase).
- [ ] Estabelecer rotina diária de commit/backup das notas.
- [ ] Garantir que scripts customizados fiquem em `scripts/` dentro do projeto, com README de uso.

## 9. Encerramento Preparatório
- [ ] Revisar se todas as tarefas acima foram marcadas.
- [ ] Arquivar checklist preenchido em `reports/checklist-preparacao-final.md`.
- [ ] Agendar primeira reunião de kick-off com o cliente.

> **Dica:** reutilize este checklist como template (“modelos/pentest-preparacao.md”) e versione melhorias.
