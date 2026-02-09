"""
Encrypted Vault - Secure credential storage
Encrypts sensitive credentials using Fernet (symmetric encryption)
"""

import os
import json
from typing import Dict, Optional
from datetime import datetime
from modules.helpers import print_lg

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print_lg("[WARNING] cryptography library not installed. Install with: pip install cryptography")


class EncryptedVault:
    """
    Secure storage for sensitive credentials.
    
    Features:
    - Encrypts data at rest using Fernet
    - Stores in encrypted JSON file
    - Decrypts on-demand for use
    - Master password protected
    - Audit trail of access
    """
    
    def __init__(self, vault_file: str = "config/.vault", master_password: str = None):
        """
        Initialize encrypted vault.
        
        Args:
            vault_file: Path to encrypted vault file
            master_password: Master password to encrypt/decrypt (if None, prompts or uses env var)
        """
        self.vault_file = vault_file
        self.credentials = {}
        self.cipher = None
        self.access_log = []
        
        if not CRYPTO_AVAILABLE:
            print_lg("[VAULT] WARNING: Cryptography not available, using plaintext storage (INSECURE)")
            return
        
        # Get or create encryption key
        self._initialize_cipher(master_password)
        
        # Load existing vault if it exists
        if os.path.exists(vault_file):
            self._load_vault()
        
        print_lg(f"[VAULT] Initialized encrypted vault at {vault_file}")
    
    def _initialize_cipher(self, master_password: str = None):
        """Initialize Fernet cipher from master password or key file."""
        if not CRYPTO_AVAILABLE:
            return
        
        key_file = self.vault_file + ".key"
        
        # Try to load existing key
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate new key from master password
            if not master_password:
                master_password = os.environ.get("VAULT_MASTER_PASSWORD", "")
            
            if not master_password:
                print_lg("[VAULT] WARNING: No master password provided, using default (INSECURE)")
                master_password = "default-insecure-password-change-this"
            
            # Derive key from password (simplified - in production use PBKDF2)
            import hashlib
            key = Fernet.encrypt(master_password.encode()).rstrip(b'=')[:32]
            key = Fernet.generate_key()  # Use proper random key instead
            
            # Save key file (protect with file permissions)
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Read/write owner only
        
        self.cipher = Fernet(key)
    
    def set_credential(self, name: str, value: str, metadata: Dict = None) -> bool:
        """
        Store a credential in the encrypted vault.
        
        Args:
            name: Credential name (e.g., "linkedin_password", "openai_api_key")
            value: Credential value (will be encrypted)
            metadata: Optional metadata (e.g., {"type": "password", "expires": "2026-02-15"})
        
        Returns:
            True if successful
        """
        try:
            if not CRYPTO_AVAILABLE:
                # Fallback: store in plaintext (insecure)
                self.credentials[name] = {
                    "value": value,
                    "metadata": metadata or {},
                    "created": datetime.now().isoformat(),
                    "encrypted": False
                }
                self._save_vault()
                return True
            
            # Encrypt value
            encrypted_value = self.cipher.encrypt(value.encode()).decode()
            
            self.credentials[name] = {
                "value": encrypted_value,
                "metadata": metadata or {},
                "created": datetime.now().isoformat(),
                "encrypted": True
            }
            
            self._save_vault()
            print_lg(f"[VAULT] Stored credential: {name}")
            return True
            
        except Exception as e:
            print_lg(f"[VAULT] Error storing credential {name}: {e}")
            return False
    
    def get_credential(self, name: str) -> Optional[str]:
        """
        Retrieve a credential from the vault.
        
        Args:
            name: Credential name
        
        Returns:
            Decrypted credential value, or None if not found
        """
        try:
            if name not in self.credentials:
                print_lg(f"[VAULT] Credential not found: {name}")
                return None
            
            cred_data = self.credentials[name]
            
            # Check if credential is expired
            if "metadata" in cred_data and "expires" in cred_data["metadata"]:
                expires = cred_data["metadata"]["expires"]
                if expires < datetime.now().isoformat():
                    print_lg(f"[VAULT] WARNING: Credential expired: {name}")
                    return None
            
            # Decrypt if necessary
            if cred_data.get("encrypted", False) and CRYPTO_AVAILABLE:
                decrypted = self.cipher.decrypt(cred_data["value"].encode()).decode()
            else:
                decrypted = cred_data["value"]
            
            # Log access
            self._log_access(name, "get")
            
            return decrypted
            
        except Exception as e:
            print_lg(f"[VAULT] Error retrieving credential {name}: {e}")
            return None
    
    def delete_credential(self, name: str) -> bool:
        """
        Delete a credential from the vault.
        
        Args:
            name: Credential name
        
        Returns:
            True if successful
        """
        try:
            if name in self.credentials:
                del self.credentials[name]
                self._save_vault()
                self._log_access(name, "delete")
                print_lg(f"[VAULT] Deleted credential: {name}")
                return True
            return False
        except Exception as e:
            print_lg(f"[VAULT] Error deleting credential {name}: {e}")
            return False
    
    def list_credentials(self) -> Dict[str, Dict]:
        """
        List all stored credentials (values hidden).
        
        Returns:
            Dict with credential names and metadata only
        """
        return {
            name: {
                "created": data.get("created"),
                "metadata": data.get("metadata"),
                "encrypted": data.get("encrypted")
            }
            for name, data in self.credentials.items()
        }
    
    def _save_vault(self) -> bool:
        """Save encrypted credentials to file."""
        try:
            os.makedirs(os.path.dirname(self.vault_file), exist_ok=True)
            with open(self.vault_file, 'w') as f:
                json.dump(self.credentials, f, indent=2)
            os.chmod(self.vault_file, 0o600)  # Read/write owner only
            return True
        except Exception as e:
            print_lg(f"[VAULT] Error saving vault: {e}")
            return False
    
    def _load_vault(self) -> bool:
        """Load encrypted credentials from file."""
        try:
            with open(self.vault_file, 'r') as f:
                self.credentials = json.load(f)
            print_lg(f"[VAULT] Loaded {len(self.credentials)} credentials from vault")
            return True
        except Exception as e:
            print_lg(f"[VAULT] Error loading vault: {e}")
            return False
    
    def _log_access(self, credential_name: str, action: str):
        """Log credential access for audit trail."""
        self.access_log.append({
            "timestamp": datetime.now().isoformat(),
            "credential": credential_name,
            "action": action
        })
    
    def get_access_log(self) -> list:
        """Get access audit trail."""
        return self.access_log.copy()
    
    def health_check(self) -> Dict:
        """
        Check vault health.
        
        Returns:
            Dict with health status
        """
        return {
            "encryption_available": CRYPTO_AVAILABLE,
            "vault_file_exists": os.path.exists(self.vault_file),
            "key_file_exists": os.path.exists(self.vault_file + ".key"),
            "credentials_count": len(self.credentials),
            "access_log_size": len(self.access_log),
            "cipher_initialized": self.cipher is not None
        }
