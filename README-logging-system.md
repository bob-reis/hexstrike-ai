# 🎯 HexStrike AI - Sistema de Logging Persistente

Um sistema completo de logging para pentest ético que salva todas as saídas de comandos em `$HOME/pentest-$DATA` com histórico persistente e organização automática.

## 🚀 Instalação Rápida

```bash
# Executar script de configuração automática
cd /opt/hexstrike-ai
./setup-pentest-logging.sh

# Reiniciar terminal ou recarregar configurações
source ~/.bashrc
```

## 📁 Estrutura de Diretórios

O sistema cria automaticamente a seguinte estrutura organizacional:

```
$HOME/pentest-YYYYMMDD/
├── logs/                           # Logs da sessão
│   ├── commands-YYYYMMDD-HHMMSS.log    # Histórico de comandos
│   ├── full-session-YYYYMMDD-HHMMSS.log # Log completo da sessão
│   ├── errors-YYYYMMDD-HHMMSS.log      # Log de erros
│   └── bash_history-YYYYMMDD-HHMMSS.log # Histórico do bash
├── outputs/                        # Saídas de ferramentas
│   └── YYYYMMDD-HHMMSS-comando.txt     # Output de cada comando
├── evidence/                       # Evidências organizadas
│   └── YYYYMMDD-HHMMSS-descrição.txt   # Evidências específicas
├── reports/                        # Relatórios finais
│   └── summary-YYYYMMDD-HHMMSS.md      # Relatórios de resumo
├── screenshots/                    # Capturas de tela
│   └── YYYYMMDD-HHMMSS-descrição.png   # Screenshots
├── session-info.json              # Metadados da sessão
└── README.md                       # Instruções da sessão
```

## 🛠️ Componentes do Sistema

### 1. **pentest-logger.sh** - Sistema de Logging Principal
- Funções para logging automático de comandos
- Wrappers para ferramentas comuns (nmap, sqlmap, gobuster, etc.)
- Gestão de evidências e screenshots
- Geração de relatórios resumo

### 2. **hexstrike-logging-integration.py** - Integração Python
- API Python para logging programático
- Integração com o servidor HexStrike AI
- Execução e logging automático de comandos
- Geração de metadados estruturados

### 3. **setup-pentest-logging.sh** - Configuração Automática
- Instalação e configuração completa
- Integração com bash (.bashrc)
- Criação de aliases globais
- Configuração de hooks de comando

## 🎯 Como Usar

### Comandos Principais

```bash
# Inicializar ambiente do dia
pentest-init

# Ver status atual
pentest-status

# Ver logs recentes
pentest-logs

# Buscar nos logs
pentest-search "VULNERABLE"

# Gerar relatório resumo
pentest-summary

# Salvar evidência importante
save_evidence "SQL Injection encontrada" "/tmp/sqlmap-output.txt"

# Capturar screenshot
take_screenshot "Página de admin acessível"
```

### Ferramentas com Logging Automático

Todas estas ferramentas agora são logadas automaticamente:

**Reconnaissance:**
- `nmap` → `nmap_logged`
- `masscan`, `zmap`, `rustscan`

**Web Testing:**
- `sqlmap` → `sqlmap_logged`
- `gobuster` → `gobuster_logged`
- `nikto` → `nikto_logged`
- `dirb`, `wfuzz`, `ffuf`

**Network Testing:**
- `netcat`, `ncat`, `socat`
- `netdiscover`, `arp-scan`

**Exploitation:**
- `msfconsole`, `msfvenom`
- `searchsploit`

**Password Attacks:**
- `hydra`, `medusa`, `john`, `hashcat`

E muitas outras...

### Integração com HexStrike Server

```bash
# Enviar comando via API
hexstrike_api "nmap -sV -sC target.com"

# Usar alias
hexapi "gobuster dir -u http://target.com -w /usr/share/wordlists/common.txt"
```

## 📊 Exemplos Práticos

### Sessão de Pentest Típica

```bash
# 1. Inicializar ambiente
pentest-init

# 2. Reconnaissance (automaticamente logado)
nmap -sV -sC -oA target target.com

# 3. Web fuzzing (automaticamente logado)
gobuster dir -u http://target.com -w /usr/share/wordlists/common.txt

# 4. SQL injection testing (automaticamente logado)
sqlmap -u "http://target.com/page.php?id=1" --dbs

# 5. Salvar evidência importante
save_evidence "Admin panel encontrado" "http://target.com/admin/"

# 6. Capturar screenshot
take_screenshot "Página de login vulnerável"

# 7. Ver estatísticas
pentest-status

# 8. Gerar relatório final
pentest-summary
```

### Análise de Resultados

