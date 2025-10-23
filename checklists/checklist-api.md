# Checklist de Segurança para APIs

Lista das medidas mais importantes a considerar ao projetar, testar e publicar uma API. Mantivemos o conteúdo base e adicionamos notas específicas para o uso combinado de HexStrike, BOAZ e Villager.

## Preparação e Automação

- Estruture o projeto em `~/pentests/<cliente>/<data>/` com subpastas: `recon/`, `exploitation/`, `evidence/`, `reports/`, `notes/`.
- Inicialize o HexStrike (`HEXSTRIKE_HOST=0.0.0.0 python3 hexstrike_server.py --port 8888`) e garanta que os MCPs de BOAZ e Villager carregam sem erros (somente JSON).
- Registre os wrappers MCP no Claude/5ire; confirme que os comandos `list_tools` respondem.
- Mantenha um diário da sessão (`notes/claude-session-YYYYMMDD.md`) para referenciar nas conversas e economizar tokens.
- Cada execução deve entrar em `notes/log.csv` (timestamp, ferramenta, comando, resumo, caminho do artefato).
- Salve saídas completas (`.log`, `.json`) em `recon/` ou `exploitation/`; registre payloads BOAZ (loader, encoding, hash) em `payloads.md`.

## Enumeração

- Utilize fuzzers para descobrir novas rotas (diferentes profundidades).
- Enumere endpoints restritos; tente variações de caminho (`..;/`, codificações, barras duplas).
- Modifique requisições adicionando parâmetros extras (`&admin=true`).
- **HexStrike:** executar ferramentas como `katana`, `httpx_probe`, `dirsearch` e arquivar saídas em `recon/` com referência no log.
- **Villager:** criar tarefas automatizadas para varredura de endpoints e parâmetros.

## Autenticação

- Evite Basic Auth; prefira padrões como JWT ou OAuth2.
- Não reinventar geração de tokens ou armazenamento de senhas; use bibliotecas confiáveis.
- Aplicar limite de tentativas e bloqueios (Max Retry + jail).
- Criptografar dados sensíveis (em repouso e em trânsito).
- Não permitir reutilização de tokens antigos.
- **Automação:** usar HexStrike para simular brute force controlado, verificando bloqueios.
- **Villager:** orquestrar fluxos de autenticação (MFA, reset de senha) e registrar respostas.

## JWT (JSON Web Token)

- Use segredo forte e imprevisível.
- Não inferir algoritmo do cabeçalho; fixe HS256 ou RS256 no backend.
- Tokens com curta validade (TTL/RTTL).
- Não armazenar dados sensíveis no payload (decodificação simples).
- Evitar payloads grandes (limite de cabeçalhos HTTP).
- Rever lista de ataques (Invicti).
- **HexStrike:** executar testes de downgrade de algoritmo, tampering de assinatura, `kid` injection.

## Controle de Acesso

- Aplicar rate limit/throttling.
- Usar HTTPS (TLS 1.2+) com cifras fortes.
- Habilitar HSTS (evita SSL Strip).
- Desativar listagem de diretórios.
- Restringir APIs privadas a IPs/hosts safelists.
- **Villager:** agendar testes de bypass (IP rotation, manipulação de cabeçalhos) e registrar resultados.

## Autorização / OAuth

- Validar `redirect_uri` no servidor (URLs autorizadas).
- Prefira fluxo Authorization Code (evite `response_type=token`).
- Use parâmetro `state` aleatório para impedir CSRF no consentimento OAuth.
- Definir escopos padrão e conferir parâmetros por aplicação.
- **Villager:** automatizar tentativas de troca de código, manipulação de `state`/`nonce` e escopos.

## Entrada de Dados (Input)

