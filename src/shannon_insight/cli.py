"""Command-line interface for Shannon Insight"""

import sys
import argparse
from .core import CodebaseAnalyzer


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Shannon Insight - Multi-Signal Codebase Quality Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  shannon-insight /path/to/codebase
  shannon-insight /path/to/codebase --language go
  shannon-insight /path/to/codebase --top 20 --output results.json

Named after Claude Shannon, father of information theory.
        """,
    )

    parser.add_argument(
        "path", help="Path to the codebase directory to analyze", nargs="?", default="."
    )

    parser.add_argument(
        "-l",
        "--language",
        choices=["auto", "go", "typescript", "react", "javascript"],
        default="auto",
        help="Programming language (default: auto-detect)",
    )

    parser.add_argument(
        "-t",
        "--top",
        type=int,
        default=15,
        help="Number of top files to display (default: 15)",
    )

    parser.add_argument(
        "-o", "--output", help="Output JSON file path (default: analysis_report.json)"
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=1.5,
        help="Z-score threshold for anomaly detection (default: 1.5)",
    )

    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.1.0"
    )

    args = parser.parse_args()

    # Run analysis
    analyzer = CodebaseAnalyzer(args.path, language=args.language)
    reports = analyzer.analyze()

    # Print results
    if reports:
        analyzer.print_report(reports, top_n=args.top)

        # Export JSON
        output_file = args.output or "analysis_report.json"
        analyzer.export_json(reports, filename=output_file)

        print()
        print("=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
    else:
        print("No anomalies detected or no files found to analyze.")
        sys.exit(1)


if __name__ == "__main__":
    main()
