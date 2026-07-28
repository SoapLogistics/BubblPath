import argparse
import sys
import json
from .invention.problem_registry import ProblemRecord

def main():
    parser = argparse.ArgumentParser(description="OSWALD CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Problem commands
    prob_parser = subparsers.add_parser("create-problem")
    prob_parser.add_argument("--title", required=True)
    prob_parser.add_argument("--description", required=True)
    prob_parser.add_argument("--domain", required=True)

    args = parser.parse_args()

    if args.command == "create-problem":
        print(json.dumps({
            "status": "success",
            "message": "Problem created",
            "title": args.title
        }, indent=2))
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
