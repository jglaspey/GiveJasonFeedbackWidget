#!/usr/bin/env python3
# ABOUTME: CLI tool for manually recording experiment results to knowledge base
# ABOUTME: Simple interface for the manual testing workflow

import argparse
import json
from pathlib import Path
from knowledge_base import KnowledgeBase


def main():
    parser = argparse.ArgumentParser(
        description="Record experiment results to knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Record a successful experiment
  python record_experiment.py \\
    --feature skills_invocation \\
    --hypothesis "Keywords trigger invocation" \\
    --prompt "Analyze this code" \\
    --expected invoked \\
    --actual invoked \\
    --notes "Keyword 'analyze' was in skill description"

  # Record a failed experiment
  python record_experiment.py \\
    --feature skills_invocation \\
    --hypothesis "Keywords trigger invocation" \\
    --prompt "Look at this" \\
    --expected invoked \\
    --actual not_invoked \\
    --notes "Generic phrase didn't match"

  # Add a pattern you've discovered
  python record_experiment.py \\
    --add-pattern \\
    --feature skills_invocation \\
    --pattern-name "Explicit keywords work" \\
    --description "Using exact keywords from skill description triggers invocation" \\
    --confidence 0.8

  # Add a gotcha
  python record_experiment.py \\
    --add-gotcha \\
    --feature skills_invocation \\
    --title "Generic phrases don't work" \\
    --description "Phrases like 'look at' or 'check' don't trigger skills" \\
    --avoid "Use specific action verbs that match skill keywords" \\
    --severity medium

  # Show current knowledge for a feature
  python record_experiment.py --show skills_invocation
        """
    )

    # Mode selection
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--add-pattern", action="store_true",
                      help="Add a discovered pattern")
    mode.add_argument("--add-gotcha", action="store_true",
                      help="Add a gotcha/pitfall")
    mode.add_argument("--add-practice", action="store_true",
                      help="Add a best practice")
    mode.add_argument("--show", metavar="FEATURE",
                      help="Show knowledge for a feature")

    # Common args
    parser.add_argument("--feature", help="Feature name (e.g., skills_invocation)")
    parser.add_argument("--category", default="claude-code",
                        help="Feature category (default: claude-code)")
    parser.add_argument("--description", help="Feature or pattern description")

    # Experiment args
    parser.add_argument("--hypothesis", help="Hypothesis being tested")
    parser.add_argument("--prompt", help="Test prompt used")
    parser.add_argument("--expected", choices=["invoked", "not_invoked", "uncertain"],
                        help="Expected outcome")
    parser.add_argument("--actual", choices=["invoked", "not_invoked"],
                        help="Actual outcome")
    parser.add_argument("--notes", help="Notes about the experiment")
    parser.add_argument("--config", type=json.loads, default={},
                        help="JSON configuration used (optional)")

    # Pattern args
    parser.add_argument("--pattern-name", help="Name of the pattern")
    parser.add_argument("--confidence", type=float, default=0.5,
                        help="Confidence score 0.0-1.0")
    parser.add_argument("--examples", nargs="+", help="Examples of the pattern")
    parser.add_argument("--edge-cases", nargs="+", help="Edge cases discovered")

    # Gotcha args
    parser.add_argument("--title", help="Gotcha title")
    parser.add_argument("--avoid", help="How to avoid the gotcha")
    parser.add_argument("--severity", choices=["low", "medium", "high", "critical"],
                        default="medium", help="Severity level")

    # Best practice args
    parser.add_argument("--practice", help="Best practice statement")
    parser.add_argument("--rationale", help="Why this is a best practice")
    parser.add_argument("--when", help="When to use this practice")

    args = parser.parse_args()

    kb = KnowledgeBase()

    # Show mode
    if args.show:
        summary = kb.get_feature_summary(args.show)
        if not summary:
            print(f"No data found for feature: {args.show}")
            return

        print(f"\n=== {summary['feature']['name']} ===")
        print(f"Category: {summary['feature']['category']}")
        print(f"Confidence: {summary['feature']['confidence_score']:.1%}")
        print(f"Description: {summary['feature']['description']}")

        if summary['experiments']:
            print(f"\n--- Experiments ({len(summary['experiments'])}) ---")
            for exp in summary['experiments']:
                status = "✓" if exp['success'] else "✗"
                print(f"  {status} {exp['hypothesis'][:50]}...")
                print(f"    Expected: {exp['expected_outcome']}, Actual: {exp['actual_outcome']}")

        if summary['patterns']:
            print(f"\n--- Patterns ({len(summary['patterns'])}) ---")
            for pat in summary['patterns']:
                print(f"  [{pat['confidence_score']:.0%}] {pat['pattern_name']}")
                print(f"    {pat['description'][:60]}...")

        if summary['gotchas']:
            print(f"\n--- Gotchas ({len(summary['gotchas'])}) ---")
            for gotcha in summary['gotchas']:
                print(f"  [{gotcha['severity'].upper()}] {gotcha['title']}")

        if summary['best_practices']:
            print(f"\n--- Best Practices ({len(summary['best_practices'])}) ---")
            for bp in summary['best_practices']:
                print(f"  [{bp['confidence_score']:.0%}] {bp['practice'][:60]}...")

        return

    # Need feature for all other modes
    if not args.feature:
        parser.error("--feature is required")

    # Get or create feature
    feature_desc = args.description or f"Learning about {args.feature}"
    feature_id = kb.get_or_create_feature(args.feature, feature_desc, args.category)

    # Add pattern
    if args.add_pattern:
        if not args.pattern_name or not args.description:
            parser.error("--pattern-name and --description required for patterns")

        pattern_id = kb.add_pattern(
            feature_id=feature_id,
            pattern_name=args.pattern_name,
            description=args.description,
            evidence=[],
            confidence=args.confidence,
            examples=args.examples,
            edge_cases=args.edge_cases
        )
        print(f"Added pattern #{pattern_id}: {args.pattern_name}")
        return

    # Add gotcha
    if args.add_gotcha:
        if not args.title or not args.description:
            parser.error("--title and --description required for gotchas")

        gotcha_id = kb.add_gotcha(
            feature_id=feature_id,
            title=args.title,
            description=args.description,
            how_to_avoid=args.avoid or "",
            severity=args.severity
        )
        print(f"Added gotcha #{gotcha_id}: {args.title}")
        return

    # Add best practice
    if args.add_practice:
        if not args.practice:
            parser.error("--practice required for best practices")

        practice_id = kb.add_best_practice(
            feature_id=feature_id,
            practice=args.practice,
            rationale=args.rationale or "",
            when_to_use=args.when or "",
            examples=args.examples,
            confidence=args.confidence
        )
        print(f"Added best practice #{practice_id}")
        return

    # Default: record experiment
    if not args.hypothesis or not args.prompt or not args.expected or not args.actual:
        parser.error("Experiment recording requires: --hypothesis, --prompt, --expected, --actual")

    success = (args.expected == args.actual) or (args.expected == "uncertain")
    config = args.config.copy()
    config["prompt"] = args.prompt

    exp_id = kb.add_experiment(
        feature_id=feature_id,
        hypothesis=args.hypothesis,
        configuration=config,
        expected_outcome=args.expected,
        actual_outcome=args.actual,
        success=success,
        notes=args.notes or ""
    )

    status = "✓ SUCCESS" if success else "✗ FAILED"
    print(f"{status} - Experiment #{exp_id} recorded")
    print(f"  Hypothesis: {args.hypothesis}")
    print(f"  Prompt: {args.prompt}")
    print(f"  Expected: {args.expected}, Actual: {args.actual}")

    # Update feature confidence
    new_confidence = kb.calculate_feature_confidence(feature_id)
    kb.update_feature_confidence(feature_id, new_confidence)
    print(f"  Feature confidence: {new_confidence:.1%}")


if __name__ == "__main__":
    main()