```bash
# Buscar por vulnerabilidades
pentest-search "VULNERABLE"
pentest-search "exploit"
pentest-search "password"

# Ver comandos que falharam
grep "❌ ERRO" logs/commands-*.log

# Listar todas as evidências
ls -la evidence/

# Ver relatório mais recente
cat reports/summary-*.md
```

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

```bash
# Personalizar diretório base
export PENTEST_BASE_DIR="$HOME/meus-pentests/$(date +%Y%m%d)"

# Configurar descrição padrão para API
export PENTEST_API_DESCRIPTION="Comando personalizado"

# Configurar projetos específicos
export BURP_PROJECT_DIR="$PENTEST_BASE_DIR/burp-projects"
export METASPLOIT_LOG_DIR="$PENTEST_BASE_DIR/metasploit-logs"
```

### Hooks Personalizados

O sistema inclui hooks que capturam automaticamente todos os comandos executados no terminal, mantendo um histórico completo da sessão de pentest.

### Integração com Systemd

O sistema pode ser configurado para inicializar automaticamente:

```bash
# Habilitar serviço do usuário
systemctl --user enable hexstrike-logging.service
systemctl --user start hexstrike-logging.service
```

## 📋 API Python

### Uso Programático

```python
from hexstrike_logging_integration import get_pentest_logger

# Obter logger
logger = get_pentest_logger()

# Executar comando com logging
result = logger.execute_and_log("nmap -sV target.com")

# Salvar evidência
logger.save_evidence("Porta SSH aberta", "22/tcp open ssh")

# Gerar relatório
report = logger.generate_summary_report()

# Obter estatísticas
stats = logger.get_session_stats()
```

### Integração com Scripts

```python
#!/usr/bin/env python3
import subprocess
from hexstrike_logging_integration import execute_and_log, save_evidence

# Executar nmap e logar automaticamente
result = execute_and_log("nmap -sV -sC target.com")

if result['success']:
    # Salvar resultado como evidência
    save_evidence("Scan inicial completo", result['stdout'])
else:
    print(f"Erro no scan: {result['stderr']}")
```

## 🔍 Troubleshooting

### Problemas Comuns

**1. Diretórios não são criados:**
```bash
# Verificar permissões
ls -la $HOME/
# Reinicializar
pentest-init
```

**2. Comandos não são logados:**
```bash
# Verificar se o sistema foi carregado
which pentest_run
# Recarregar configurações
source ~/.bashrc
```

**3. Integração com servidor não funciona:**
```bash
# Verificar se servidor está rodando
curl http://localhost:8888/health
# Verificar logs
tail -f logs/errors-*.log
```

### Logs de Debug

```bash
# Ver logs completos
tail -f logs/full-session-*.log

# Ver apenas erros
tail -f logs/errors-*.log

# Debug do bash
set -x
pentest_run "echo teste"
set +x
```

## 🗑️ Desinstalação

```bash
# Executar script de desinstalação
/opt/hexstrike-ai/uninstall-pentest-logging.sh

# Ou manualmente:
rm -rf ~/.local/bin/pentest-logger
rm -rf ~/.local/bin/hexstrike-logger
rm -f ~/.hexstrike_aliases

# Restaurar .bashrc do backup
cp ~/.bashrc.backup-* ~/.bashrc
```

## 📈 Estatísticas e Relatórios

### Métricas Coletadas

- **Comandos executados**: Total, sucessos, falhas
- **Duração da sessão**: Tempo total de pentest
- **Ferramentas utilizadas**: Frequência de uso
- **Arquivos gerados**: Outputs, evidências, screenshots
- **Padrões encontrados**: Vulnerabilidades, exploits, credenciais

### Formato dos Relatórios

Os relatórios são gerados em Markdown e incluem:
- Estatísticas da sessão
- Lista de arquivos gerados
- Comandos mais executados
- Erros encontrados
- Timeline da sessão

## 🔒 Considerações de Segurança

### Dados Sensíveis

- ❌ **Não committar** diretórios de pentest no git
- ✅ **Criptografar** evidências sensíveis
- ✅ **Usar** permissões restritivas (700) nos diretórios
- ✅ **Limpar** dados temporários após o pentest

### Compliance

O sistema é projetado para compliance com:
- **OWASP Testing Guide**
- **NIST Cybersecurity Framework**
- **ISO 27001** (documentação de testes)
- **PCI DSS** (testes de segurança)

## 🤝 Contribuindo

Para melhorar o sistema:

1. **Issues**: Reporte bugs ou sugestões
2. **Pull Requests**: Contribua com melhorias
3. **Documentação**: Ajude a melhorar este README
4. **Testes**: Adicione casos de teste

## 📜 Licença

Sistema desenvolvido como parte do HexStrike AI para uso em pentesting ético e defensive security.

---

**🎯 Sistema de Logging Persistente para Pentest Ético**
*Nunca mais perca evidências importantes - tudo é automaticamente logado e organizado!*