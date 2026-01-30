"""
Face Data Encryption Service
Ensures DPDP Act 2023 compliance by encrypting biometric data at rest
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os
import base64
import json


class FaceDataEncryption:
    """
    Handles encryption/decryption of face embeddings before storage
    Uses Fernet (symmetric encryption) with AES-128
    """
    
    def __init__(self):
        # Get encryption key from environment variable
        # In production, use AWS Secrets Manager or HashiCorp Vault
        encryption_key = os.getenv("FACE_ENCRYPTION_KEY")
        
        if not encryption_key:
            # Generate a key if not exists (ONLY for development)
            print("⚠️ WARNING: No FACE_ENCRYPTION_KEY found. Generating temporary key.")
            print("⚠️ This is NOT secure for production!")
            encryption_key = Fernet.generate_key().decode()
            print(f"Generated key: {encryption_key}")
            print("Add this to your .env file: FACE_ENCRYPTION_KEY={encryption_key}")
        
        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
    
    def encrypt_embedding(self, embedding: list) -> str:
        """
        Encrypt face embedding before storing in database
        
        Args:
            embedding: List of float values (face vector)
        
        Returns:
            Encrypted string (base64 encoded)
        """
        try:
            # Convert embedding list to JSON string
            embedding_json = json.dumps(embedding)
            
            # Encrypt
            encrypted_bytes = self.cipher.encrypt(embedding_json.encode())
            
            # Return as base64 string for database storage
            return encrypted_bytes.decode()
        
        except Exception as e:
            print(f"❌ Encryption failed: {e}")
            raise
    
    def decrypt_embedding(self, encrypted_data: str) -> list:
        """
        Decrypt face embedding for matching
        
        Args:
            encrypted_data: Encrypted string from database
        
        Returns:
            Original embedding list
        """
        try:
            # Decrypt
            decrypted_bytes = self.cipher.decrypt(encrypted_data.encode())
            
            # Parse JSON back to list
            embedding = json.loads(decrypted_bytes.decode())
            
            return embedding
        
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            raise
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key
        Use this ONCE during initial setup
        
        Returns:
            Base64 encoded encryption key
        """
        return Fernet.generate_key().decode()


# Singleton instance
encryption_service = FaceDataEncryption()


# Example usage:
if __name__ == "__main__":
    # Test encryption/decryption
    test_embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # Simulated 500-d vector
    
    print("Original embedding (first 10):", test_embedding[:10])
    
    # Encrypt
    encrypted = encryption_service.encrypt_embedding(test_embedding)
    print(f"\nEncrypted (length: {len(encrypted)}):", encrypted[:50] + "...")
    
    # Decrypt
    decrypted = encryption_service.decrypt_embedding(encrypted)
    print("\nDecrypted embedding (first 10):", decrypted[:10])
    
    # Verify
    assert test_embedding == decrypted, "Encryption/Decryption failed!"
    print("\n✅ Encryption test passed!")
