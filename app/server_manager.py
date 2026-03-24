import subprocess
import os
import time
from pathlib import Path
from .rcon import MCRcon

class ServerManager:
    def __init__(self, base_dir, rcon_host, rcon_port, rcon_password):
        self.base_dir = Path(base_dir).resolve()
        self.server_dir = self.base_dir / "server"
        self.rcon_host = rcon_host
        self.rcon_port = rcon_port
        self.rcon_password = rcon_password
        self.process = None
        self.rcon = None

    def start_server(self):
        if self.is_running():
            return "Server is already running."
            
        server_jar = self.server_dir / "server.jar"
        if not server_jar.exists():
            return "Error: server.jar not found in server/ directory."

        # Check EULA
        eula_file = self.server_dir / "eula.txt"
        if not eula_file.exists():
             # Create it with false
             with open(eula_file, "w") as f:
                 f.write("eula=false\n")
             return "Please agree to EULA in server/eula.txt"
        
        with open(eula_file, "r") as f:
            content = f.read()
            if "eula=true" not in content and "eula=TRUE" not in content:
                 return "Please agree to EULA in server/eula.txt"

        # Start process
        # Security: shell=False, cwd=server_dir
        cmd = ["java", "-Xmx1024M", "-Xms1024M", "-jar", "server.jar", "nogui"]
        try:
             self.process = subprocess.Popen(
                cmd,
                cwd=str(self.server_dir),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
             )
             return "Server started. Please wait for initialization."
        except Exception as e:
            return f"Failed to start server: {e}"

    def is_running(self):
        return self.process is not None and self.process.poll() is None

    def connect_rcon(self):
        retries = 3
        for i in range(retries):
            try:
                self.rcon = MCRcon(self.rcon_host, self.rcon_port, self.rcon_password)
                self.rcon.connect()
                return True
            except Exception:
                time.sleep(1)
        return False

    def send_command(self, cmd):
        if not self.rcon:
             if not self.connect_rcon():
                 return "Error: Could not connect to RCON."
        try:
            return self.rcon.command(cmd)
        except Exception as e:
             self.rcon = None # Force reconnect next time
             return f"RCON Error: {str(e)}"

    def stop_server(self):
        if self.is_running():
            if self.rcon:
                try:
                    self.rcon.command("stop")
                    self.rcon.disconnect()
                except:
                    pass
            
            # Wait for strict shutdown
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            return "Server stopped."
        return "Server not running."
