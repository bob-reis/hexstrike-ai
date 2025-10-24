#!/usr/bin/env python3
"""
🎯 HexStrike AI - Integração de Logging Persistente
Integra o sistema de logging com o servidor HexStrike AI
"""

import os
import json
import datetime
import subprocess
import shlex
from pathlib import Path
from typing import Dict, Any, Optional

class PentestLogger:
    """Sistema de logging persistente para pentest ético"""

    def __init__(self):
        """Inicializar o sistema de logging"""
        self.pentest_date = datetime.datetime.now().strftime('%Y%m%d')
        self.base_dir = Path.home() / f"pentest-{self.pentest_date}"
        self.log_dir = self.base_dir / "logs"
        self.output_dir = self.base_dir / "outputs"
        self.evidence_dir = self.base_dir / "evidence"
        self.reports_dir = self.base_dir / "reports"
        self.screenshots_dir = self.base_dir / "screenshots"

        # Arquivos de log
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        self.command_log = self.log_dir / f"commands-{timestamp}.log"
        self.full_log = self.log_dir / f"full-session-{timestamp}.log"
        self.error_log = self.log_dir / f"errors-{timestamp}.log"

        # Inicializar estrutura
        self._init_directory_structure()

    def _init_directory_structure(self):
        """Criar estrutura de diretórios"""
        directories = [
            self.log_dir,
            self.output_dir,
            self.evidence_dir,
            self.reports_dir,
            self.screenshots_dir
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        # Criar arquivo de metadados da sessão
        session_info = {
            "session_start": datetime.datetime.now().isoformat(),
            "pentest_date": self.pentest_date,
            "base_directory": str(self.base_dir),
            "operator": os.getenv('USER', 'unknown'),
            "hostname": os.getenv('HOSTNAME', 'unknown'),
            "os_info": dict(zip(['sysname', 'nodename', 'release', 'version', 'machine'], os.uname())) if hasattr(os, 'uname') else 'unknown'
        }

        with open(self.base_dir / "session-info.json", 'w') as f:
            json.dump(session_info, f, indent=2)

        # Criar README
        self._create_readme()

    def _create_readme(self):
        """Criar arquivo README com instruções"""
        readme_content = f"""# 🎯 Pentest Session: {self.pentest_date}

## 📁 Estrutura de Diretórios

- **logs/**: Logs completos da sessão, comandos executados e erros
- **outputs/**: Saídas brutas de todas as ferramentas
- **evidence/**: Evidências organizadas para relatório
- **reports/**: Relatórios finais e documentação
- **screenshots/**: Capturas de tela e evidências visuais

## 🔧 Comandos Úteis

```bash
# Ver comandos executados
tail -f logs/commands-*.log

# Ver log completo da sessão
tail -f logs/full-session-*.log

# Ver apenas erros
tail -f logs/errors-*.log

# Listar todas as saídas salvas
ls -la outputs/

# Buscar por padrões nos logs
grep -r "VULNERABLE" logs/
```

## 🎯 Sessão Iniciada em: {datetime.datetime.now()}
"""

        with open(self.base_dir / "README.md", 'w') as f:
            f.write(readme_content)

    def log_command(self, command: str, output: str, error: str = "", exit_code: int = 0):
        """Registrar comando executado com sua saída"""
        timestamp = datetime.datetime.now().isoformat()

        # Criar nome de arquivo para a saída
        safe_cmd = "".join(c for c in command if c.isalnum() or c in ".-_")[:50]
        output_filename = f"{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}-{safe_cmd}.txt"
        output_file = self.output_dir / output_filename

        # Registrar comando no log de comandos
        with open(self.command_log, 'a') as f:
            status = "✅ SUCESSO" if exit_code == 0 else f"❌ ERRO ({exit_code})"
            f.write(f"[{timestamp}] {status}: {command}\\n")
            f.write(f"[{timestamp}] OUTPUT_FILE: {output_file}\\n")

        # Salvar saída completa
        with open(output_file, 'w') as f:
            f.write(f"# Comando executado em: {timestamp}\\n")
            f.write(f"# Comando: {command}\\n")
            f.write(f"# Operador: {os.getenv('USER')}@{os.getenv('HOSTNAME')}\\n")
            f.write(f"# Código de saída: {exit_code}\\n")
            f.write("# ======================================\\n\\n")

            if output:
                f.write("# STDOUT:\\n")
                f.write(output)
                f.write("\\n\\n")

            if error:
                f.write("# STDERR:\\n")
                f.write(error)
                f.write("\\n\\n")

            f.write(f"# ======================================\\n")
            f.write(f"# Comando concluído em: {datetime.datetime.now().isoformat()}\\n")

        # Registrar no log completo
        with open(self.full_log, 'a') as f:
            f.write(f"[{timestamp}] COMANDO: {command}\\n")
            f.write(f"OUTPUT_FILE: {output_file}\\n")
            f.write("========================================\\n")
            if output:
                f.write(output)
                f.write("\\n")
            if error:
                f.write("STDERR:\\n")
                f.write(error)
                f.write("\\n")
            f.write("\\n")

        # Registrar erros separadamente se houver
        if exit_code != 0:
            with open(self.error_log, 'a') as f:
                f.write(f"[{timestamp}] ❌ ERRO ({exit_code}): {command}\\n")
                if error:
                    f.write(f"STDERR: {error}\\n")
                f.write("\\n")

        return str(output_file)

    def execute_and_log(self, command: str) -> Dict[str, Any]:
        """Executar comando e registrar automaticamente"""
        try:
            # Executar comando
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos de timeout
            )

            # Registrar resultado
            output_file = self.log_command(
                command=command,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode
            )

            return {
                "success": result.returncode == 0,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "output_file": output_file,
                "timestamp": datetime.datetime.now().isoformat()
            }

        except subprocess.TimeoutExpired:
            error_msg = f"Comando '{command}' excedeu timeout de 5 minutos"
            output_file = self.log_command(
                command=command,
                output="",
                error=error_msg,
                exit_code=124  # Código padrão para timeout
            )

            return {
                "success": False,
                "command": command,
                "stdout": "",
                "stderr": error_msg,
                "exit_code": 124,
                "output_file": output_file,
                "timestamp": datetime.datetime.now().isoformat()
            }

        except Exception as e:
            error_msg = f"Erro ao executar comando: {str(e)}"
            output_file = self.log_command(
                command=command,
                output="",
                error=error_msg,
                exit_code=1
            )

            return {
                "success": False,
                "command": command,
                "stdout": "",
                "stderr": error_msg,
                "exit_code": 1,
                "output_file": output_file,
                "timestamp": datetime.datetime.now().isoformat()
            }

    def save_evidence(self, description: str, content: str, source_file: Optional[str] = None):
        """Salvar evidência importante"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        safe_desc = "".join(c for c in description if c.isalnum() or c in ".-_")
        evidence_file = self.evidence_dir / f"{timestamp}-{safe_desc}.txt"

        with open(evidence_file, 'w') as f:
            f.write(f"# EVIDÊNCIA: {description}\\n")
            f.write(f"# Data: {datetime.datetime.now().isoformat()}\\n")
            f.write(f"# Operador: {os.getenv('USER')}@{os.getenv('HOSTNAME')}\\n")
            if source_file:
                f.write(f"# Arquivo origem: {source_file}\\n")
            f.write("# ======================================\\n\\n")
            f.write(content)

        return str(evidence_file)

    def generate_summary_report(self) -> str:
        """Gerar relatório resumo da sessão"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        report_file = self.reports_dir / f"summary-{timestamp}.md"

        # Coletar estatísticas
        total_commands = 0
        successful_commands = 0
        failed_commands = 0

        if self.command_log.exists():
            with open(self.command_log, 'r') as f:
                lines = f.readlines()
                total_commands = len([l for l in lines if "COMANDO:" in l or "✅ SUCESSO:" in l or "❌ ERRO" in l])
                successful_commands = len([l for l in lines if "✅ SUCESSO:" in l])
                failed_commands = len([l for l in lines if "❌ ERRO" in l])

        # Contar arquivos
        output_count = len(list(self.output_dir.glob("*")))
        evidence_count = len(list(self.evidence_dir.glob("*")))
        screenshot_count = len(list(self.screenshots_dir.glob("*")))

        report_content = f"""# 🎯 Relatório Resumo - Pentest {self.pentest_date}

## 📊 Estatísticas da Sessão

- **Data**: {datetime.datetime.now()}
- **Operador**: {os.getenv('USER')}@{os.getenv('HOSTNAME')}
- **Comandos executados**: {total_commands}
- **Sucessos**: {successful_commands}
- **Erros**: {failed_commands}

## 📁 Arquivos Gerados

- **Outputs**: {output_count} arquivos
- **Evidências**: {evidence_count} arquivos
- **Screenshots**: {screenshot_count} arquivos

## 🔍 Comandos Mais Executados

[Esta seção seria populada com análise dos logs]

## ❌ Últimos Erros

[Esta seção seria populada com últimos erros do error_log]

---
*Relatório gerado automaticamente pelo HexStrike AI Logging System*
"""

        with open(report_file, 'w') as f:
            f.write(report_content)

        return str(report_file)

    def get_session_stats(self) -> Dict[str, Any]:
        """Obter estatísticas da sessão atual"""
        stats = {
            "base_directory": str(self.base_dir),
            "session_date": self.pentest_date,
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "output_files": len(list(self.output_dir.glob("*"))),
            "evidence_files": len(list(self.evidence_dir.glob("*"))),
            "screenshot_files": len(list(self.screenshots_dir.glob("*")))
        }

        if self.command_log.exists():
            with open(self.command_log, 'r') as f:
                lines = f.readlines()
                stats["total_commands"] = len([l for l in lines if "✅ SUCESSO:" in l or "❌ ERRO" in l])
                stats["successful_commands"] = len([l for l in lines if "✅ SUCESSO:" in l])
                stats["failed_commands"] = len([l for l in lines if "❌ ERRO" in l])

        return stats