- Sanitizar entradas; escapar caracteres perigosos.
- Utilizar método HTTP correto (GET, POST, PUT/PATCH, DELETE); retornar 405 quando inadequado.
- Validar cabeçalho `Accept` e responder 406 se não houver formato suportado.
- Validar `Content-Type` (form-data, JSON, x-www-form-urlencoded, etc.) e responder 415 se divergente.
- Testar contra XSS, SQLi, RCE, XXE e similares.
- Não transportar credenciais, tokens ou chaves em URLs; use cabeçalho Authorization.
- Manipular cabeçalhos `Referer` que possam ser esperados.
- Aplicar criptografia no servidor.
- Utilizar API Gateway para caching e políticas de rate limit (Quota, Spike Arrest, Concurrent Rate Limit).
- Testar upload de arquivos, tamanhos atípicos e tipos inesperados.
- Avaliar CSRF quando a API compartilha autenticação com aplicações web.
- Atenção ao IDOR em corpo/cabeçalho (ex.: `{ "id": { "id": 111 } }`).
- **HexStrike:** testar payloads com `ffuf`, `wfuzz`, `sqlmap`, `xsser`, XML/YAML bombs e registrar evidências.
- **BOAZ:** subir payloads ofuscados para avaliar filtros de upload.
- **Villager:** tasks para schema validations e expansão exponencial (XXE, Billion Laughs).

## Processamento (Backend)

- Proteger todos os endpoints; evitar autenticação quebrada.
- Preferir `/me/recursos` no lugar de IDs explícitos.
- Utilizar UUID em vez de auto-incrementos.
- Desativar parsing de entidades externas (XML/ YAML) e expansão exponencial.
- Usar CDN para uploads.
- Para processos pesados, delegar a workers/queues; evitar bloqueios HTTP prolongados.
- Desligar `DEBUG`; confirmar via análise de resposta.
- Habilitar stacks não executáveis se possível.
- Testar se `GET`/`POST`/`DELETE` indevidos permitem operações indevidas.
- **Villager:** monitorar fila de tarefas (Agent Scheduler) e documentar execuções.
- **Logs:** compilar entradas relevantes de `hexstrike.log`, `villager` e `mcp` em `reports/processing.md`.

## Saída (Output)

- Enviar `X-Content-Type-Options: nosniff`.
- Enviar `X-Frame-Options: deny`.
- Enviar `Content-Security-Policy: default-src 'none'`.
- Remover cabeçalhos de fingerprint (`X-Powered-By`, `Server`, etc.).
- Forçar `Content-Type` adequado (JSON => `application/json`).
- Não retornar dados sensíveis (credenciais, tokens, chaves).
- Retornar código HTTP coerente (200, 400, 401, 405, etc.).
- Limitar parâmetros potencialmente abusivos (`/api/news?limit=9999999999`).
- **HexStrike:** capturar cabeçalhos via `curl -i`, `nuclei` e armazenar em `evidence/headers/`.
- **Villager:** criar rotinas para validar cabeçalhos de segurança periodicamente.

## Monitoramento e Observabilidade

- Centralizar logs de todos os serviços.
- Monitorar tráfego, erros e padrões de requisição/resposta.
- Configurar alertas (SMS, Slack, Email, Telegram, Kibana, CloudWatch etc.).
- Não registrar dados sensíveis (cartões, senhas, PINs) em logs.
- Empregar IDS/IPS para vigiar acessos e hosts.
- **Projeto:** gerar resumo diário com logs do HexStrike, Villager e BOAZ em `reports/monitoring.md`.
- **Villager:** agendar health-checks para conferir HSTS, rate limit e alertas de IDS.

## Relatório e Encerramento

- Produzir relatório incremental em `reports/report-draft.md`, alinhado às seções do checklist.
- Para cada achado: evidência, passos de reprodução, impacto, recomendação, referências.
- Registrar hashes de scripts/binários em `evidence/hashes.txt`.
- Sanitizar tokens/chaves antes de compartilhar artefatos.
- Arquivar checklist preenchido junto ao relatório final.

