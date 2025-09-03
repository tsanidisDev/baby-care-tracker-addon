#!/usr/bin/env python3
"""
Utilities module for Baby Care Tracker
Common utility functions and configuration helpers
"""

import os
import json
import logging
import yaml
from datetime import datetime
from typing import Dict, Any, Optional

def setup_logging(log_level: str = 'info') -> logging.Logger:
    """Setup logging configuration"""
    
    # Convert string log level to logging constant
    level_map = {
        'trace': logging.DEBUG,
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'notice': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'fatal': logging.CRITICAL
    }
    
    level = level_map.get(log_level.lower(), logging.INFO)
    
    # Create logs directory
    os.makedirs('/data/logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Console output
            logging.FileHandler('/data/logs/baby_care_tracker.log', mode='a')  # File output
        ]
    )
    
    # Set specific log levels for noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('paho').setLevel(logging.WARNING)
    
    logger = logging.getLogger('baby_care_tracker')
    logger.info(f"Logging initialized at level: {log_level}")
    
    return logger

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables and options"""
    
    config = {}
    
    # Load from environment variables (set by run.sh)
    env_mappings = {
        'MQTT_BROKER': 'mqtt_broker',
        'MQTT_USERNAME': 'mqtt_username', 
        'MQTT_PASSWORD': 'mqtt_password',
        'DATABASE_TYPE': 'database_type',
        'LOG_LEVEL': 'log_level',
        'ENABLE_ANALYTICS': 'enable_analytics',
        'EXPORT_ENABLED': 'export_enabled',
        'TIMEZONE': 'timezone'
    }
    
    for env_var, config_key in env_mappings.items():
        value = os.getenv(env_var)
        if value:
            # Convert boolean strings
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            config[config_key] = value
    
    # Load from add-on options file if available
    try:
        with open('/data/options.json', 'r') as f:
            addon_options = json.load(f)
            config.update(addon_options)
    except FileNotFoundError:
        pass  # Not running as add-on
    except Exception as e:
        logging.warning(f"Could not load add-on options: {e}")
    
    # Set defaults
    defaults = {
        'mqtt_broker': 'core-mosquitto',
        'mqtt_username': '',
        'mqtt_password': '',
        'database_type': 'sqlite',
        'log_level': 'info',
        'enable_analytics': True,
        'export_enabled': True,
        'timezone': 'UTC',
        'debug': False,
        'ha_discovery': True,
        'auto_cleanup': False,
        'cleanup_days': 365,
        'daily_reports': False
    }
    
    for key, default_value in defaults.items():
        if key not in config:
            config[key] = default_value
    
    return config

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration"""
    
    required_keys = ['mqtt_broker', 'database_type', 'log_level']
    
    for key in required_keys:
        if key not in config:
            logging.error(f"Missing required configuration key: {key}")
            return False
    
    # Validate specific values
    valid_db_types = ['sqlite', 'postgresql']
    if config['database_type'] not in valid_db_types:
        logging.error(f"Invalid database type: {config['database_type']}. Must be one of: {valid_db_types}")
        return False
    
    valid_log_levels = ['trace', 'debug', 'info', 'notice', 'warning', 'error', 'fatal']
    if config['log_level'] not in valid_log_levels:
        logging.error(f"Invalid log level: {config['log_level']}. Must be one of: {valid_log_levels}")
        return False
    
    return True

def get_version_info() -> Dict[str, str]:
    """Get version information"""
    return {
        'addon_version': '2.0.0',
        'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        'build_date': datetime.now().isoformat()
    }

def ensure_data_directories():
    """Ensure all required data directories exist"""
    directories = [
        '/data',
        '/data/database',
        '/data/exports', 
        '/data/logs',
        '/data/backups'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string"""
    
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        return f"{hours}h"

def format_time_ago(timestamp: datetime) -> str:
    """Format timestamp as 'time ago' string"""
    
    now = datetime.now()
    if timestamp.tzinfo:
        now = now.replace(tzinfo=timestamp.tzinfo)
    
    diff = now - timestamp
    seconds = int(diff.total_seconds())
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem usage"""
    
    import re
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def create_backup(source_dir: str, backup_name: str) -> str:
    """Create a backup of the specified directory"""
    
    import shutil
    import tarfile
    
    backup_dir = '/data/backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"{backup_name}_{timestamp}.tar.gz"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        with tarfile.open(backup_path, 'w:gz') as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        
        logging.info(f"Backup created: {backup_path}")
        return backup_path
        
    except Exception as e:
        logging.error(f"Error creating backup: {e}")
        raise

def cleanup_old_files(directory: str, days: int = 30, pattern: str = "*"):
    """Clean up old files in directory"""
    
    import glob
    from pathlib import Path
    
    if not os.path.exists(directory):
        return
    
    cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
    
    files_deleted = 0
    for file_path in glob.glob(os.path.join(directory, pattern)):
        if os.path.isfile(file_path):
            file_stat = os.stat(file_path)
            if file_stat.st_mtime < cutoff_time:
                try:
                    os.remove(file_path)
                    files_deleted += 1
                except Exception as e:
                    logging.warning(f"Could not delete old file {file_path}: {e}")
    
    if files_deleted > 0:
        logging.info(f"Cleaned up {files_deleted} old files from {directory}")

def get_system_info() -> Dict[str, Any]:
    """Get system information"""
    
    import platform
    import psutil
    
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/data')
        
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': os.cpu_count(),
            'memory_total_gb': round(memory.total / (1024**3), 2),
            'memory_available_gb': round(memory.available / (1024**3), 2),
            'memory_percent': memory.percent,
            'disk_total_gb': round(disk.total / (1024**3), 2),
            'disk_free_gb': round(disk.free / (1024**3), 2),
            'disk_percent': round((disk.used / disk.total) * 100, 1)
        }
        
    except ImportError:
        # psutil not available
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': os.cpu_count()
        }

