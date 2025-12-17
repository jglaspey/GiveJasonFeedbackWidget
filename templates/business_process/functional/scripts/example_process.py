#!/usr/bin/env python3
# ABOUTME: Example business process script demonstrating logging, resumability, and prompt isolation
# ABOUTME: Follow this pattern for your own business process scripts

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Set, Dict, Any
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def create_run_directory(base_dir: Path = None) -> Path:
    """Create timestamp-based run directory with subdirectories"""
    if base_dir is None:
        base_dir = project_root / "outputs"

    run_id = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir = base_dir / f"run_{run_id}"

    # Create subdirectories
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)
    (run_dir / "results").mkdir(parents=True, exist_ok=True)
    (run_dir / "errors").mkdir(parents=True, exist_ok=True)

    return run_dir


def setup_logging(run_dir: Path) -> logging.Logger:
    """Configure logging for this run"""
    log_file = run_dir / "logs" / "progress.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def log_progress(run_dir: Path, item_id: str, status: str, details: Dict[str, Any] = None):
    """Log progress for resumability - JSONL format"""
    progress_file = run_dir / "logs" / "progress.jsonl"

    entry = {
        "timestamp": datetime.now().isoformat(),
        "item_id": item_id,
        "status": status,
        "details": details or {}
    }

    with progress_file.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def load_completed_items(run_dir: Path) -> Set[str]:
    """Load IDs of already-completed items for resumability"""
    progress_file = run_dir / "logs" / "progress.jsonl"

    if not progress_file.exists():
        return set()

    completed = set()
    with progress_file.open("r") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            if entry["status"] == "completed":
                completed.add(entry["item_id"])

    return completed


def log_error(run_dir: Path, item_id: str, error: Exception, context: Dict[str, Any] = None):
    """Log error with full context for debugging"""
    import traceback

    errors_dir = run_dir / "errors"
    errors_dir.mkdir(parents=True, exist_ok=True)

    error_file = errors_dir / f"item_{item_id}_error.json"

    error_data = {
        "timestamp": datetime.now().isoformat(),
        "item_id": item_id,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        "context": context or {}
    }

    with error_file.open("w") as f:
        json.dump(error_data, f, indent=2)


def load_prompt(name: str) -> str:
    """Load prompt from functional/prompts/ directory"""
    prompt_path = project_root / "functional" / "prompts" / f"{name}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")

    return prompt_path.read_text()


def process_item(item_id: str, item_data: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
    """
    Process a single item
    Replace this with your actual business logic
    """
    logger.info(f"Processing item: {item_id}")

    # Example: Load prompt and format with data
    # prompt_template = load_prompt("example_prompt")
    # prompt = prompt_template.format(**item_data)

    # Example: Call Claude via Agent SDK
    # from claude_agent_sdk import create_session
    # session = await create_session()
    # response = await session.send_message(prompt)

    # For this example, just return mock result
    result = {
        "item_id": item_id,
        "processed": True,
        "data": item_data
    }

    return result


def main():
    """Main process execution"""

    # Create run directory
    run_dir = create_run_directory()
    logger = setup_logging(run_dir)

    logger.info(f"Starting process run: {run_dir.name}")
    logger.info(f"Run directory: {run_dir}")

    # Load items to process
    # In real implementation, load from config or arguments
    items = [
        {"id": "item_001", "data": "example data 1"},
        {"id": "item_002", "data": "example data 2"},
        {"id": "item_003", "data": "example data 3"},
    ]

    # Check for already-completed items (resumability)
    completed = load_completed_items(run_dir)
    logger.info(f"Already completed: {len(completed)} items")

    # Process each item
    results = []
    errors_count = 0

    for item in items:
        item_id = item["id"]

        # Skip if already done
        if item_id in completed:
            logger.info(f"Skipping {item_id} (already completed)")
            continue

        try:
            # Process item
            result = process_item(item_id, item, logger)
            results.append(result)

            # Log progress
            log_progress(run_dir, item_id, "completed", {"result": result})
            logger.info(f"✓ Completed {item_id}")

        except Exception as e:
            # Log error with context
            log_error(run_dir, item_id, e, context={"item": item})
            log_progress(run_dir, item_id, "failed", {"error": str(e)})
            logger.error(f"✗ Failed {item_id}: {e}")
            errors_count += 1

            # Continue with next item (fault tolerance)
            continue

    # Save final results
    results_file = run_dir / "results" / "final_output.json"
    with results_file.open("w") as f:
        json.dump(results, f, indent=2)

    # Summary
    logger.info("=" * 50)
    logger.info(f"Process complete!")
    logger.info(f"Total items: {len(items)}")
    logger.info(f"Completed: {len(results)}")
    logger.info(f"Failed: {errors_count}")
    logger.info(f"Results: {results_file}")
    logger.info("=" * 50)

    # Write summary
    summary = {
        "run_id": run_dir.name,
        "timestamp": datetime.now().isoformat(),
        "total_items": len(items),
        "completed": len(results),
        "failed": errors_count,
        "results_file": str(results_file.relative_to(project_root))
    }

    summary_file = run_dir / "results" / "summary.json"
    with summary_file.open("w") as f:
        json.dump(summary, f, indent=2)

    return 0 if errors_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
