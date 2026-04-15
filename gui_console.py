#!/usr/bin/env python3
"""CCATK Geek Console GUI (safe mode).

This GUI intentionally provides *non-destructive* features only:
- URL reachability check
- Optional proxy availability check
- Real-time dark themed logs

Use only on assets you are authorized to test.
"""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

import requests
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


@dataclass
class AppConfig:
    target_url: str
    check_interval: float
    timeout: float
    rounds: int
    use_proxy: bool
    proxy_file: Optional[Path]


class GeekConsoleApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("CCATK Geek Console (Safe)")
        self.root.geometry("1080x720")
        self.root.minsize(960, 620)

        self.log_queue: "queue.Queue[str]" = queue.Queue()
        self.worker: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        self._setup_style()
        self._build_layout()

        self.root.after(80, self._drain_logs)

    def _setup_style(self) -> None:
        self.root.configure(bg="#070B10")
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background="#070B10")
        style.configure("Card.TFrame", background="#101820")
        style.configure("TLabel", background="#070B10", foreground="#7CFCB2", font=("Consolas", 10))
        style.configure("Hint.TLabel", foreground="#9AA8B2")
        style.configure("Title.TLabel", foreground="#40F4C6", font=("Consolas", 18, "bold"))
        style.configure("SubTitle.TLabel", foreground="#8FA3B0", font=("Consolas", 10))
        style.configure("TButton", background="#0F2E2A", foreground="#C7FDEB", borderwidth=0, padding=8)
        style.map("TButton", background=[("active", "#15453D")])
        style.configure("Accent.TButton", background="#165F52", foreground="#E7FFF8", padding=10)
        style.map("Accent.TButton", background=[("active", "#1A7262")])

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=16, pady=16)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 12))

        ttk.Label(header, text="CCATK // GEEK CONSOLE", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Single-flow workflow: Configure -> Validate -> Run checks -> Inspect logs",
            style="SubTitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        form_card = ttk.Frame(container, style="Card.TFrame", padding=12)
        form_card.pack(fill="x", pady=(0, 10))

        self.url_var = tk.StringVar(value="https://example.com")
        self.interval_var = tk.StringVar(value="1.0")
        self.timeout_var = tk.StringVar(value="5.0")
        self.rounds_var = tk.StringVar(value="30")
        self.proxy_enabled_var = tk.BooleanVar(value=False)
        self.proxy_file_var = tk.StringVar(value="")

        self._row(form_card, 0, "Target URL", self.url_var, "例: https://example.com")
        self._row(form_card, 1, "Interval(s)", self.interval_var, "轮询间隔，建议 >=0.5")
        self._row(form_card, 2, "Timeout(s)", self.timeout_var, "单次请求超时时间")
        self._row(form_card, 3, "Rounds", self.rounds_var, "检查次数")

        proxy_row = ttk.Frame(form_card, style="Card.TFrame")
        proxy_row.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        proxy_row.columnconfigure(1, weight=1)

        ttk.Checkbutton(
            proxy_row,
            text="Enable proxy check (http://ip:port per line)",
            variable=self.proxy_enabled_var,
            command=self._toggle_proxy_widgets,
        ).grid(row=0, column=0, sticky="w")

        self.proxy_entry = ttk.Entry(proxy_row, textvariable=self.proxy_file_var)
        self.proxy_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        self.proxy_btn = ttk.Button(proxy_row, text="Browse", command=self._pick_proxy_file)
        self.proxy_btn.grid(row=1, column=2, padx=(8, 0), pady=(6, 0))

        action_row = ttk.Frame(form_card, style="Card.TFrame")
        action_row.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(12, 0))

        self.start_btn = ttk.Button(action_row, text="Start", style="Accent.TButton", command=self._start)
        self.start_btn.pack(side="left")

        self.stop_btn = ttk.Button(action_row, text="Stop", command=self._stop, state="disabled")
        self.stop_btn.pack(side="left", padx=(8, 0))

        ttk.Button(action_row, text="Clear Logs", command=self._clear_logs).pack(side="left", padx=(8, 0))

        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(action_row, textvariable=self.status_var, style="Hint.TLabel").pack(side="right")

        log_card = ttk.Frame(container, style="Card.TFrame", padding=10)
        log_card.pack(fill="both", expand=True)

        ttk.Label(log_card, text="Runtime Logs", style="SubTitle.TLabel").pack(anchor="w", pady=(0, 6))

        self.log = tk.Text(
            log_card,
            bg="#020609",
            fg="#73FBD3",
            insertbackground="#73FBD3",
            font=("Consolas", 10),
            relief="flat",
            padx=10,
            pady=10,
            spacing1=2,
            spacing3=2,
        )
        self.log.pack(fill="both", expand=True)
        self.log.insert("end", "[BOOT] GUI ready. Configure and click Start.\n")
        self.log.configure(state="disabled")

        self._toggle_proxy_widgets()

    def _row(self, parent: ttk.Frame, row: int, label: str, var: tk.StringVar, hint: str) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(parent, textvariable=var).grid(row=row, column=1, sticky="ew", padx=(8, 8), pady=4)
        ttk.Label(parent, text=hint, style="Hint.TLabel").grid(row=row, column=2, sticky="w")
        parent.columnconfigure(1, weight=1)

    def _toggle_proxy_widgets(self) -> None:
        enabled = self.proxy_enabled_var.get()
        state = "normal" if enabled else "disabled"
        self.proxy_entry.configure(state=state)
        self.proxy_btn.configure(state=state)

    def _pick_proxy_file(self) -> None:
        path = filedialog.askopenfilename(title="选择代理文件", filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if path:
            self.proxy_file_var.set(path)

    def _append_log(self, message: str) -> None:
        self.log_queue.put(message)

    def _drain_logs(self) -> None:
        dirty = False
        while True:
            try:
                msg = self.log_queue.get_nowait()
            except queue.Empty:
                break
            else:
                if not dirty:
                    self.log.configure(state="normal")
                    dirty = True
                self.log.insert("end", msg + "\n")
                self.log.see("end")
        if dirty:
            self.log.configure(state="disabled")
        self.root.after(80, self._drain_logs)

    def _parse_config(self) -> AppConfig:
        url = self.url_var.get().strip()
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL 必须以 http:// 或 https:// 开头")

        interval = float(self.interval_var.get().strip())
        timeout = float(self.timeout_var.get().strip())
        rounds = int(self.rounds_var.get().strip())
        if interval <= 0 or timeout <= 0 or rounds <= 0:
            raise ValueError("Interval / Timeout / Rounds 必须是正数")

        use_proxy = self.proxy_enabled_var.get()
        proxy_file = None
        if use_proxy:
            value = self.proxy_file_var.get().strip()
            if not value:
                raise ValueError("已开启代理检测，但未选择代理文件")
            proxy_file = Path(value)
            if not proxy_file.exists():
                raise ValueError(f"代理文件不存在: {proxy_file}")

        return AppConfig(
            target_url=url,
            check_interval=interval,
            timeout=timeout,
            rounds=rounds,
            use_proxy=use_proxy,
            proxy_file=proxy_file,
        )

    def _start(self) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("Info", "任务正在运行中")
            return

        try:
            cfg = self._parse_config()
        except Exception as exc:
            messagebox.showerror("配置错误", str(exc))
            return

        self.stop_event.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_var.set("Running")

        self.worker = threading.Thread(target=self._run_flow, args=(cfg,), daemon=True)
        self.worker.start()

    def _stop(self) -> None:
        self.stop_event.set()
        self._append_log("[CTRL] Stop requested by user.")

    def _clear_logs(self) -> None:
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _run_flow(self, cfg: AppConfig) -> None:
        try:
            self._append_log("[FLOW] Step 1/3: configuration accepted")
            proxies = self._load_proxies(cfg.proxy_file) if cfg.use_proxy and cfg.proxy_file else []
            if cfg.use_proxy:
                self._append_log(f"[FLOW] Step 2/3: loaded {len(proxies)} proxies")
            else:
                self._append_log("[FLOW] Step 2/3: proxy check disabled")

            self._append_log("[FLOW] Step 3/3: start URL checks")
            self._run_url_checks(cfg, proxies)
        except Exception as exc:
            self._append_log(f"[ERR] {exc}")
        finally:
            self.root.after(0, self._on_finish)

    def _on_finish(self) -> None:
        self.status_var.set("Idle")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self._append_log("[DONE] Flow ended.")

    def _load_proxies(self, proxy_file: Path) -> List[str]:
        lines = [line.strip() for line in proxy_file.read_text(encoding="utf-8").splitlines()]
        proxies = [line for line in lines if line and not line.startswith("#")]
        if not proxies:
            raise ValueError("代理文件为空")
        return proxies

    def _proxy_ok(self, proxy: str, timeout: float) -> bool:
        test_url = "https://httpbin.org/ip"
        proxy_map = {"http": proxy, "https": proxy}
        try:
            requests.get(test_url, timeout=timeout, proxies=proxy_map)
            return True
        except requests.RequestException:
            return False

    def _iter_round_proxies(self, proxies: List[str], index: int) -> Iterable[str]:
        if not proxies:
            return []
        return [proxies[index % len(proxies)]]

    def _run_url_checks(self, cfg: AppConfig, proxies: List[str]) -> None:
        ok = 0
        fail = 0
        for i in range(1, cfg.rounds + 1):
            if self.stop_event.is_set():
                self._append_log("[FLOW] interrupted before completion")
                return

            use_proxy = None
            if proxies:
                candidate = next(iter(self._iter_round_proxies(proxies, i - 1)))
                if self._proxy_ok(candidate, cfg.timeout):
                    use_proxy = candidate
                    self._append_log(f"[PROXY] #{i} using healthy proxy {candidate}")
                else:
                    self._append_log(f"[PROXY] #{i} skip unhealthy proxy {candidate}")

            try:
                kwargs = {"timeout": cfg.timeout}
                if use_proxy:
                    kwargs["proxies"] = {"http": use_proxy, "https": use_proxy}

                resp = requests.get(cfg.target_url, **kwargs)
                self._append_log(f"[CHECK] round={i} status={resp.status_code} len={len(resp.content)}")
                ok += 1
            except requests.RequestException as exc:
                fail += 1
                self._append_log(f"[CHECK] round={i} failed: {exc}")

            time.sleep(cfg.check_interval)

        self._append_log(f"[STAT] total={cfg.rounds} ok={ok} fail={fail}")


def main() -> None:
    root = tk.Tk()
    app = GeekConsoleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