def health_check() -> Dict[str, Any]:
    """Perform health check and return status"""
    
    health_status = {
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy',
        'checks': {}
    }
    
    # Check data directory
    try:
        os.listdir('/data')
        health_status['checks']['data_directory'] = 'ok'
    except Exception as e:
        health_status['checks']['data_directory'] = f'error: {e}'
        health_status['status'] = 'unhealthy'
    
    # Check database file (if SQLite)
    try:
        if os.path.exists('/data/database/baby_care_tracker.db'):
            health_status['checks']['database_file'] = 'ok'
        else:
            health_status['checks']['database_file'] = 'not_found'
    except Exception as e:
        health_status['checks']['database_file'] = f'error: {e}'
    
    # Check log directory
    try:
        os.listdir('/data/logs')
        health_status['checks']['logs_directory'] = 'ok'
    except Exception as e:
        health_status['checks']['logs_directory'] = f'error: {e}'
    
    # Check available disk space
    try:
        import psutil
        disk = psutil.disk_usage('/data')
        free_percent = (disk.free / disk.total) * 100
        
        if free_percent > 20:
            health_status['checks']['disk_space'] = 'ok'
        elif free_percent > 10:
            health_status['checks']['disk_space'] = 'warning'
        else:
            health_status['checks']['disk_space'] = 'critical'
            health_status['status'] = 'unhealthy'
            
    except ImportError:
        health_status['checks']['disk_space'] = 'unavailable'
    except Exception as e:
        health_status['checks']['disk_space'] = f'error: {e}'
    
    return health_status

def parse_baby_care_action(action_string: str) -> Dict[str, str]:
    """Parse baby care action string into components"""
    
    action_map = {
        'feeding_start_left': {
            'category': 'feeding',
            'action': 'start',
            'detail': 'left_breast',
            'display': 'Start Left Breast Feeding'
        },
        'feeding_start_right': {
            'category': 'feeding', 
            'action': 'start',
            'detail': 'right_breast',
            'display': 'Start Right Breast Feeding'
        },
        'feeding_stop': {
            'category': 'feeding',
            'action': 'stop',
            'detail': None,
            'display': 'Stop Feeding'
        },
        'sleep_start': {
            'category': 'sleep',
            'action': 'start',
            'detail': None,
            'display': 'Start Sleep'
        },
        'wake_up': {
            'category': 'sleep',
            'action': 'stop',
            'detail': None,
            'display': 'Wake Up'
        },
        'diaper_pee': {
            'category': 'diaper',
            'action': 'change',
            'detail': 'pee',
            'display': 'Pee Diaper Change'
        },
        'diaper_poo': {
            'category': 'diaper',
            'action': 'change', 
            'detail': 'poo',
            'display': 'Poo Diaper Change'
        },
        'diaper_both': {
            'category': 'diaper',
            'action': 'change',
            'detail': 'both',
            'display': 'Both (Pee & Poo) Diaper Change'
        }
    }
    
    return action_map.get(action_string, {
        'category': 'unknown',
        'action': 'unknown',
        'detail': None,
        'display': action_string
    })

def generate_unique_id(prefix: str = '') -> str:
    """Generate a unique ID"""
    
    import uuid
    
    unique_id = str(uuid.uuid4()).replace('-', '')[:12]
    
    if prefix:
        return f"{prefix}_{unique_id}"
    
    return unique_id

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """Safely load JSON string with fallback"""
    
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = '{}') -> str:
    """Safely dump object to JSON string with fallback"""
    
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default

class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass

class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass

class DeviceError(Exception):
    """Custom exception for device-related errors"""
    pass

class AnalyticsError(Exception):
    """Custom exception for analytics-related errors"""
    pass
