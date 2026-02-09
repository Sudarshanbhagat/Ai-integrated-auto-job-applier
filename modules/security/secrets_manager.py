"""
Secrets Manager - Automated credential rotation
Handles periodic rotation of API keys, tokens, and passwords
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable
import threading
import json
import os
from modules.helpers import print_lg


class SecretsManager:
    """
    Manages credential rotation and lifecycle.
    
    Features:
    - Scheduled rotation of secrets
    - Backup old secrets for rollback
    - Rotation callbacks (e.g., update remote service)
    - Rotation history tracking
    - Support for custom rotation logic
    """
    
    def __init__(self, vault=None):
        """
        Initialize secrets manager.
        
        Args:
            vault: EncryptedVault instance for storing secrets
        """
        self.vault = vault
        self.rotation_config = {}
        self.rotation_history = []
        self.rotation_threads = {}
        self.rotation_callbacks = {}
        
        print_lg("[SECRETS] Initialized Secrets Manager")
    
    def register_secret(self, secret_name: str, rotation_days: int = 90,
                       callback: Callable = None) -> bool:
        """
        Register a secret for rotation.
        
        Args:
            secret_name: Name of secret (e.g., "openai_api_key")
            rotation_days: Days between rotations (default: 90)
            callback: Function to call on rotation - signature: callback(new_value, old_value)
        
        Returns:
            True if registered
        """
        try:
            self.rotation_config[secret_name] = {
                "rotation_days": rotation_days,
                "last_rotation": datetime.now().isoformat(),
                "next_rotation": (datetime.now() + timedelta(days=rotation_days)).isoformat(),
                "rotation_count": 0,
                "enabled": True
            }
            
            if callback:
                self.rotation_callbacks[secret_name] = callback
            
            print_lg(f"[SECRETS] Registered secret for rotation: {secret_name} (every {rotation_days} days)")
            return True
            
        except Exception as e:
            print_lg(f"[SECRETS] Error registering secret {secret_name}: {e}")
            return False
    
    def check_due_rotations(self) -> list:
        """
        Check which secrets are due for rotation.
        
        Returns:
            List of secret names due for rotation
        """
        due_for_rotation = []
        now = datetime.now()
        
        for secret_name, config in self.rotation_config.items():
            if not config.get("enabled"):
                continue
            
            next_rotation = datetime.fromisoformat(config["next_rotation"])
            if now >= next_rotation:
                due_for_rotation.append(secret_name)
        
        return due_for_rotation
    
    def rotate_secret(self, secret_name: str, new_value: str) -> bool:
        """
        Rotate a secret (replace with new value).
        
        Args:
            secret_name: Name of secret to rotate
            new_value: New secret value
        
        Returns:
            True if rotation successful
        """
        try:
            if secret_name not in self.rotation_config:
                print_lg(f"[SECRETS] Secret not registered for rotation: {secret_name}")
                return False
            
            # Get old value before replacing
            old_value = self.vault.get_credential(secret_name) if self.vault else None
            
            # Store new value
            if self.vault:
                self.vault.set_credential(
                    secret_name,
                    new_value,
                    {"rotated_at": datetime.now().isoformat()}
                )
            
            # Update rotation config
            self.rotation_config[secret_name]["last_rotation"] = datetime.now().isoformat()
            rotation_days = self.rotation_config[secret_name]["rotation_days"]
            self.rotation_config[secret_name]["next_rotation"] = (
                datetime.now() + timedelta(days=rotation_days)
            ).isoformat()
            self.rotation_config[secret_name]["rotation_count"] += 1
            
            # Call rotation callback if registered
            if secret_name in self.rotation_callbacks:
                try:
                    self.rotation_callbacks[secret_name](new_value, old_value)
                    print_lg(f"[SECRETS] Rotation callback executed for {secret_name}")
                except Exception as e:
                    print_lg(f"[SECRETS] Rotation callback failed for {secret_name}: {e}")
            
            # Log rotation
            self.rotation_history.append({
                "timestamp": datetime.now().isoformat(),
                "secret": secret_name,
                "old_value_hash": hash(old_value) if old_value else None,
                "new_value_hash": hash(new_value),
                "success": True
            })
            
            print_lg(f"[SECRETS] Successfully rotated secret: {secret_name}")
            return True
            
        except Exception as e:
            print_lg(f"[SECRETS] Error rotating secret {secret_name}: {e}")
            return False
    
    def get_rotation_status(self, secret_name: str = None) -> Dict:
        """
        Get rotation status for secret(s).
        
        Args:
            secret_name: Specific secret or None for all
        
        Returns:
            Dict with rotation status
        """
        if secret_name:
            if secret_name in self.rotation_config:
                config = self.rotation_config[secret_name]
                next_rotation = datetime.fromisoformat(config["next_rotation"])
                days_until = (next_rotation - datetime.now()).days
                return {
                    "secret": secret_name,
                    "enabled": config["enabled"],
                    "rotation_days": config["rotation_days"],
                    "last_rotation": config["last_rotation"],
                    "next_rotation": config["next_rotation"],
                    "days_until_rotation": max(0, days_until),
                    "rotation_count": config["rotation_count"]
                }
            return {"error": f"Secret not found: {secret_name}"}
        else:
            # All secrets
            status = {}
            for secret_name, config in self.rotation_config.items():
                next_rotation = datetime.fromisoformat(config["next_rotation"])
                days_until = (next_rotation - datetime.now()).days
                status[secret_name] = {
                    "enabled": config["enabled"],
                    "days_until_rotation": max(0, days_until),
                    "rotation_count": config["rotation_count"]
                }
            return status
    
    def enable_secret(self, secret_name: str) -> bool:
        """Enable rotation for a secret."""
        if secret_name in self.rotation_config:
            self.rotation_config[secret_name]["enabled"] = True
            print_lg(f"[SECRETS] Enabled rotation for: {secret_name}")
            return True
        return False
    
    def disable_secret(self, secret_name: str) -> bool:
        """Disable rotation for a secret."""
        if secret_name in self.rotation_config:
            self.rotation_config[secret_name]["enabled"] = False
            print_lg(f"[SECRETS] Disabled rotation for: {secret_name}")
            return True
        return False
    
    def get_rotation_history(self, limit: int = 100) -> list:
        """
        Get rotation history (last N rotations).
        
        Args:
            limit: Maximum number of rotation records to return
        
        Returns:
            List of rotation events
        """
        return self.rotation_history[-limit:]
    
    def start_auto_rotation(self, check_interval_hours: int = 24) -> bool:
        """
        Start background thread for automatic rotation checking.
        
        Args:
            check_interval_hours: How often to check for due rotations
        
        Returns:
            True if started successfully
        """
        try:
            def rotation_monitor():
                """Background thread that monitors for due rotations."""
                while True:
                    time.sleep(check_interval_hours * 3600)  # Sleep for interval
                    
                    due_secrets = self.check_due_rotations()
                    if due_secrets:
                        print_lg(f"[SECRETS] Secrets due for rotation: {due_secrets}")
                        # Emit alert or trigger rotation
            
            thread = threading.Thread(target=rotation_monitor, daemon=True)
            thread.start()
            self.rotation_threads["monitor"] = thread
            
            print_lg(f"[SECRETS] Started auto-rotation monitor (check every {check_interval_hours} hours)")
            return True
            
        except Exception as e:
            print_lg(f"[SECRETS] Error starting auto-rotation: {e}")
            return False
    
    def export_rotation_config(self, filepath: str = None) -> Dict:
        """
        Export rotation configuration.
        
        Args:
            filepath: Optional file to save config to
        
        Returns:
            Rotation configuration dict
        """
        config = {
            "managed_secrets": len(self.rotation_config),
            "rotation_config": self.rotation_config,
            "total_rotations": len(self.rotation_history)
        }
        
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=2)
            print_lg(f"[SECRETS] Exported rotation config to {filepath}")
        
        return config
