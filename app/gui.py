import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import datetime
import json
import time
from pathlib import Path

class MVBApp:
    def __init__(self, root, base_dir, server_manager, security_manager, datapack_generator, bridge_manager, session_manager):
        self.root = root
        self.root.title("Minecraft VibeCoding Bridge (MVB)")
        self.root.geometry("1000x700")
        
        self.base_dir = base_dir
        self.server_manager = server_manager
        self.security_manager = security_manager
        self.datapack_generator = datapack_generator
        self.bridge_manager = bridge_manager
        self.session_manager = session_manager
        
        self.create_widgets()
        self.refresh_history()
        
    def create_widgets(self):
        # Style
        style = ttk.Style()
        style.configure("Safe.TLabel", foreground="green", font=("Helvetica", 12, "bold"))
        style.configure("Warning.TLabel", foreground="red", font=("Helvetica", 10))
        
        # Header - Safety Message
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)
        
        safety_label = ttk.Label(header_frame, text="✅ MVB Safe Mode Active (Isolated / No Delete / Localhost Only)", style="Safe.TLabel")
        safety_label.pack(side=tk.LEFT)
        
        # Main Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tab 1: Main Control
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main Control")
        self.create_main_tab()
        
        # Tab 2: History
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="History")
        self.create_history_tab()
        
    def create_main_tab(self):
        # Server Control Section
        control_frame = ttk.LabelFrame(self.main_tab, text="Server Control", padding="10")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.btn_start_server = ttk.Button(control_frame, text="Start Server", command=self.start_server_thread)
        self.btn_start_server.pack(side=tk.LEFT, padx=5)
        
        self.btn_rcon_test = ttk.Button(control_frame, text="Test RCON", command=self.test_rcon)
        self.btn_rcon_test.pack(side=tk.LEFT, padx=5)
        
        self.server_status_var = tk.StringVar(value="Status: Stopped")
        self.lbl_server_status = ttk.Label(control_frame, textvariable=self.server_status_var)
        self.lbl_server_status.pack(side=tk.LEFT, padx=15)
        
        # Request Section
        request_frame = ttk.LabelFrame(self.main_tab, text="User Request (Input what you want to do)", padding="10")
        request_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.txt_request = scrolledtext.ScrolledText(request_frame, height=5)
        self.txt_request.pack(fill=tk.BOTH, expand=True)
        
        action_frame = ttk.Frame(request_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        self.btn_generate = ttk.Button(action_frame, text="Generate & Run Plan (JSON)", command=self.run_process_thread)
        self.btn_generate.pack(side=tk.RIGHT)
        
        # Log Section
        log_frame = ttk.LabelFrame(self.main_tab, text="Safety Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.txt_log = scrolledtext.ScrolledText(log_frame, height=10, state='disabled')
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def create_history_tab(self):
        paned = ttk.PanedWindow(self.history_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left: Session List
        left_frame = ttk.Frame(paned, width=200)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Sessions").pack(anchor=tk.W)
        self.lst_history = tk.Listbox(left_frame)
        self.lst_history.pack(fill=tk.BOTH, expand=True)
        self.lst_history.bind("<<ListboxSelect>>", self.on_history_select)
        
        # Right: Details
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        
        ttk.Label(right_frame, text="Explanation").pack(anchor=tk.W)
        self.txt_history_detail = scrolledtext.ScrolledText(right_frame, state='disabled')
        self.txt_history_detail.pack(fill=tk.BOTH, expand=True)
        
        btn_refresh = ttk.Button(left_frame, text="Refresh", command=self.refresh_history)
        btn_refresh.pack(fill=tk.X)

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.txt_log.configure(state='normal')
        self.txt_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.txt_log.see(tk.END)
        self.txt_log.configure(state='disabled')

    def start_server_thread(self):
        self.log("Starting server... (This may take a while)")
        self.btn_start_server.config(state="disabled")
        
        def run():
            msg = self.server_manager.start_server()
            self.root.after(0, lambda: self.log(msg))
            self.root.after(0, lambda: self.update_server_status())
            
        threading.Thread(target=run, daemon=True).start()

    def update_server_status(self):
        if self.server_manager.is_running():
            self.server_status_var.set("Status: Running")
            self.btn_start_server.config(text="Stop Server", command=self.stop_server, state="normal")
        else:
            self.server_status_var.set("Status: Stopped")
            self.btn_start_server.config(text="Start Server", command=self.start_server_thread, state="normal")

    def stop_server(self):
        msg = self.server_manager.stop_server()
        self.log(msg)
        self.update_server_status()

    def test_rcon(self):
        resp = self.server_manager.send_command("list")
        self.log(f"RCON Test: {resp}")

    def run_process_thread(self):
        request_text = self.txt_request.get("1.0", tk.END).strip()
        if not request_text:
            messagebox.showwarning("Empty Request", "Please enter a request.")
            return

        self.btn_generate.config(state="disabled")
        threading.Thread(target=self.run_process, args=(request_text,), daemon=True).start()

    def run_process(self, request_text):
        try:
            # 1. Create Prompt
            self.log("Creating prompt for AI...")
            prompt = self.bridge_manager.create_prompt(request_text)
            self.log(f"Prompt saved to {self.bridge_manager.bridge_in / 'prompt.json'}")
            
            # 2. Wait for Plan
            self.log("Waiting for plan.json... (Please generate it with Antigravity)")
            
            plan = None
            for _ in range(60): # Wait up to 60 seconds (or logic to wait indefinitely?)
                # Spec says "detect plan.json". Let's wait a bit.
                # In a real tool we might want a cancel button.
                plan = self.bridge_manager.check_for_plan()
                if plan:
                    break
                time.sleep(1)
            
            if not plan:
                self.log("Timeout: plan.json not found in mvb_work/bridge_out/")
                self.root.after(0, lambda: self.btn_generate.config(state="normal"))
                return

            self.log("Plan received! Validating...")
            
            # 3. Validate
            self.security_manager.validate_plan_json(plan)
            self.log("Validation Passed.")
            
            # 4. Session Start
            session_id, session_dir = self.session_manager.create_session()
            self.log(f"Session created: {session_id}")
            
            self.session_manager.save_request(session_dir, request_text)
            self.session_manager.save_prompt(session_dir, prompt)
            self.session_manager.save_plan(session_dir, plan)
            
            # 5. Generate Datapack
            self.log("Generating Datapack...")
            generated_files = self.datapack_generator.generate(plan)
            self.session_manager.save_generated_files(session_dir, generated_files)
            for f in generated_files:
                self.log(f"Generated: {f}")
                
            # 6. Run Steps
            self.log("Executing Run Steps...")
            for step in plan["run"]["steps"]:
                step_type = step["type"]
                if step_type == "reload":
                    resp = self.server_manager.send_command("reload")
                    self.log(f"CMD reload: {resp}")
                elif step_type == "function":
                    val = step["value"]
                    resp = self.server_manager.send_command(f"function {val}")
                    self.log(f"CMD function {val}: {resp}")
                    
            # 7. Finalize Session
            self.session_manager.create_explain_md(session_dir, plan)
            self.log("Execution Completed Successfully.")
            
            self.root.after(0, self.refresh_history)
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.root.after(0, lambda: self.btn_generate.config(state="normal"))

    def refresh_history(self):
        self.lst_history.delete(0, tk.END)
        sessions = self.session_manager.list_sessions()
        for s in sessions:
            self.lst_history.insert(tk.END, s)

    def on_history_select(self, event):
        selection = self.lst_history.curselection()
        if not selection:
            return
        session_id = self.lst_history.get(selection[0])
        session_dir = self.session_manager.sessions_dir / session_id
        
        display_text = ""
        
        # Read explain.md
        explain_md = session_dir / "explain.md"
        if explain_md.exists():
            with open(explain_md, "r", encoding="utf-8") as f:
                display_text += f"--- {session_id} ---\n\n"
                display_text += f.read()
        
        self.txt_history_detail.configure(state='normal')
        self.txt_history_detail.delete("1.0", tk.END)
        self.txt_history_detail.insert(tk.END, display_text)
        self.txt_history_detail.configure(state='disabled')
