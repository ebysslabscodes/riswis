# tools/mteb_eval.py
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

import os
import logging

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

try:
    from transformers.utils import logging as hf_logging

    hf_logging.set_verbosity_error()
    hf_logging.disable_progress_bar()
except Exception:
    pass

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("datasets").setLevel(logging.ERROR)

import mteb


def _to_jsonable(obj):
    """
    Convert MTEB/Pydantic-ish objects to JSON-serializable structures.
    Handles ModelResult, datetime, numpy scalars/arrays, sets, Paths, etc.
    """
    # --- datetime ---
    if isinstance(obj, datetime):
        # Always ISO format (timezone-aware if possible)
        if obj.tzinfo is None:
            obj = obj.replace(tzinfo=timezone.utc)
        return obj.isoformat()

    # --- pathlib ---
    if isinstance(obj, Path):
        return str(obj)

    # --- primitives ---
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj

    # --- dict ---
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}

    # --- list/tuple/set ---
    if isinstance(obj, (list, tuple, set)):
        return [_to_jsonable(v) for v in obj]

    # --- numpy support (optional, but common in eval outputs) ---
    try:
        import numpy as np  # only if installed

        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
    except Exception:
        pass

    # --- pydantic v2 ---
    if hasattr(obj, "model_dump"):
        try:
            return _to_jsonable(obj.model_dump())
        except Exception:
            pass

    # --- pydantic v1 ---
    if hasattr(obj, "dict"):
        try:
            return _to_jsonable(obj.dict())
        except Exception:
            pass

    # --- custom ---
    if hasattr(obj, "to_dict"):
        try:
            return _to_jsonable(obj.to_dict())
        except Exception:
            pass

    # --- last resort ---
    return str(obj)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a small MTEB eval and save results."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="HF model id (e.g., sentence-transformers/all-MiniLM-L6-v2)",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        default=["STSBenchmark", "SICK-R"],
        help="Task names (space-separated). Example: STSBenchmark SICK-R",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default="results/mteb",
        help="Output directory for result JSON",
    )
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"Loading model: {args.model}")
    model = mteb.get_model(args.model)

    print(f"Running tasks: {args.tasks}")
    tasks = mteb.get_tasks(tasks=args.tasks)

    # Evaluate (API varies by version; this works for your current one)
    raw_results = mteb.evaluate(model, tasks=tasks)
    results = _to_jsonable(raw_results)

    now_utc = datetime.now(timezone.utc)
    stamp = now_utc.strftime("%Y%m%d_%H%M%S")
    outpath = outdir / f"mteb_results_{stamp}.json"

    payload = {
        "model": args.model,
        "tasks": args.tasks,
        "created_at_utc": now_utc.isoformat(),
        "results": results,
    }

    outpath.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nSaved: {outpath}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
