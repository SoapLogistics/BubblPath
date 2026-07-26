route_key = "joe_blueprint_facade"

import os
import sys

# Ensure services is in path so we can import the root engine if approved
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services import solomon_joe_bridge

def queue_blueprint(blueprint_text: str):
    """
    HTTP safe facade for J.O.E.
    Strictly enforces dry-run mode for packet generation.
    """
    # Force dry_run=True to block execution without explicit governance approval
    return solomon_joe_bridge.generate_packet(blueprint_text, dry_run=True)
