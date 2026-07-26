route_key = "joe_root_engine"

def generate_packet(blueprint_text: str, dry_run: bool = True):
    """
    Root J.O.E. engine for generating work packets.
    Strictly forbids subprocess execution if dry_run is True.
    """
    # Analyze categories, produce task packets, estimate helper count, etc.
    packet_proposal = {
        "tasks": ["Analyze blueprint", "Formulate strategy"],
        "risk": "low",
        "tests_required": True,
        "files_impacted": [],
        "approvals_required": ["Mark"],
        "next_steps": ["Review governance packet"]
    }

    if not dry_run:
        raise PermissionError("Approved execution mode not implemented yet (future only). Requires Mark approval, governance packet, repo allowlist, etc.")

    return packet_proposal
