#!/usr/bin/env python3
# ABOUTME: Benchmark runner for hook latency measurement
# ABOUTME: Runs hooks multiple times and calculates statistics

import subprocess
import time
import json
import statistics
import sys
from pathlib import Path

def run_hook(hook_path: str, input_data: dict, runs: int = 100) -> dict:
    """Run a hook multiple times and collect timing stats."""
    times = []

    input_json = json.dumps(input_data)

    for i in range(runs):
        start = time.perf_counter()
        proc = subprocess.run(
            [hook_path],
            input=input_json,
            capture_output=True,
            text=True
        )
        elapsed = (time.perf_counter() - start) * 1000  # ms
        times.append(elapsed)

        if proc.returncode != 0 and i == 0:
            print(f"Warning: {hook_path} returned {proc.returncode}")
            if proc.stderr:
                print(f"  stderr: {proc.stderr[:200]}")

    times.sort()
    return {
        'runs': runs,
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'min': min(times),
        'max': max(times),
        'p95': times[int(runs * 0.95)] if runs >= 20 else max(times),
        'p99': times[int(runs * 0.99)] if runs >= 100 else max(times),
    }

def format_stats(stats: dict) -> str:
    """Format stats for display."""
    return (
        f"  mean: {stats['mean']:.1f}ms | "
        f"median: {stats['median']:.1f}ms | "
        f"p95: {stats['p95']:.1f}ms | "
        f"max: {stats['max']:.1f}ms"
    )

def main():
    test_dir = Path(__file__).parent

    # Sample input data
    small_input = {
        'tool_name': 'Edit',
        'tool_input': {
            'file_path': '/test/file.py',
            'old_string': 'foo',
            'new_string': 'bar'
        }
    }

    # Medium content (~100 lines)
    medium_content = '\n'.join([f'line {i}: some code here' for i in range(100)])
    medium_input = {
        'tool_name': 'Edit',
        'tool_input': {
            'file_path': '/test/file.py',
            'old_string': 'foo',
            'new_string': medium_content
        }
    }

    # Large content (~1000 lines)
    large_content = '\n'.join([f'line {i}: some code here with more text' for i in range(1000)])
    large_input = {
        'tool_name': 'Edit',
        'tool_input': {
            'file_path': '/test/file.py',
            'old_string': 'foo',
            'new_string': large_content
        }
    }

    print("=" * 60)
    print("HOOK LATENCY BENCHMARK")
    print("=" * 60)

    # H1: Python vs Bash baseline
    print("\n## H1: Python vs Bash Baseline (empty hooks)")
    print("-" * 40)

    python_stats = run_hook(str(test_dir / 'empty_python_hook.py'), small_input)
    print(f"Python hook:")
    print(format_stats(python_stats))

    bash_stats = run_hook(str(test_dir / 'empty_bash_hook.sh'), small_input)
    print(f"Bash hook:")
    print(format_stats(bash_stats))

    print(f"\nPython overhead vs bash: {python_stats['mean'] - bash_stats['mean']:.1f}ms")

    # H2: State file I/O overhead
    print("\n## H2: State File I/O Overhead")
    print("-" * 40)

    # Ensure state file exists for read test
    state_file = Path('/tmp/latency_test_state.json')
    state_file.write_text('{"count": 0}')

    no_io_stats = run_hook(str(test_dir / 'state_no_io.py'), small_input)
    print(f"No I/O:")
    print(format_stats(no_io_stats))

    read_stats = run_hook(str(test_dir / 'state_read_only.py'), small_input)
    print(f"Read only:")
    print(format_stats(read_stats))

    write_stats = run_hook(str(test_dir / 'state_read_write.py'), small_input)
    print(f"Read + Write:")
    print(format_stats(write_stats))

    print(f"\nRead overhead: {read_stats['mean'] - no_io_stats['mean']:.1f}ms")
    print(f"Write overhead: {write_stats['mean'] - read_stats['mean']:.1f}ms")
    print(f"Total I/O overhead: {write_stats['mean'] - no_io_stats['mean']:.1f}ms")

    # H3: Content analysis overhead
    print("\n## H3: Content Analysis Overhead")
    print("-" * 40)

    print(f"Small content (minimal):")
    small_analysis = run_hook(str(test_dir / 'content_analysis.py'), small_input)
    print(format_stats(small_analysis))

    print(f"Medium content (~100 lines):")
    medium_analysis = run_hook(str(test_dir / 'content_analysis.py'), medium_input)
    print(format_stats(medium_analysis))

    print(f"Large content (~1000 lines):")
    large_analysis = run_hook(str(test_dir / 'content_analysis.py'), large_input)
    print(format_stats(large_analysis))

    print(f"\nContent analysis overhead (vs baseline):")
    print(f"  Small: {small_analysis['mean'] - python_stats['mean']:.1f}ms")
    print(f"  Medium: {medium_analysis['mean'] - python_stats['mean']:.1f}ms")
    print(f"  Large: {large_analysis['mean'] - python_stats['mean']:.1f}ms")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    # Estimate cumulative latency with realistic hooks
    estimated_cumulative = (
        python_stats['mean'] +  # Base Python overhead
        (write_stats['mean'] - no_io_stats['mean']) +  # State I/O
        (medium_analysis['mean'] - python_stats['mean'])  # Content analysis
    )

    print(f"\nEstimated cumulative latency per Edit (typical file):")
    print(f"  Python base: {python_stats['mean']:.1f}ms")
    print(f"  + State I/O: {write_stats['mean'] - no_io_stats['mean']:.1f}ms")
    print(f"  + Content analysis: {medium_analysis['mean'] - python_stats['mean']:.1f}ms")
    print(f"  = TOTAL: {estimated_cumulative:.1f}ms")

    print("\n## Targets vs Actual")
    print(f"  Individual hook < 100ms: {'✅ PASS' if python_stats['p95'] < 100 else '❌ FAIL'} (p95: {python_stats['p95']:.1f}ms)")
    print(f"  Cumulative < 300ms: {'✅ PASS' if estimated_cumulative < 300 else '❌ FAIL'} ({estimated_cumulative:.1f}ms)")
    print(f"  User perception < 500ms: {'✅ PASS' if estimated_cumulative < 500 else '❌ FAIL'}")

    # Return structured results for recording
    return {
        'h1': {
            'python': python_stats,
            'bash': bash_stats,
            'overhead': python_stats['mean'] - bash_stats['mean']
        },
        'h2': {
            'no_io': no_io_stats,
            'read_only': read_stats,
            'read_write': write_stats,
            'read_overhead': read_stats['mean'] - no_io_stats['mean'],
            'write_overhead': write_stats['mean'] - read_stats['mean'],
            'total_io_overhead': write_stats['mean'] - no_io_stats['mean']
        },
        'h3': {
            'small': small_analysis,
            'medium': medium_analysis,
            'large': large_analysis,
        },
        'estimated_cumulative': estimated_cumulative
    }

if __name__ == '__main__':
    main()
