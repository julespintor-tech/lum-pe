from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from lum_pe.engine.core import run

def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(path: str, obj: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def cmd_run(args: argparse.Namespace) -> int:
    input_obj = _load_json(args.input)
    payload = _load_json(args.payload)
    config_obj = _load_json(args.config) if args.config else input_obj.get("CONFIG", {})
    model_obj = _load_json(args.model) if args.model else input_obj.get("MODEL", {})

    # Allow 'input file' to either be raw INPUT only, or a container with INPUT/CONFIG/MODEL
    if "INPUT" in input_obj and "CONFIG" in input_obj and "MODEL" in input_obj:
        config_obj = input_obj["CONFIG"]
        model_obj = input_obj["MODEL"]
        input_obj = input_obj["INPUT"]

    bundle = run(args.problem, input_obj, config_obj, model_obj, payload)

    if args.out:
        _save_json(args.out, bundle)
    else:
        print(json.dumps(bundle, ensure_ascii=False, indent=2))
    return 0

def cmd_validate(args: argparse.Namespace) -> int:
    b = _load_json(args.bundle)
    # validation happens in engine post-checks; we just print status here
    ok = b.get("AUDIT", {}).get("post_checks_passed", False)
    notes = b.get("AUDIT", {}).get("post_checks_notes", [])
    print("post_checks_passed:", ok)
    if notes:
        print("notes:")
        for n in notes:
            print("-", n)
    return 0 if ok else 2

def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="lum", description="LUM-PE vΩ.2026-02 CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Run LUM-PE pipeline and emit bundle")
    p_run.add_argument("--problem", required=True, help="Problem text (for demarcation/PSNC-D)")
    p_run.add_argument("--input", required=True, help="Path to INPUT.json or container.json (INPUT+CONFIG+MODEL)")
    p_run.add_argument("--payload", required=True, help="Path to payload.json")
    p_run.add_argument("--config", help="Optional path to CONFIG.json (if input is only INPUT.json)")
    p_run.add_argument("--model", help="Optional path to MODEL.json (if input is only INPUT.json)")
    p_run.add_argument("--out", help="Write bundle to this path (json)")
    p_run.set_defaults(func=cmd_run)

    p_val = sub.add_parser("validate", help="Validate an emitted bundle (reads AUDIT flags)")
    p_val.add_argument("--bundle", required=True, help="Path to bundle.json")
    p_val.set_defaults(func=cmd_validate)

    args = p.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