# Instância global do logger
pentest_logger = None

def init_pentest_logging():
    """Inicializar o sistema de logging global"""
    global pentest_logger
    pentest_logger = PentestLogger()
    return pentest_logger

def get_pentest_logger():
    """Obter instância do logger (inicializar se necessário)"""
    global pentest_logger
    if pentest_logger is None:
        pentest_logger = PentestLogger()
    return pentest_logger

# Funções de conveniência
def log_command(command: str, output: str, error: str = "", exit_code: int = 0):
    """Registrar comando com logging"""
    logger = get_pentest_logger()
    return logger.log_command(command, output, error, exit_code)

def execute_and_log(command: str):
    """Executar comando com logging automático"""
    logger = get_pentest_logger()
    return logger.execute_and_log(command)

def save_evidence(description: str, content: str, source_file: Optional[str] = None):
    """Salvar evidência"""
    logger = get_pentest_logger()
    return logger.save_evidence(description, content, source_file)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python hexstrike-logging-integration.py <comando>")
        print("Comandos:")
        print("  init    - Inicializar sistema de logging")
        print("  exec    - Executar comando com logging")
        print("  stats   - Mostrar estatísticas")
        print("  report  - Gerar relatório resumo")
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        logger = init_pentest_logging()
        print(f"✅ Sistema de logging inicializado em: {logger.base_dir}")

    elif command == "exec":
        if len(sys.argv) < 3:
            print("Uso: python hexstrike-logging-integration.py exec <comando>")
            sys.exit(1)

        cmd_to_execute = " ".join(sys.argv[2:])
        logger = get_pentest_logger()
        result = logger.execute_and_log(cmd_to_execute)

        print(f"Comando: {result['command']}")
        print(f"Sucesso: {result['success']}")
        print(f"Código de saída: {result['exit_code']}")
        print(f"Arquivo de saída: {result['output_file']}")

        if result['stdout']:
            print("\\nSTDOUT:")
            print(result['stdout'])

        if result['stderr']:
            print("\\nSTDERR:")
            print(result['stderr'])

    elif command == "stats":
        logger = get_pentest_logger()
        stats = logger.get_session_stats()

        print("🎯 Estatísticas da Sessão de Pentest")
        print("====================================")
        for key, value in stats.items():
            print(f"{key}: {value}")

    elif command == "report":
        logger = get_pentest_logger()
        report_file = logger.generate_summary_report()
        print(f"📋 Relatório gerado: {report_file}")

    else:
        print(f"❌ Comando desconhecido: {command}")
        sys.exit(1)