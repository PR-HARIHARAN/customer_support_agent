"""CLI entrypoint for the customer-support-agent reproducible pipeline.

Subcommands:

* ``python main.py agent "<message>"`` -- run the LangGraph support agent on a customer tweet.
* ``python main.py eval [--sample-size 30]`` -- run the complete evaluation harness.
* ``python main.py golden-report`` -- print golden evaluation set distribution & statistics.
* ``python main.py pilot`` -- run the small intent-classification baseline pilot.

Other entrypoints:

* ``streamlit run app.py``       -- browse the reconstructed conversations.
* ``streamlit run label_app.py`` -- label the human golden set.

See README.md for the full reproduction walkthrough.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def run_agent_cli(args: list[str]) -> int:
    """Run interactive or one-shot agent execution."""
    parser = argparse.ArgumentParser(description="Run AmericanAir AI Support Agent.")
    parser.add_argument(
        "message",
        nargs="?",
        default="My flight AA1842 was cancelled in Chicago. How do I get rebooked?",
        help="Customer message text to process.",
    )
    parsed = parser.parse_args(args)

    from customer_support.agent import load_production_agent

    print("\n" + "=" * 60)
    print("  AmericanAir AI Customer Support Agent (LangGraph)")
    print("=" * 60)
    print(f'\n[Incoming Customer Tweet]:\n  "{parsed.message}"\n')
    print("Loading agent pipeline & SOTA models...")

    agent = load_production_agent()
    result = agent.run(parsed.message)

    print("\n--- Agent Execution Output ---")
    print(
        f"Predicted Intent:      {result['intent']} (confidence: {result.get('intent_confidence', 1.0):.2f})"
    )
    print(f"Routing Action:        {result['action']}")
    print(f"Action Justification:  {result['action_reason']}")
    print("\n[Drafted Grounded Reply]:")
    print(f'  "{result["draft_reply"]}"')

    retrieved = result.get("retrieved_resolutions", [])
    if retrieved:
        print(f"\n[Top Historical Match (sim: {retrieved[0]['score']:.3f})]:")
        print(f'  Historical Query:    "{retrieved[0]["customer_query"][:80]}..."')
        print(f'  Historical Agent:    "{retrieved[0]["agent_resolution"][:100]}..."')

    print("\n" + "=" * 60 + "\n")
    return 0


def run_eval_cli(args: list[str]) -> int:
    """Run full evaluation harness."""
    from scripts.run_eval_harness import main as run_eval

    # Ensure scripts directory is importable
    scripts_dir = Path(__file__).resolve().parent / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return run_eval(args)


def run_golden_report_cli(args: list[str]) -> int:
    """Print golden set validation summary."""
    from scripts.golden_set_report import main as run_report

    scripts_dir = Path(__file__).resolve().parent / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    return run_report(args)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    command, rest = args[0], args[1:]
    if command == "agent":
        return run_agent_cli(rest)
    if command == "eval":
        return run_eval_cli(rest)
    if command == "golden-report":
        return run_golden_report_cli(rest)
    if command == "pilot":
        from customer_support.pipeline.run_pilot import main as run_pilot

        return run_pilot(rest)

    print(f"Unknown command: {command!r}\n\n{__doc__}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
