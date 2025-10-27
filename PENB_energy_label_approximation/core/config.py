"""
Správa konfigurace a API tokenu
"""
import json
import os
from pathlib import Path
from typing import Optional
from core.data_models import APIConfig


# Cesta k úložišti
STORAGE_DIR = Path(__file__).parent.parent / "storage"
TOKEN_STORE_PATH = STORAGE_DIR / "token_store.json"
USER_INPUTS_PATH = STORAGE_DIR / "user_inputs.json"


def ensure_storage_dir():
    """Zajistí existenci storage adresáře"""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def load_api_config() -> APIConfig:
    """
    Načte API konfiguraci ze souboru.
    Pokud soubor neexistuje, vrátí prázdnou konfiguraci.
    """
    ensure_storage_dir()
    
    if not TOKEN_STORE_PATH.exists():
        return APIConfig()
    
    try:
        with open(TOKEN_STORE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return APIConfig(**data)
    except Exception as e:
        print(f"Varování: Nelze načíst konfiguraci: {e}")
        return APIConfig()


def save_api_config(config: APIConfig):
    """
    Uloží API konfiguraci do souboru.
    """
    ensure_storage_dir()
    
    try:
        with open(TOKEN_STORE_PATH, 'w', encoding='utf-8') as f:
            json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)
        
        # Nastaví oprávnění jen pro uživatele (Windows: není jednoduché, na Linuxu chmod 600)
        # Na Windows to můžeme přeskočit nebo použít pywin32
        if os.name != 'nt':
            os.chmod(TOKEN_STORE_PATH, 0o600)
            
    except Exception as e:
        raise RuntimeError(f"Nelze uložit konfiguraci: {e}")


def get_api_key() -> Optional[str]:
    """Získá API klíč z konfigurace"""
    config = load_api_config()
    return config.weather_api_key


def set_api_key(api_key: str):
    """Uloží API klíč do konfigurace"""
    config = load_api_config()
    config.weather_api_key = api_key
    save_api_config(config)


def get_last_location() -> Optional[str]:
    """Získá poslední použitou lokalitu"""
    config = load_api_config()
    return config.last_location


def set_last_location(location: str):
    """Uloží poslední použitou lokalitu"""
    config = load_api_config()
    config.last_location = location
    save_api_config(config)


def save_user_inputs(inputs_dict: dict):
    """
    Uloží poslední uživatelské vstupy (pro pohodlí při dalším spuštění).
    """
    ensure_storage_dir()
    
    try:
        with open(USER_INPUTS_PATH, 'w', encoding='utf-8') as f:
            json.dump(inputs_dict, f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        print(f"Varování: Nelze uložit vstupy: {e}")


def load_user_inputs() -> Optional[dict]:
    """
    Načte poslední uživatelské vstupy.
    """
    if not USER_INPUTS_PATH.exists():
        return None
    
    try:
        with open(USER_INPUTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Varování: Nelze načíst vstupy: {e}")
        return None
