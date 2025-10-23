# Checklist de Pentest em Aplicações Web

Baseado na checklist OWASP (500+ casos de teste) com notas adicionais para uso integrado de HexStrike, BOAZ e Villager. Referência original: https://hariprasaanth.notion.site/WEB-APPLICATION-PENTESTING-CHECKLIST-0f02d8074b9d4af7b12b8da2d46ac998

## Preparação e Automação

- Estruture o projeto em `~/pentests/<cliente>/<data>/` com `recon/`, `exploitation/`, `evidence/`, `reports/`, `notes/`.
- Configure e valide os MCPs (HexStrike, BOAZ, Villager); confirme `list_tools`.
- Mantenha diário (`notes/claude-session-YYYYMMDD.md`) e log (`notes/log.csv`).
- Salve saídas completas em `recon/` ou `exploitation/`; evidências em `evidence/` com hashes.
- Registre payloads BOAZ (loader, encoding, hash) em `payloads.md`.
- Use Villager para orquestrar fases (Recon → Auth → Exploit → Relatório) e HexStrike para execuções pontuais.

## COLETA DE INFORMAÇÕES

### Reconhecimento em Código Aberto
- Realizar buscas com Google Dorks.
- Executar OSINT (Whois, redes sociais, vazamentos).

### Fingerprinting do Servidor Web
- Identificar tipo e versão do servidor web.

### Metafiles
- Verificar `robots.txt`, `sitemap.xml`, `humans.txt`, `security.txt`.

### Enumeração de Aplicações
- Executar Nmap e Netcat.
- Realizar DNS lookup e reverse DNS.

### Revisão do Conteúdo Web
- Inspecionar código-fonte, scripts JavaScript, chaves embutidas.
- Verificar desabilitação de autocomplete.

### Pontos de Entrada
- Identificar métodos suportados e pontos de injeção.

### Caminhos de Execução
- Burp Suite, Dirsearch, Gobuster.

### Fingerprinting de Framework
- Wappalyzer, WhatWeb, extensões, HTML, cookies, headers.

### Arquitetura da Aplicação
- Mapear estrutura geral do site.

**Automação:** HexStrike (`httpx`, `katana`, `nuclei`); Villager para tasks OSINT. Armazenar resultados em `recon/`.

## CONFIGURAÇÃO E DEPLOYMENT

- Verificar configurações de rede e credenciais padrão.
- Confirmar módulos obrigatórios, resistência a DoS, tratamento de erros, logs.
- Controlar extensões sensíveis/maliciosas e testar upload.
- Validar arquivos não referenciados e backups.
- Procurar interfaces de infra/admin ocultas.
- Descobrir métodos HTTP permitidos e validar PUT/OPTIONS, bypass, XST, override.
- Confirmar HSTS e políticas cross-domain.
- Checar permissões de arquivos e enumeração de diretórios.
- Avaliar takeover de subdomínio (DNS/CNAME/NS, 404).
- Verificar storage em nuvem (AWS/GCP/Azure) em busca de caminhos expostos.

**Automação:** HexStrike (`nmap`, `gobuster`, `aws s3`), Villager para sequências automatizadas.

## GERENCIAMENTO DE IDENTIDADE

- Testar forced browsing, IDOR, manipulação de parâmetros, privilégio mínimo.
- Revisar processo de registro (duplicidade, verificação, e-mails descartáveis, provas).
- Avaliar provisionamento/deprovisionamento (admin, auto-desprovisionamento, recursos).
- Inspecionar respostas para credenciais válidas/invalidas; garantir rate limit.
- Monitorar enumeração de usernames.

**Automação:** HexStrike para brute force controlado; Villager para cenários de registro/provisionamento.

## AUTENTICAÇÃO

- Garantir que páginas de login/registro/reset/mudança usem HTTPS.
- Testar credenciais padrão e manipulações.
- Validar lockout e CAPTCHA.
- Verificar bypass (forced browsing, previsão de sessão, tampering, SQLi, reuso de sessão, logins simultâneos).
- Revisar funções “lembrar senha” (armazenamento seguro).
- Confirmar cabeçalhos de cache adequados.
- Validar política de senhas (complexidade, reuso, min/max).
- Avaliar perguntas de segurança (complexidade, brute force).
- Revisar reset de senha (dados, HTTP, tokens, rate limit, expiração).
- Revisar troca de senha (senha antiga, sessões destruídas).
- Testar autenticação em canais alternativos (desktop/móvel, idiomas, países).

**Automação:** HexStrike para brute force/lockout; Villager para fluxos multi-canal.

## AUTORIZAÇÃO

- Testar LFI/RFI em URL e cookies.
- Aplicar codificações (Base64, URL, ASCII, HTML, Hex, Binário, Octal, Gzip, dupla codificação).
- Verificar traversal em esquemas Unix/Windows/Mac.
- Testar bypass horizontal/vertical e cabeçalhos customizados.
- Validar escalada de privilégio (forced browsing, IDOR, tampering).
- Testar IDOR (IDs, parâmetros, HPP, extensões, versões antigas, array/JSON, case, método, path traversal).

