import json
import os
from datetime import datetime

class CookieManager:
    def __init__(self, file_path='data/cookies.json'):
        self.file_path = file_path
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """Crear directorio data/ si no existe"""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
    
    def save_cookies(self, sessionid, sessionid_sign):
        """Guardar cookies en archivo JSON"""
        data = {
            'tv_sessionid': sessionid,
            'tv_sessionid_sign': sessionid_sign,
            'cookies_updated_at': datetime.now().isoformat()
        }
        
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving cookies: {e}")
            return False
    
    def load_cookies(self):
        """Cargar cookies desde archivo JSON"""
        if not os.path.exists(self.file_path):
            return '', '', None
            
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            return (
                data.get('tv_sessionid', ''),
                data.get('tv_sessionid_sign', ''),
                data.get('cookies_updated_at')
            )
        except Exception as e:
            print(f"Error loading cookies: {e}")
            return '', '', None
    
    def get_cookie(self, key, default=''):
        """Obtener un valor específico de cookie"""
        sessionid, sessionid_sign, updated_at = self.load_cookies()
        
        if key == 'tv_sessionid':
            return sessionid
        elif key == 'tv_sessionid_sign':
            return sessionid_sign
        elif key == 'cookies_updated_at':
            return updated_at
        else:
            return default
    
    def cookies_exist(self):
        """Verificar si existen cookies guardadas"""
        sessionid, sessionid_sign, _ = self.load_cookies()
        return bool(sessionid and sessionid_sign)
    
    def clear_cookies(self):
        """Limpiar archivo de cookies"""
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            return True
        except Exception as e:
            print(f"Error clearing cookies: {e}")
            return False