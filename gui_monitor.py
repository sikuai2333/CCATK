#!/usr/bin/env python3
"""CCATK 安全版 GUI：用于连通性巡检与代理可用性检测。

说明：
- 本工具仅用于合法的网络可达性检查与代理质量检测。
- 不提供攻击/洪泛能力。
"""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import requests
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


@dataclass
class CheckResult:
    target: str
    ok: bool
    status_code: Optional[int]
    latency_ms: float
    error: str = ""


class GeekMonitorGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("CCATK Geek Monitor Console")
        self.root.geometry("1180x760")
        self.root.configure(bg="#0a0a0a")

        self.log_queue: queue.Queue[str] = queue.Queue()
        self.stop_event = threading.Event()
        self.worker: Optional[threading.Thread] = None

        self.proxy_list: List[str] = []

        self._build_style()
        self._build_layout()
        self._schedule_log_flush()

    def _build_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("TFrame", background="#0a0a0a")
        style.configure("Card.TFrame", background="#111111", borderwidth=0)
        style.configure("Title.TLabel", background="#0a0a0a", foreground="#44ff99", font=("Consolas", 16, "bold"))
        style.configure("Hint.TLabel", background="#0a0a0a", foreground="#a3a3a3", font=("Consolas", 10))
        style.configure("Field.TLabel", background="#111111", foreground="#44ff99", font=("Consolas", 10, "bold"))
        style.configure("Stats.TLabel", background="#111111", foreground="#f5f5f5", font=("Consolas", 10))

        style.configure(
            "Geek.TButton",
            background="#141414",
            foreground="#44ff99",
            bordercolor="#44ff99",
            focusthickness=2,
            focuscolor="#44ff99",
            relief="flat",
            font=("Consolas", 10, "bold"),
            padding=7,
        )
        style.map("Geek.TButton", background=[("active", "#1d1d1d")], foreground=[("disabled", "#666666")])

        style.configure("TEntry", fieldbackground="#0d0d0d", foreground="#f5f5f5", insertcolor="#44ff99")

    def _build_layout(self) -> None:
        shell = ttk.Frame(self.root)
        shell.pack(fill="both", expand=True, padx=18, pady=16)

        header = ttk.Frame(shell)
        header.pack(fill="x")
        ttk.Label(header, text="[ GEEK MONITOR CONSOLE ]", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="流程：1) 配置检测参数  2) 启动巡检  3) 观察日志与统计  4) 导出结果",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(4, 10))

        body = ttk.Frame(shell)
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body, style="Card.TFrame")
        left.pack(side="left", fill="y", padx=(0, 10), ipadx=8, ipady=8)

        right = ttk.Frame(body, style="Card.TFrame")
        right.pack(side="right", fill="both", expand=True, ipadx=8, ipady=8)

        self._build_controls(left)
        self._build_console(right)

    def _build_controls(self, parent: ttk.Frame) -> None:
        frm = ttk.Frame(parent, style="Card.TFrame")
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        ttk.Label(frm, text="目标 URL", style="Field.TLabel").pack(anchor="w")
        self.url_var = tk.StringVar(value="https://example.com")
        ttk.Entry(frm, textvariable=self.url_var, width=38).pack(fill="x", pady=(4, 10))

        ttk.Label(frm, text="HTTP 方法", style="Field.TLabel").pack(anchor="w")
        self.method_var = tk.StringVar(value="GET")
        method_box = ttk.Combobox(frm, textvariable=self.method_var, values=["GET", "HEAD"], state="readonly", width=10)
        method_box.pack(fill="x", pady=(4, 10))

        ttk.Label(frm, text="巡检间隔(秒)", style="Field.TLabel").pack(anchor="w")
        self.interval_var = tk.StringVar(value="2")
        ttk.Entry(frm, textvariable=self.interval_var).pack(fill="x", pady=(4, 10))

        ttk.Label(frm, text="请求超时(秒)", style="Field.TLabel").pack(anchor="w")
        self.timeout_var = tk.StringVar(value="8")
        ttk.Entry(frm, textvariable=self.timeout_var).pack(fill="x", pady=(4, 10))

        ttk.Label(frm, text="代理文件 (ip:port 每行一个)", style="Field.TLabel").pack(anchor="w")
        proxy_row = ttk.Frame(frm, style="Card.TFrame")
        proxy_row.pack(fill="x", pady=(4, 10))
        self.proxy_file_var = tk.StringVar(value="")
        ttk.Entry(proxy_row, textvariable=self.proxy_file_var).pack(side="left", fill="x", expand=True)
        ttk.Button(proxy_row, text="浏览", style="Geek.TButton", command=self._select_proxy_file).pack(side="left", padx=(6, 0))

        btn_row = ttk.Frame(frm, style="Card.TFrame")
        btn_row.pack(fill="x", pady=(8, 8))
        ttk.Button(btn_row, text="启动巡检", style="Geek.TButton", command=self.start_monitor).pack(fill="x", pady=3)
        ttk.Button(btn_row, text="停止", style="Geek.TButton", command=self.stop_monitor).pack(fill="x", pady=3)
        ttk.Button(btn_row, text="检测代理", style="Geek.TButton", command=self.check_proxies).pack(fill="x", pady=3)
        ttk.Button(btn_row, text="清空日志", style="Geek.TButton", command=self.clear_log).pack(fill="x", pady=3)
        ttk.Button(btn_row, text="导出日志", style="Geek.TButton", command=self.export_log).pack(fill="x", pady=3)

        self.stats_var = tk.StringVar(value="请求: 0 | 成功: 0 | 失败: 0 | 平均延迟: 0.0 ms")
        ttk.Label(frm, textvariable=self.stats_var, style="Stats.TLabel", wraplength=300).pack(anchor="w", pady=(10, 4))

    def _build_console(self, parent: ttk.Frame) -> None:
        frm = ttk.Frame(parent, style="Card.TFrame")
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        ttk.Label(frm, text="LOG WINDOW", style="Field.TLabel").pack(anchor="w", pady=(0, 6))

        self.log_text = tk.Text(
            frm,
            bg="#050505",
            fg="#33ff88",
            insertbackground="#33ff88",
            selectbackground="#14532d",
            relief="flat",
            font=("Consolas", 10),
            wrap="word",
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.insert("end", "[system] Geek console ready.\n")
        self.log_text.configure(state="disabled")

    def _schedule_log_flush(self) -> None:
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self.log_text.configure(state="normal")
            self.log_text.insert("end", msg + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        self.root.after(120, self._schedule_log_flush)

    def _log(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{ts}] {msg}")

    def _select_proxy_file(self) -> None:
        path = filedialog.askopenfilename(title="选择代理文件", filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if path:
            self.proxy_file_var.set(path)
            self._log(f"已选择代理文件: {path}")

    def _validate_inputs(self) -> tuple[str, float, float]:
        target = self.url_var.get().strip()
        parsed = urlparse(target)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("URL 无效，请输入 http:// 或 https:// 开头的地址")

        interval = float(self.interval_var.get().strip())
        timeout = float(self.timeout_var.get().strip())
        if interval <= 0 or timeout <= 0:
            raise ValueError("间隔与超时必须大于 0")

        return target, interval, timeout

    def start_monitor(self) -> None:
        if self.worker and self.worker.is_alive():
            self._log("巡检已在运行。")
            return
        try:
            target, interval, timeout = self._validate_inputs()
        except Exception as exc:
            messagebox.showerror("参数错误", str(exc))
            return

        self.stop_event.clear()
        self.worker = threading.Thread(
            target=self._monitor_loop,
            args=(target, self.method_var.get().strip(), interval, timeout),
            daemon=True,
        )
        self.worker.start()
        self._log(f"开始巡检: {target} | method={self.method_var.get()} | interval={interval}s")

    def stop_monitor(self) -> None:
        self.stop_event.set()
        self._log("收到停止信号。")

    def _monitor_loop(self, target: str, method: str, interval: float, timeout: float) -> None:
        total = ok_count = fail_count = 0
        latency_sum = 0.0

        while not self.stop_event.is_set():
            result = self._check_target(target, method, timeout)
            total += 1
            latency_sum += result.latency_ms
            if result.ok:
                ok_count += 1
                self._log(f"[OK] {result.target} status={result.status_code} latency={result.latency_ms:.1f}ms")
            else:
                fail_count += 1
                self._log(f"[FAIL] {result.target} err={result.error} latency={result.latency_ms:.1f}ms")

            avg = latency_sum / max(total, 1)
            self.root.after(
                0,
                lambda t=total, o=ok_count, f=fail_count, a=avg: self.stats_var.set(
                    f"请求: {t} | 成功: {o} | 失败: {f} | 平均延迟: {a:.1f} ms"
                ),
            )
            time.sleep(interval)

        self._log("巡检已停止。")

    def _check_target(self, target: str, method: str, timeout: float) -> CheckResult:
        start = time.perf_counter()
        try:
            resp = requests.request(method=method, url=target, timeout=timeout)
            latency = (time.perf_counter() - start) * 1000
            return CheckResult(target=target, ok=200 <= resp.status_code < 400, status_code=resp.status_code, latency_ms=latency)
        except Exception as exc:
            latency = (time.perf_counter() - start) * 1000
            return CheckResult(target=target, ok=False, status_code=None, latency_ms=latency, error=str(exc))

    def _load_proxies(self) -> List[str]:
        path = self.proxy_file_var.get().strip()
        if not path:
            return []
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"代理文件不存在: {path}")
        proxies = [line.strip() for line in p.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip()]
        return proxies

    def check_proxies(self) -> None:
        try:
            proxies = self._load_proxies()
        except Exception as exc:
            messagebox.showerror("代理文件错误", str(exc))
            return

        if not proxies:
            messagebox.showinfo("提示", "未加载代理；请先选择包含 ip:port 的 txt 文件")
            return

        threading.Thread(target=self._check_proxies_worker, args=(proxies,), daemon=True).start()

    def _check_proxies_worker(self, proxies: List[str]) -> None:
        self._log(f"开始代理可用性检测，总数: {len(proxies)}")
        good: List[str] = []
        test_url = self.url_var.get().strip()
        timeout = float(self.timeout_var.get().strip())

        for idx, proxy in enumerate(proxies, start=1):
            if self.stop_event.is_set():
                break
            proxy_url = f"http://{proxy}"
            mapping = {"http": proxy_url, "https": proxy_url}
            start = time.perf_counter()
            try:
                resp = requests.get(test_url, timeout=timeout, proxies=mapping)
                latency = (time.perf_counter() - start) * 1000
                if resp.status_code < 400:
                    good.append(proxy)
                    self._log(f"[Proxy OK {idx}/{len(proxies)}] {proxy} {latency:.1f}ms")
                else:
                    self._log(f"[Proxy BAD {idx}/{len(proxies)}] {proxy} status={resp.status_code}")
            except Exception as exc:
                self._log(f"[Proxy BAD {idx}/{len(proxies)}] {proxy} err={exc}")

        self.proxy_list = good
        out = Path("available_proxies.txt")
        out.write_text("\n".join(good), encoding="utf-8")
        self._log(f"代理检测完成，可用: {len(good)}，已输出到 {out.resolve()}")

    def clear_log(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("end", "[system] log cleared.\n")
        self.log_text.configure(state="disabled")

    def export_log(self) -> None:
        path = filedialog.asksaveasfilename(
            title="导出日志",
            defaultextension=".log",
            filetypes=[("Log", "*.log"), ("Text", "*.txt"), ("All", "*.*")],
        )
        if not path:
            return
        text = self.log_text.get("1.0", "end")
        Path(path).write_text(text, encoding="utf-8")
        self._log(f"日志已导出到: {path}")


def main() -> None:
    root = tk.Tk()
    app = GeekMonitorGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_event.set(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
