# src/sources/telegram_source.py
"""
Telegram dark intel recon integration.
Searches public Telegram channels for mentions of the target query.
Requires an active Telegram API ID and Hash.
"""

import os
from src.config import CFG
from src.logger import get_logger
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, ApiIdInvalidError

log = get_logger("telegram")

def search_telegram(query: str, limit: int = 5) -> list:
    """
    Search Telegram for the given query.
    Note: Requires an active session. If no session exists, it logs a warning.
    """
    api_id = CFG.get("api_keys", {}).get("telegram_api_id", "")
    api_hash = CFG.get("api_keys", {}).get("telegram_api_hash", "")
    session_name = CFG.get("api_keys", {}).get("telegram_session", "bharosint_session")

    if not api_id or not api_hash:
        log.warning("Telegram API ID or Hash missing in config.yaml. Skipping Telegram recon.")
        return []

    results = []
    
    # We use a context manager for the client, but since we are running 
    # automated non-interactive, we require the session to already be authenticated.
    try:
        # Avoid creating the session file if we know we can't authenticate automatically
        if not os.path.exists(f"{session_name}.session"):
            log.warning("Telegram session file not found. You must run a manual script to authenticate first.")
            return []

        with TelegramClient(session_name, api_id, api_hash) as client:
            log.info("Querying Telegram for: %s", query[:50])
            
            # Search global messages
            # Note: Global search might return channels instead of messages sometimes. 
            # We'll search across public channels the user is part of or global.
            messages = client.iter_messages(None, search=query, limit=limit)
            
            for msg in messages:
                text = msg.text or ""
                if not text:
                    continue
                    
                sender = msg.sender_id or "Unknown"
                date = msg.date.strftime("%Y-%m-%d %H:%M:%S") if msg.date else "Unknown Date"
                
                results.append({
                    "source": "Telegram",
                    "platform": "telegram",
                    "title": f"Msg from {sender} on {date}",
                    "snippet": text,
                    "link": f"tg://resolve?domain={msg.chat.username}&post={msg.id}" if msg.chat and getattr(msg.chat, 'username', None) else "-",
                    "date": date
                })
                
        log.debug("Telegram returned %d results", len(results))
        return results

    except ApiIdInvalidError:
        log.error("Telegram API ID/Hash is invalid.")
        return []
    except Exception as e:
        log.error("Unexpected error during Telegram search: %s", e)
        return []
