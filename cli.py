"""
CLI interface for autodetect.

Usage:
    python -m autodetect /path/to/project
    python -m autodetect /path/to/project --output Dockerfile
    python -m autodetect /path/to/project --json
    python -m autodetect /path/to/project --framework nextjs --output Dockerfile
"""

import argparse
import json
import sys
import os
from pathlib import Path

from autodetect import __version__
from autodetect.detect import detect_framework
from autodetect.dockerfile import generate_dockerfile


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="autodetect",
        description="Smart framework detection & Dockerfile generation. "
        "Scans any project directory, detects the framework and "
        "language, and generates a production-ready Dockerfile.",
    )
    parser.add_argument(
        "project_dir",
        help="Path to the project directory to scan",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Write Dockerfile to this path instead of stdout",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output the detection result as JSON instead of a Dockerfile",
    )
    parser.add_argument(
        "--framework", "-f",
        default=None,
        help="Explicitly specify the framework (e.g. 'nextjs', 'fastapi'). "
        "Skips auto-detection.",
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"autodetect {__version__}",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress info messages, output only the Dockerfile",
    )

    args = parser.parse_args(argv)

    project_dir = os.path.abspath(args.project_dir)
    if not os.path.isdir(project_dir):
        print(f"Error: '{args.project_dir}' is not a directory", file=sys.stderr)
        return 1

    # ── Detect ────────────────────────────────────────────────────────────
    detection = detect_framework(project_dir, user_framework=args.framework)

    if detection["framework"] == "unknown":
        print(
            f"Warning: could not detect any known framework in '{project_dir}'",
            file=sys.stderr,
        )
        if not args.json:
            # Still generate a fallback Dockerfile
            pass

    if args.json:
        # ── JSON output ────────────────────────────────────────────────
        output = json.dumps(detection, indent=2, default=str)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output + "\n")
            if not args.quiet:
                print(f"Detection written to {args.output}")
        else:
            print(output)
        return 0

    # ── Generate Dockerfile ──────────────────────────────────────────────
    dockerfile = generate_dockerfile(detection, build_context=project_dir)

    if args.output:
        with open(args.output, "w") as f:
            f.write(dockerfile)
        if not args.quiet:
            print(f"Dockerfile written to {args.output}", file=sys.stderr)
            if detection["framework"] != "unknown":
                print(
                    f"Detected: {detection['framework']} ({detection['type']})",
                    file=sys.stderr,
                )
    else:
        # Print to stdout — Dockerfile only (no stderr noise)
        print(dockerfile, end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
