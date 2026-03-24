import tkinter as tk
from pathlib import Path
import json
import sys

from app.security import SecurityManager
from app.datapack import DatapackGenerator
from app.rcon import MCRcon
from app.server_manager import ServerManager
from app.bridge import BridgeManager
from app.session import SessionManager
from app.gui import MVBApp

def main():
    base_dir = Path(".").resolve()
    
    # Load Settings
    settings_path = base_dir / "config" / "settings.json"
    if not settings_path.exists():
        print("Error: config/settings.json not found.")
        return

    with open(settings_path, "r") as f:
        settings = json.load(f)
        
    # Initialize Core Components
    security_manager = SecurityManager(base_dir)
    datapack_generator = DatapackGenerator(base_dir, security_manager)
    
    server_manager = ServerManager(
        base_dir, 
        settings.get("rcon_host", "localhost"),
        settings.get("rcon_port", 25575),
        settings.get("rcon_password", "password")
    )
    
    bridge_manager = BridgeManager(base_dir)
    session_manager = SessionManager(base_dir)
    
    # Initialize GUI
    root = tk.Tk()
    app = MVBApp(
        root, 
        base_dir, 
        server_manager, 
        security_manager, 
        datapack_generator, 
        bridge_manager, 
        session_manager
    )
    
    root.mainloop()

if __name__ == "__main__":
    main()