**Automação:** HexStrike (`wfuzz`, `ffuf`); BOAZ para payloads em upload; Villager para workflows de autorização.

## GERENCIAMENTO DE SESSÃO

- Verificar `Set-Cookie` seguro/HttpOnly, canal criptografado, expiração, fixação, login simultâneo, comportamento pós logout/fechamento, decodificação.
- Confirmar flags `Secure`, `Path`, `HttpOnly`.
- Garantir nova sessão após login.
- Testar exposição de variáveis de sessão (GET/POST, troca método).
- Validar ataques back/refresh.
- Testar CSRF (token server-side, tamanho, múltiplas contas, POST↔GET, remoção/modificação do token, content-type, referer/host, com clickjacking).
- Avaliar logout (visibilidade, término de sessão, back button, timeout).
- Confirmar timeout de sessão e destruição de tokens.
- Mapear variáveis de sessão (session puzzling) e tentar quebrar fluxo.
- Testar hijacking (ausência de HSTS, uso de cookies capturados).

**Automação:** HexStrike scripts (CSRF, cookies); Villager para cenários multi-dispositivo.

## VALIDAÇÃO / INJEÇÃO

- XSS refletido: filtros, escapes, encoding, newline, double encode, recursion, payload sem whitespace, alteração de método.
- XSS armazenado: parâmetros persistentes, uploads, tags HTML.
- HTTP Parameter Pollution.
- SQLi: login/busca/campos editáveis (GET/POST/COOKIE/HEADER), null byte, URL encode, mix case, tamper, time/boolean, uso de sqlmap.
- LDAP Injection.
- XML Injection/XXE.
- Server Side Includes (SSI).
- XPATH Injection.
- IMAP/SMTP Injection.
- LFI/RFI (keywords, null byte).
- Command Injection (delimitadores, comandos OS).
- Format String Injection.
- Host Header Injection (Host, X-Forwarded, duplos, prefixos/sufixos, password reset poisoning).
- SSRF (keywords, cabeçalhos, exploração interna/externa).
- Server Side Template Injection (identificar engine, usar tplmap ou payloads).

**Automação:** HexStrike (`sqlmap`, `wfuzz`, `nuclei`), BOAZ (payloads ofuscados), Villager (tarefas encadeadas).

## TRATAMENTO DE ERROS

- Avaliar mensagens, códigos, inconsistências; induzir erros em parâmetros, uploads, entradas inesperadas.

## CRIPTOGRAFIA / TLS

- Testar DROWN, POODLE, BEAST, FREAK, ciphers nulos, NOMORE (RC4), LUCKY13, CRIME, LOGJAM.
- Garantir certificados ≥ 2048 bits, SHA-256, cadeia válida; evitar MD5/SHA-1.
- Revisar cipher suites fracos.

**Automação:** HexStrike (`nmap --script ssl-enum-ciphers`, `testssl.sh`).

## LÓGICA DE NEGÓCIO

- Entender fluxos e botões; testar valores extremos, quantidades, pagamentos, tampering.
- Upload malicioso (payloads XSS/RCE/LFI/RFI/SQL, RTLO, encoded, payload dentro de imagem, arquivos grandes).

**HexStrike/BOAZ:** combinar payloads e registrar efeitos.

## CLIENT-SIDE

- XSS DOM: identificar sinks, construir payloads.
- Redirecionamento: parâmetros, payload list, whitelist, subdomínios, XSS, URLs de perfil.
- CORS: verificar `Access-Control-Allow-Origin`, explorar via HTML.
- Clickjacking: confirmar `X-Frame-Options`, criar POC com iframe.

## OUTROS PROBLEMAS

- Rate limiting: confirmar existência, tentar bypass por case, barra, cabeçalhos (únicos e duplos), Origin, IP rotation, null bytes, race conditions.
- EXIF geodata: garantir remoção, usar analisador EXIF.
- Broken link hijack: testar links com `blc`.
- SPF: confirmar registro e testar com `nslookup`.
- 2FA fraco: bypass via sessão, OAuth, brute force, manipulação de resposta/status, links de ativação, alteração de e-mail/senha, entradas nulas, boolean false, remoção de parâmetros.
- OTP fraco: reutilização, brute force, entradas vazias, manipulação de resposta/status.

**Automação:** HexStrike para rate limit, 2FA/OTP; Villager para cenários multi-canal e race conditions.

## ENCERRAMENTO / RELATÓRIO

- Consolidar achados em `reports/report-draft.md` alinhado ao checklist.
- Documentar evidência, reprodução, impacto, recomendação, referência.
- Sanitizar tokens/chaves antes de compartilhar artefatos.
- Arquivar checklist preenchido junto ao relatório final.
- Registrar IDs de tarefas do Villager e hashes de payloads BOAZ.
