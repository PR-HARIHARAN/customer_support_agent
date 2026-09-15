#!/usr/bin/env python3
"""Interactive Terminal IDE (TUI) for the AmericanAir AI Support Agent.

Provides a rich, terminal-based developer workspace experience for testing
intent classification, RAG vectorstore retrieval, decision policy gating,
and grounded response generation.
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Ensure src is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

# Ensure Windows terminal handles UTF-8 glyphs gracefully
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import torch
from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from customer_support.agent.loader import load_production_agent

# Standard curated presets representing edge cases and common intents
PRESETS = [
    {
        "id": "1",
        "title": "Flight Delay & Rebooking",
        "intent": "Flight delay",
        "text": "@AmericanAir Flight AA1422 from DFW to ORD is delayed by 3 hours. Any chance I make my connection to LGA?",
    },
    {
        "id": "2",
        "title": "Damaged / Missing Baggage",
        "intent": "Baggage issues",
        "text": "@AmericanAir landed in Miami 2 hours ago and my checked bag never arrived on the carousel. Need assistance ASAP.",
    },
    {
        "id": "3",
        "title": "Sarcastic Delay Complaint (Adversarial)",
        "intent": "Disruption recovery",
        "text": "@AmericanAir Wonderful! 4 hours sitting on the tarmac with no water and no AC. Truly top notch service!",
    },
    {
        "id": "4",
        "title": "Positive Experience & Staff Kudos",
        "intent": "Positive experience",
        "text": "@AmericanAir Shoutout to flight attendant Sarah on flight AA204 today! She was so kind and helpful with my elderly mom.",
    },
    {
        "id": "5",
        "title": "Cabin Lost Item (Found in Seatback)",
        "intent": "Special assistance",
        "text": "@AmericanAir I left my iPad in seat 14B on flight 482 that just arrived at PHX. Who can I contact at the airport?",
    },
    {
        "id": "6",
        "title": "Urgent Medical / Safety Escalation",
        "intent": "Special assistance",
        "text": "@AmericanAir My mother is traveling with portable oxygen on AA918 tomorrow and customer service hung up on us. Need urgent medical clearance.",
    },
]


class AgentTUI:
    """Rich Terminal IDE User Interface for live interaction with the AI Support Agent."""

    def __init__(self) -> None:
        import platform

        self.console = Console(legacy_windows=False)
        if torch.cuda.is_available():
            self.device = "cuda"
            try:
                self.device_name = torch.cuda.get_device_name(0).strip()
            except Exception:
                self.device_name = "NVIDIA CUDA GPU"
        else:
            self.device = "cpu"
            self.device_name = platform.processor() or "Host CPU"

        self.session_queries: list[dict[str, Any]] = []
        self.agent: Any = None

    def print_banner(self) -> None:
        """Render the IDE header banner with system telemetry."""
        header_table = Table.grid(expand=True)
        header_table.add_column(justify="left", ratio=2)
        header_table.add_column(justify="right", ratio=1)

        title = Text.assemble(
            (" ✈  ", "bold yellow"),
            ("AMERICAN AIRLINES AI AGENT ", "bold bright_cyan"),
            ("│ ", "dim bright_white"),
            ("TERMINAL IDE WORKSPACE", "bold bright_white"),
        )
        telemetry = Text.assemble(
            ("HARDWARE: ", "dim"),
            (f"{self.device_name} ", "bold green" if self.device == "cuda" else "bold yellow"),
            ("│ STORE: ", "dim"),
            ("FAISS 1,500 TWEETS ", "bold magenta"),
            ("│ MODEL: ", "dim"),
            ("SOTA ENSEMBLE (76%)", "bold bright_yellow"),
        )
        header_table.add_row(title, telemetry)

        content = Group(
            header_table,
            Rule(style="cyan"),
            Text(
                "Commands:  Type any customer tweet/message  │  :1 - :6 (Presets)  │  :examples  │  :stats  │  :clear  │  :exit",
                style="dim bright_white",
            ),
        )
        self.console.print(
            Panel(content, box=box.HEAVY, border_style="cyan", padding=(0, 1)),
        )

    def load_agent(self) -> None:
        """Initialize the LangGraph pipeline with a clean spinner status."""
        with self.console.status(
            f"[bold cyan]Initializing AI Support Agent pipeline on {self.device_name}...[/bold cyan]",
            spinner="dots",
        ):
            t0 = time.time()
            self.agent = load_production_agent(device=self.device)
            load_time = time.time() - t0

        self.console.print(
            f" [bold green]✔[/bold green] [dim]Loaded SOTA Intent Ensemble + FAISS Historical Resolution Store in {load_time:.2f}s[/dim]\n"
        )

    def show_examples(self) -> None:
        """Display the preset benchmark scenarios."""
        table = Table(
            title="⚡ Curated Realistic Test Scenarios",
            box=box.ROUNDED,
            header_style="bold bright_cyan",
            border_style="dim cyan",
            expand=True,
        )
        table.add_column("Key", style="bold yellow", width=6, justify="center")
        table.add_column("Scenario / Intent", style="bold bright_white", width=25)
        table.add_column("Sample Customer Tweet", style="white")

        for p in PRESETS:
            table.add_row(f":{p['id']}", f"{p['title']}\n[dim]({p['intent']})[/dim]", p["text"])

        self.console.print(table)
        self.console.print()

    def show_stats(self) -> None:
        """Display session analytics."""
        if not self.session_queries:
            self.console.print(
                Panel("[yellow]No interactions recorded in this session yet.[/yellow]", box=box.ROUNDED)
            )
            return

        total = len(self.session_queries)
        auto = sum(1 for q in self.session_queries if q["action"] == "AUTO_HANDLE")
        esc = total - auto
        avg_conf = sum(q.get("confidence", 0.0) for q in self.session_queries) / total
        avg_lat = sum(q.get("latency_ms", 0.0) for q in self.session_queries) / total

        table = Table(
            title="📊 Session Analytics & Gating Distribution",
            box=box.ROUNDED,
            header_style="bold bright_cyan",
            border_style="dim cyan",
            expand=True,
        )
        table.add_column("Metric", style="bold white")
        table.add_column("Value", style="bold bright_yellow", justify="right")

        table.add_row("Total Inquiries Processed", str(total))
        table.add_row(
            "AUTO_HANDLE Rate",
            f"{auto} ({auto / total * 100:.1f}%) [green]✔ Low-Risk Social/Routine[/green]",
        )
        table.add_row(
            "ESCALATE Rate",
            f"{esc} ({esc / total * 100:.1f}%) [red]⚠ High-Stakes Disruption/Safety[/red]",
        )
        table.add_row("Mean Intent Confidence", f"{avg_conf * 100:.1f}%")
        table.add_row("Mean End-to-End Latency", f"{avg_lat:.1f} ms")

        self.console.print(table)
        self.console.print()

    def render_turn(self, user_msg: str, out: dict[str, Any], latency_ms: float) -> None:
        """Render the complete IDE inspection workspace for a single query."""
        intent = out.get("intent", "Unknown")
        conf = float(out.get("intent_confidence", 0.0))
        action = out.get("action", "AUTO_HANDLE")
        reason = out.get("action_reason", "N/A")
        draft = out.get("draft_reply", "").strip()
        retrieved = out.get("retrieved_resolutions", [])

        # Store for session stats
        self.session_queries.append(
            {
                "text": user_msg,
                "intent": intent,
                "confidence": conf,
                "action": action,
                "reason": reason,
                "latency_ms": latency_ms,
            }
        )

        now = datetime.now().strftime("%H:%M:%S")

        # 1. Customer Input Panel
        input_panel = Panel(
            Text(user_msg, style="bold bright_white"),
            title=f"[dim]CUSTOMER INQUIRY @ {now}[/dim]",
            title_align="left",
            box=box.ROUNDED,
            border_style="bright_blue",
        )

        # 2. Diagnostics & Metadata Table
        meta_table = Table(
            box=box.SIMPLE_HEAVY,
            expand=True,
            show_header=True,
            header_style="bold bright_cyan",
            border_style="dim cyan",
        )
        meta_table.add_column("Telemetry Key", style="dim white", width=22)
        meta_table.add_column("Value & Policy Inference", style="white")

        # Intent badge
        meta_table.add_row(
            "Classified Intent",
            f"[bold bright_yellow]{intent}[/bold bright_yellow]  [dim](Confidence: {conf:.1%})[/dim]",
        )

        # Action badge
        if action == "AUTO_HANDLE":
            action_badge = "[bold white on dark_green] AUTO_HANDLE [/bold white on dark_green] [green]Automated dispatch safe[/green]"
        else:
            action_badge = "[bold white on dark_red] ESCALATE [/bold white on dark_red] [red]Routed to human specialist[/red]"

        meta_table.add_row("Routing Decision", action_badge)
        meta_table.add_row("Policy Justification", f"[italic]{reason}[/italic]")
        meta_table.add_row("Pipeline Latency", f"[cyan]{latency_ms:.1f} ms[/cyan] [dim](GPU batch)[/dim]")

        diag_panel = Panel(
            meta_table,
            title="[bold bright_cyan]⚙ DIAGNOSTIC METADATA & POLICY GATING[/bold bright_cyan]",
            title_align="left",
            box=box.ROUNDED,
            border_style="cyan",
        )

        # 3. Vectorstore Retrieval Panel
        if retrieved:
            ret_table = Table(
                box=box.SIMPLE,
                expand=True,
                show_header=True,
                header_style="bold magenta",
                border_style="dim magenta",
            )
            ret_table.add_column("Rank", style="bold yellow", width=6, justify="center")
            ret_table.add_column("Score", style="cyan", width=8, justify="center")
            ret_table.add_column("Historical Resolution Snippet", style="white")

            for i, r in enumerate(retrieved[:3], 1):
                score = r.get("score", r.get("similarity", 0.0))
                agent_res = r.get("agent_resolution", "").replace("\n", " ")
                if len(agent_res) > 130:
                    agent_res = agent_res[:127] + "..."
                ret_table.add_row(f"#{i}", f"{score:.3f}", f"[dim]@{agent_res}[/dim]")

            vector_panel = Panel(
                ret_table,
                title=f"[bold magenta]📚 VECTORSTORE RETRIEVAL (Top {min(len(retrieved), 3)} Grounding Candidates from 1,500 Tweets)[/bold magenta]",
                title_align="left",
                box=box.ROUNDED,
                border_style="magenta",
            )
        else:
            vector_panel = Panel(
                "[dim]No historical candidates matched above retrieval threshold.[/dim]",
                title="[bold magenta]📚 VECTORSTORE RETRIEVAL[/bold magenta]",
                box=box.ROUNDED,
                border_style="magenta",
            )

        # Print header panels in logical sequence
        self.console.print(input_panel)
        self.console.print(diag_panel)
        self.console.print(vector_panel)

        # 4. Animated Agent Drafted Response Panel (Live Streaming Typewriter Effect)
        reply_style = "bright_green" if action == "AUTO_HANDLE" else "bright_yellow"
        words = draft.split()

        from rich.live import Live

        accumulated: list[str] = []
        with Live(console=self.console, refresh_per_second=30, transient=False) as live:
            for word in words:
                accumulated.append(word)
                cur_text = " ".join(accumulated)
                panel_content = Group(
                    Text.assemble(
                        (cur_text, f"bold {reply_style}"),
                        (" ▌", "bright_white blink"),
                    ),
                    Text(""),
                    Text(
                        "✔ Grounded in AmericanAir official resolution patterns  │  Privacy guard: Directs sensitive data to DM",
                        style="dim bright_black",
                    ),
                )
                live.update(
                    Panel(
                        panel_content,
                        title=f"[bold {reply_style}]🤖 AGENT DRAFTED RESPONSE ({action}) [dim](streaming...)[/dim][/bold {reply_style}]",
                        title_align="left",
                        box=box.DOUBLE,
                        border_style=reply_style,
                    )
                )
                time.sleep(0.016)

            # Final clean render without cursor
            final_content = Group(
                Text(draft, style=f"bold {reply_style}"),
                Text(""),
                Text(
                    "✔ Grounded in AmericanAir official resolution patterns  │  Privacy guard: Directs sensitive data to DM",
                    style="dim bright_black",
                ),
            )
            live.update(
                Panel(
                    final_content,
                    title=f"[bold {reply_style}]🤖 AGENT DRAFTED RESPONSE ({action})[/bold {reply_style}]",
                    title_align="left",
                    box=box.DOUBLE,
                    border_style=reply_style,
                )
            )
        self.console.print()

    def run_loop(self) -> None:
        """Main interactive REPL loop."""
        os.system("cls" if os.name == "nt" else "clear")
        self.print_banner()
        self.load_agent()

        while True:
            try:
                user_input = Prompt.ask("[bold bright_cyan]❯[/bold bright_cyan] Enter inquiry").strip()
            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[bold yellow]Exiting Terminal IDE. Goodbye![/bold yellow]\n")
                break

            if not user_input:
                continue

            # Command dispatcher
            cmd = user_input.lower()
            if cmd in (":exit", ":quit", ":q", "exit", "quit"):
                self.console.print("[bold yellow]Exiting Terminal IDE. Goodbye![/bold yellow]\n")
                break
            elif cmd in (":clear", ":cls", "clear", "cls"):
                os.system("cls" if os.name == "nt" else "clear")
                self.print_banner()
                continue
            elif cmd in (":examples", ":presets", ":help"):
                self.show_examples()
                continue
            elif cmd in (":stats", ":metrics"):
                self.show_stats()
                continue
            elif cmd.startswith(":") and cmd[1:] in [p["id"] for p in PRESETS]:
                preset_id = cmd[1:]
                matched = next(p for p in PRESETS if p["id"] == preset_id)
                user_input = matched["text"]
                self.console.print(
                    f"[dim cyan]Loading Preset #{preset_id}: {matched['title']}...[/dim cyan]"
                )

            # Process with agent
            t0 = time.perf_counter()
            with self.console.status(
                "[bold cyan]Running LangGraph pipeline (Intent + RAG + Gating + Draft)...[/bold cyan]",
                spinner="line",
            ):
                out = self.agent.run(user_input)
            latency_ms = (time.perf_counter() - t0) * 1000.0

            self.render_turn(user_input, out, latency_ms)


def main() -> None:
    tui = AgentTUI()
    tui.run_loop()


if __name__ == "__main__":
    main()
