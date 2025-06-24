"""
Configuration management for mem0-mcp
"""
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:
    """Application configuration"""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    mode: str = "full"  # "basic" or "full"
    
    # MCP settings
    server_name: str = "mem0-mcp"
    
    # Mem0 settings
    mem0_api_key: Optional[str] = None
    default_user_id: str = "cursor_mcp"
    
    # Deployment settings
    is_render: bool = False
    is_production: bool = False
    
    # Feature flags
    enable_advanced_tools: bool = True
    enable_custom_instructions: bool = True
    enable_health_check: bool = True
    enable_cors: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables"""
        config = cls()
        
        # Server settings
        config.host = os.getenv("HOST", config.host)
        config.port = int(os.getenv("PORT", str(config.port)))
        config.debug = os.getenv("DEBUG", "").lower() in ("true", "1", "yes")
        config.mode = os.getenv("MODE", config.mode)
        
        # MCP settings
        config.server_name = os.getenv("SERVER_NAME", config.server_name)
        
        # Mem0 settings
        config.mem0_api_key = os.getenv("MEM0_API_KEY")
        config.default_user_id = os.getenv("DEFAULT_USER_ID", config.default_user_id)
        
        # Deployment detection
        config.is_render = bool(os.getenv("RENDER"))
        config.is_production = (
            config.is_render or 
            os.getenv("ENVIRONMENT", "").lower() == "production"
        )
        
        # Feature flags
        config.enable_advanced_tools = (
            os.getenv("ENABLE_ADVANCED_TOOLS", "true").lower() != "false"
        )
        config.enable_custom_instructions = (
            os.getenv("ENABLE_CUSTOM_INSTRUCTIONS", "true").lower() != "false"
        )
        config.enable_health_check = (
            os.getenv("ENABLE_HEALTH_CHECK", "true").lower() != "false"
        )
        config.enable_cors = (
            os.getenv("ENABLE_CORS", "true").lower() != "false"
        )
        
        # Logging
        config.log_level = os.getenv("LOG_LEVEL", config.log_level)
        
        # Mode overrides
        if config.mode == "basic":
            config.enable_advanced_tools = False
        
        return config
    
    def validate(self) -> list[str]:
        """
        Validate configuration
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required settings
        if not self.mem0_api_key:
            errors.append("MEM0_API_KEY is required")
        
        # Validate port
        if not (1 <= self.port <= 65535):
            errors.append(f"Invalid port: {self.port}")
        
        # Validate mode
        if self.mode not in ("basic", "full"):
            errors.append(f"Invalid mode: {self.mode}")
        
        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            errors.append(f"Invalid log level: {self.log_level}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "mode": self.mode,
            "server_name": self.server_name,
            "mem0_api_key": "***" if self.mem0_api_key else None,
            "default_user_id": self.default_user_id,
            "is_render": self.is_render,
            "is_production": self.is_production,
            "enable_advanced_tools": self.enable_advanced_tools,
            "enable_custom_instructions": self.enable_custom_instructions,
            "enable_health_check": self.enable_health_check,
            "enable_cors": self.enable_cors,
            "log_level": self.log_level
        }
    
    def __str__(self) -> str:
        """String representation"""
        return f"Config(mode={self.mode}, host={self.host}:{self.port}, production={self.is_production})"


# Global config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.from_env()
    return _config_instance


def reset_config() -> None:
    """Reset the global config instance (useful for testing)"""
    global _config_instance
    _config_instance = None