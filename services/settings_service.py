"""Shared persistence and presentation helpers for restaurant settings."""
import json
import shutil
from pathlib import Path

from database.connection import create_connection


DEFAULT_CURRENCIES = [
    {"name": "US Dollar", "symbol": "$"},
    {"name": "Euro", "symbol": "€"},
    {"name": "British Pound", "symbol": "£"},
    {"name": "Kenyan Shilling", "symbol": "KSh"},
    {"name": "Ugandan Shilling", "symbol": "USh"},
    {"name": "Tanzanian Shilling", "symbol": "TSh"},
    {"name": "South African Rand", "symbol": "R"},
    {"name": "Canadian Dollar", "symbol": "C$"},
    {"name": "Australian Dollar", "symbol": "A$"},
    {"name": "Indian Rupee", "symbol": "₹"},
    {"name": "Japanese Yen", "symbol": "¥"},
    {"name": "Chinese Yuan", "symbol": "¥"},
]
LOGO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}
_settings_cache = None


def get_settings(refresh=False):
    """Return the settings map once per session, with a safe database fallback."""
    global _settings_cache
    if _settings_cache is not None and not refresh:
        return _settings_cache
    conn = create_connection()
    if not conn:
        return _settings_cache or {}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT [key], [value] FROM settings")
        _settings_cache = {row[0]: row[1] for row in cursor.fetchall()}
    except Exception as error:
        print(f"Error fetching settings: {error}")
        _settings_cache = _settings_cache or {}
    finally:
        conn.close()
    return _settings_cache


def update_settings_cache(key, value):
    """Keep the active session in sync immediately after a setting is saved."""
    global _settings_cache
    if _settings_cache is None:
        _settings_cache = get_settings()
    _settings_cache[key] = value


def get_currency_options():
    """Return defaults plus valid custom currencies saved by the administrator."""
    options = list(DEFAULT_CURRENCIES)
    raw_custom = get_settings().get("custom_currencies", "")
    try:
        custom = json.loads(raw_custom) if raw_custom else []
    except (TypeError, json.JSONDecodeError):
        custom = []
    for item in custom:
        if (isinstance(item, dict) and item.get("name") and item.get("symbol")
                and item not in options):
            options.append({"name": str(item["name"]), "symbol": str(item["symbol"])})
    return options


def get_active_currency_symbol():
    """Get the active symbol; old installations without a setting remain USD."""
    return get_settings().get("currency", "").strip() or "$"


def format_currency(amount, decimals=2):
    """Format an amount with the restaurant's persisted active currency."""
    try:
        value = float(amount or 0)
    except (TypeError, ValueError):
        value = 0.0
    symbol = get_active_currency_symbol()
    return (f"-{symbol}{abs(value):,.{decimals}f}" if value < 0
            else f"{symbol}{value:,.{decimals}f}")


def save_custom_currencies(currencies):
    """Serialize the custom currency list for the existing settings table."""
    from services.admin_service import save_setting
    value = json.dumps(currencies, ensure_ascii=False)
    success = save_setting("custom_currencies", value)
    if success:
        update_settings_cache("custom_currencies", value)
    return success


def logo_storage_dir():
    return Path(__file__).resolve().parents[1] / "assets" / "branding"


def store_logo(source_path):
    """Validate and copy a selected logo into application-managed storage."""
    source = Path(source_path)
    if not source.is_file():
        return False, "", "The selected logo file no longer exists."
    if source.suffix.lower() not in LOGO_EXTENSIONS:
        return False, "", "Use a PNG, JPG, JPEG, or BMP image."
    try:
        from PyQt6.QtGui import QImageReader
        reader = QImageReader(str(source))
        if not reader.canRead() or reader.read().isNull():
            return False, "", "The selected file is not a valid readable image."
        destination_dir = logo_storage_dir()
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / f"restaurant_logo{source.suffix.lower()}"
        for existing in destination_dir.glob("restaurant_logo.*"):
            if existing != destination:
                existing.unlink(missing_ok=True)
        shutil.copy2(source, destination)
        return True, str(destination), ""
    except Exception as error:
        return False, "", f"Could not store the logo: {error}"


def remove_managed_logo(path):
    """Remove only logos owned by this application; never delete an external file."""
    try:
        target = Path(path).resolve()
        storage = logo_storage_dir().resolve()
        if storage in target.parents and target.is_file():
            target.unlink()
    except OSError as error:
        print(f"Error removing logo: {error}")
