# Checklist de Pentest em Thick Client

Baseado no checklist OWASP (80+ casos) com notas adicionais para integração com HexStrike, BOAZ e Villager. Referência original: https://hariprasaanth.notion.site/THICK-CLIENT-PENTESTING-CHECKLIST-35c6803f26eb4c9d89ba7f5fdc901fb0

## Preparação e Automação

- Estruture o projeto em `~/pentests/<cliente>/<data>/` com `recon/`, `exploitation/`, `evidence/`, `reports/`, `notes/`.
- Inicialize serviços auxiliares (HexStrike, Villager, BOAZ) e confirme conectividade (MCP `list_tools`).
- Mantenha `notes/log.csv` para todos os comandos/scripts; salve dumps e capturas em `evidence/`.
- Registrar hashes de executáveis e bibliotecas antes/depois da análise; documentar payloads BOAZ em `payloads.md`.
- Use Villager para orquestrar tarefas (ex.: instrumentação, interceptação de tráfego) e HexStrike para análises complementares (binário, rede, API).

## COLETA DE INFORMAÇÕES

- Identificar arquitetura da aplicação (two-tier / three-tier).
- Identificar tecnologias (linguagens, frameworks).
- Mapear comunicação de rede (protocolos, portas, endpoints).
- Observar processos, funcionalidades, comportamento geral.
- Identificar pontos de entrada (UI, arquivos, rede, registros, plugins).
- Analisar mecanismos de segurança (auth, autorização, criptografia).

**Ferramentas:** CFF Explorer, Sysinternals Suite, Wireshark, PEiD, Detect It Easy (DIE), `strings`.

**Notas automação:**
- HexStrike: scripts para varredura de portas, fingerprinting de serviços backend.
- Villager: tarefas para acompanhar execução do cliente (process monitor + network capture).
- Registrar dumps e capturas em `recon/`.

## TESTES GUI

- **Permissões de Objetos GUI:** revelar objetos ocultos, ativar funcionalidades desabilitadas, exibir senhas mascaradas.
- **Conteúdo da GUI:** procurar dados sensíveis.
- **Lógica da GUI:** testar controles de acesso, injeções, bypass por funções legítimas, tratamento de erros/inputs, escalada de privilégio (ativar recursos admin), manipulação de pagamento.

**Ferramentas:** UISpy, WinSpy++, Window Detective, Snoop WPF.

**Integração:**
- Registrar capturas (prints, vídeos) em `evidence/gui/`.
- Utilizar Villager para automatizar interações repetitivas.

## TESTES DE ARQUIVOS

- **Permissões:** verificar permissões de arquivos/pastas (leitura, escrita, execução).
- **Continuidade:** validar strong naming, assinatura de código.
- **Conteúdo/Debugar:** buscar dados sensíveis (config, logs, símbolos, senhas, chaves, side-channel), checar armazenamento em texto claro.
- **Manipulação:** testar backdooring de framework, preloading de DLL, race conditions, substituição de arquivos/conteúdo, bypass client-side por engenharia reversa.
- **Funções Exportadas:** localizar funções exportadas e tentar chamá-las sem autenticação.
- **Métodos Públicos:** criar wrappers para acessar métodos sem autenticação.
- **Decompilar/Recompilar:** recuperar código fonte, senhas, chaves, recompilar/patch.
- **Desobfuscação/Decriptação:** validar obfuscação, extrair segredos.
- **Montagem:** desmontar/reassemblar (assemblies patchados).

**Ferramentas:** `strings`, dnSpy, Procmon, Process Explorer, Process Hacker.

**Integração:**
- HexStrike: `strings`, `binwalk`, scripts Python para analisar recursos.
- BOAZ: gerar payloads (DLLs, binários) para testar preloading/hijacking.
- Villager: agendar execuções repetidas para observar alterações em arquivos/logs.

## REGISTRO (REGISTRY)

- **Permissões:** leitura/escrita em chaves relevantes.
- **Conteúdo:** procurar dados sensíveis; comparar antes/depois da execução.
- **Manipulação:** tentar bypass de autenticação/autorização via alterações de registro.

**Ferramentas:** Regshot, Procmon, AccessEnum.

**Integração:**
- Scripts HexStrike/Villager para snapshot e diff automático do registry.

## REDE

- Monitorar dados sensíveis em trânsito.
- Testar bypass de firewall/IDS.
- Manipular tráfego (replay, MITM, modificação).

**Ferramentas:** Wireshark, TCPView.

**Integração:**
- HexStrike: scripts `mitmproxy`, `scapy`, `responder` se aplicável.
- Villager: orquestrar captura de tráfego e replay.
- Documentar pacotes relevantes em `evidence/network/`.

## ASSEMBLY / PROTEÇÕES BINÁRIAS

- Verificar ASLR, SafeSEH, DEP, ControlFlowGuard, HighEntropyVA, strong naming.

**Ferramentas:** PESecurity, CFF Explorer, DIE.

**Integração:** registrar resultados em `reports/assembly.md`.

## MEMÓRIA

- **Conteúdo:** checar se dados sensíveis residem na memória (strings, tokens, chaves).
- **Manipulação:** tentar alterar memória para bypass de autenticação/autorização.
- **Tempo de Execução:** analisar dumps, substituição de processos, patch em memória, depuração, identificação de funções perigosas, breakpoints.

**Ferramentas:** Process Hacker, HxD, `strings`, depuradores (x64dbg, WinDbg).

**Integração:**
- Registrar dumps (minidumps) em `evidence/memory/` com hashes.
- Villager: tarefas automatizadas para gerar dumps pós-ação.

## TRÁFEGO

- Analisar fluxo de tráfego; procurar dados sensíveis.
- Ferramentas: Echo Mirage, MITM Relay, Burp Suite.

**Integração:**
- HexStrike: apoiar com scripts HTTP/SMB/LDAP para replays.
- Villager: agendar capturas e manipulações.

## VULNERABILIDADES COMUNS

- Eng. reversa, decompiler, OWASP Web Top 10 / API Top 10.
- DLL Hijacking, verificação de assinatura (Sigcheck), análise binária (Binscope/VCG).
- Erros de lógica de negócio.
- Ataques TCP/UDP.
- Scans automatizados (Visual Code Grepper, Sonar, etc.).

**Integração final:**
- HexStrike: automatizar varreduras (ex.: `nuclei`, `sqlmap` no backend exposto).
- BOAZ: criar cargas customizadas para testar hijacking.
- Villager: consolidar tarefas e gerar relatório incremental.

## Relatório e Encerramento

- Atualizar `reports/report-draft.md` com achados associados às seções acima.
- Anexar evidências (hashes, dumps, capturas) e checklist preenchido.
- Sanitizar segredos antes de compartilhar.
- Documentar IDs de tarefas do Villager, payloads BOAZ e comandos HexStrike usados.
