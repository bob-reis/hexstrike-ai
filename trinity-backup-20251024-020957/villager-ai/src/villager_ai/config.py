# Villager Configuration - Fixed for MCP SERVER setup
import os
import uuid

# Generate a unique server UUID
SERVER_UUID = str(uuid.uuid4())

# Villager operates as MCP SERVER (not client)
# Remove the MCP client configuration entirely
# Villager will be called by Cursor via MCP protocol

# LLM Provider Configuration - Flexible for multiple AI agent models
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')  # Options: 'agent-zero', 'deepseek', 'openai', 'custom', 'ollama'

# Agent Zero Configuration (Default)
AGENT_ZERO_URL = os.getenv('AGENT_ZERO_URL', 'http://localhost:50001')

# DeepSeek AI Configuration (Alternative)
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')

# OpenAI Configuration (Alternative)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')

# Custom LLM Configuration (Alternative)
CUSTOM_LLM_URL = os.getenv('CUSTOM_LLM_URL', '')
CUSTOM_LLM_API_KEY = os.getenv('CUSTOM_LLM_API_KEY', '')

# Ollama Configuration (Local LLM)
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'deepseek-r1-uncensored')

# Set environment variables based on provider
if LLM_PROVIDER == 'agent-zero':
    os.environ['OPENAI_API_KEY'] = 'agent-zero'  # Placeholder for Agent Zero
    os.environ['OPENAI_API_BASE'] = AGENT_ZERO_URL
elif LLM_PROVIDER == 'deepseek':
    os.environ['OPENAI_API_KEY'] = DEEPSEEK_API_KEY
    os.environ['OPENAI_API_BASE'] = DEEPSEEK_BASE_URL
elif LLM_PROVIDER == 'openai':
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    os.environ['OPENAI_API_BASE'] = OPENAI_BASE_URL
elif LLM_PROVIDER == 'custom':
        os.environ['OPENAI_API_KEY'] = CUSTOM_LLM_API_KEY
        os.environ['OPENAI_API_BASE'] = CUSTOM_LLM_URL
elif LLM_PROVIDER == 'ollama':
        os.environ['OPENAI_API_KEY'] = 'ollama'  # Placeholder for Ollama
        os.environ['OPENAI_API_BASE'] = OLLAMA_BASE_URL

# Server Configuration
HOST = os.getenv('VILLAGER_HOST', '0.0.0.0')
PORT = int(os.getenv('VILLAGER_PORT', '37695'))

# Security Configuration - FULL ACCESS for red team operations
ALLOW_SHELL = os.getenv('ALLOW_SHELL', '1') == '1'
ALLOW_APT = os.getenv('ALLOW_APT', '1') == '1'
ALLOW_WRITE = os.getenv('ALLOW_WRITE', '1') == '1'
ALLOW_BUILD = os.getenv('ALLOW_BUILD', '1') == '1'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'villager.log')

# Master Configuration (required by Villager)
class Master:
    """Master configuration class required by Villager."""
    
    def __init__(self):
        # Configure based on selected provider
        if LLM_PROVIDER == 'agent-zero':
            self.api_key = 'agent-zero'
            self.openai_api_key = 'agent-zero'
            self.base_url = AGENT_ZERO_URL
            self.model = "gpt-4"  # Agent Zero uses OpenAI-compatible models
            self.default_model = "gpt-4"
            self.openai_api_endpoint = AGENT_ZERO_URL
        elif LLM_PROVIDER == 'deepseek':
            self.api_key = DEEPSEEK_API_KEY
            self.openai_api_key = DEEPSEEK_API_KEY
            self.base_url = DEEPSEEK_BASE_URL
            self.model = "deepseek-chat"
            self.default_model = "deepseek-chat"
            self.openai_api_endpoint = DEEPSEEK_BASE_URL
        elif LLM_PROVIDER == 'openai':
            self.api_key = OPENAI_API_KEY
            self.openai_api_key = OPENAI_API_KEY
            self.base_url = OPENAI_BASE_URL
            self.model = "gpt-4"
            self.default_model = "gpt-4"
            self.openai_api_endpoint = OPENAI_BASE_URL
        elif LLM_PROVIDER == 'custom':
            self.api_key = CUSTOM_LLM_API_KEY
            self.openai_api_key = CUSTOM_LLM_API_KEY
            self.base_url = CUSTOM_LLM_URL
            self.model = "gpt-4"
            self.default_model = "gpt-4"
            self.openai_api_endpoint = CUSTOM_LLM_URL
        elif LLM_PROVIDER == 'ollama':
            self.api_key = 'ollama'
            self.openai_api_key = 'ollama'
            self.base_url = OLLAMA_BASE_URL
            self.model = OLLAMA_MODEL
            self.default_model = OLLAMA_MODEL
            self.openai_api_endpoint = OLLAMA_BASE_URL
        
        # Common settings
        self.temperature = 0.7
        self.max_tokens = 4000
        self.timeout = 30
        
    def get(self, key):
        """Get configuration value by key."""
        if key == "prefix":
            return "You are a helpful AI assistant with access to shell commands and system tools. "
        elif key == "misc":
            return self.get_misc_config()
        return getattr(self, key, None)
        
    def get_llm_config(self):
        """Get LLM configuration for DeepSeek AI."""
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout
        }
    
    def get_misc_config(self):
        """Get miscellaneous configuration for Villager tools."""
        return {
            "shell_encode": "utf-8"
        }

# Security validation
if LLM_PROVIDER == 'deepseek' and not DEEPSEEK_API_KEY:
    raise ValueError("❌ DEEPSEEK_API_KEY must be set when using 'deepseek' provider. Set it via environment variable.")
if LLM_PROVIDER == 'openai' and not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY must be set when using 'openai' provider. Set it via environment variable.")

# MCP Configuration (required by Villager)
class MCP:
    """MCP configuration class required by Villager."""
    
    def __init__(self):
        self.client = {
            'base_url': 'http://localhost:25989',  # Villager's MCP Client port
            'timeout': 30
        }
        self.server = {
            'base_url': 'http://localhost:25989',  # Villager's MCP Client port
            'kali_driver': 'http://localhost:1611',  # Kali Driver port
            'browser_use': 'http://localhost:8080',  # Browser automation port
            'timeout': 30
        }
        self.enabled = True
        
    def __getitem__(self, key):
        """Make MCP subscriptable."""
        return getattr(self, key, None)
        
    def get(self, key):
        """Get configuration value by key."""
        return getattr(self, key, None)

# Create instances
Master = Master()
MCP = MCP()