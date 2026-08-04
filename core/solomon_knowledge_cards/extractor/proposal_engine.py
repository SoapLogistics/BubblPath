import datetime
import uuid
import os
import re
from typing import Optional
from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.models.card import KnowledgeCard

class ProposalEngine:
    def __init__(self, repository: CardRepository):
        self.repository = repository

    def create_procedure_proposal(
        self,
        repair_card_id: str,
        creator: str = "proposal_engine"
    ) -> Optional[KnowledgeCard]:
        """
        Automatically generates a PROPOSAL type card for an approved REPAIR card.
        Queries the repository for the parent procedure referenced by the repair card,
        reads the target procedure markdown, and drafts a dry-run update proposal.
        Does NOT modify the file on disk.
        """
        repair_card = self.repository.get_card(repair_card_id)
        if not repair_card:
            raise ValueError(f"Repair card {repair_card_id} not found.")

        if repair_card.card_type != "REPAIR":
            raise ValueError(f"Card {repair_card_id} is not of type REPAIR.")

        # Find target procedure ID from the repair card source IDs
        procedure_id = None
        for s_id in repair_card.source_ids:
            if s_id.startswith("PC-"):
                procedure_id = s_id
                break

        if not procedure_id:
            # Fallback
            procedure_id = "PC-GENERIC"

        # Try to retrieve the original legacy Doctrine card from the database to find original file path
        legacy_card = self.repository.get_card(procedure_id)
        file_path = None

        if legacy_card:
            file_path = legacy_card.extra_metadata.get("original_file_path")
        else:
            # Fallback: search checklists folder for file ending in name
            checklists_dir = "openclaw-workspace/checklists/"
            if os.path.exists(checklists_dir):
                for f in os.listdir(checklists_dir):
                    if f.endswith(".md") and procedure_id.lower().replace("pc-", "") in f.lower():
                        file_path = os.path.join(checklists_dir, f)
                        break

        # Resolve content safely without overwriting file_path fallback if file_path was found
        if not file_path:
            file_path = f"openclaw-workspace/checklists/{procedure_id.lower()}.md"

        # Draft a safe proposed patch
        remediation_actions = repair_card.body
        proposal_id = f"PP-{uuid.uuid4().hex[:8].upper()}"
        now_str = datetime.datetime.now(datetime.UTC).isoformat()

        title = f"Proposal: Safe procedural update to {procedure_id}"
        summary = f"Proposed operational update based on approved remediation {repair_card_id} to prevent port and environment conflicts."

        # Build dry-run proposal body
        formatted_remediation = remediation_actions.replace('\n', '\n  > ')
        proposal_body = (
            f"### Proposed Procedure Amendment\n"
            f"**Target Document:** `{file_path}`\n"
            f"**Procedure ID:** `{procedure_id}`\n"
            f"**Triggering Repair Card:** `{repair_card_id}`\n"
            f"**Proposed Modification:**\n"
            f"Append the following remediation instruction into the 'Remediation/Self-Healing' checklist section of {procedure_id}:\n\n"
            f"```markdown\n"
            f"## [PROPOSED] Self-Healing Protocol\n"
            f"- Before executing tool deployments, execute port diagnostics and resolve binding conflicts as detailed in {repair_card_id}:\n"
            f"  > {formatted_remediation}\n"
            f"```\n"
        )

        proposal_card = KnowledgeCard(
            card_id=proposal_id,
            card_type="PROPOSAL",
            schema_version="1.0.0",
            title=title,
            summary=summary,
            body=proposal_body,
            status="DRAFT",  # All proposals start as DRAFT
            confidence=repair_card.confidence,
            validation_state="UNVALIDATED",
            created_at=now_str,
            updated_at=now_str,
            created_by=creator,
            source_type="REPAIR_CARD",
            source_ids=[repair_card_id, procedure_id],
            parent_card_ids=[procedure_id],
            related_card_ids=[repair_card_id],
            tags=["proposal", "mutation", "procedure-update", procedure_id.lower()],
            security_classification="INTERNAL",
            evidence=f"Repair card {repair_card_id} successfully resolved a deployment block in active worker task logs.",
            why_created=f"To safely propogate the remediation from {repair_card_id} into canonical standard operating checklists without silent disk corruption.",
            problem_solved=f"Prevents future instances of {procedure_id} from hitting the same unmitigated failure pathway.",
            future_work_dependent=f"Future runs of {procedure_id} will reference this active proposal to execute self-healing steps."
        )

        self.repository.create_card(proposal_card, creator=creator, reason="Automatically generated proposal from repair codification")
        return proposal_card

    def apply_proposal_to_disk(self, proposal_id: str, operator: str = "operator") -> bool:
        """
        Simulates the safe, human-reviewed/approved mutation of a procedure checklist file on disk.
        Only allowed if the Proposal Card is in APPROVED status.
        """
        proposal = self.repository.get_card(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found.")

        if proposal.card_type != "PROPOSAL":
            raise ValueError(f"Card {proposal_id} is not of type PROPOSAL.")

        if proposal.status != "APPROVED" and proposal.status != "ACTIVE":
            print(f"[ProposalEngine] Safe Mutation Aborted: Proposal {proposal_id} status is {proposal.status}. Must be APPROVED/ACTIVE first.")
            return False

        # Extract target file path from body using robust regex allowing bold markdown formatting asterisks
        match = re.search(r"Target Document:.*?`([^`]+)`", proposal.body)
        if not match:
            print("[ProposalEngine] File path parsing failed from proposal body.")
            return False

        target_file_path = match.group(1)
        if not os.path.exists(target_file_path):
            # Create parents directories if not exist
            os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
            # Create a basic stub to write to
            with open(target_file_path, "w", encoding="utf-8") as f:
                f.write("# Procedure Card\n")

        # Read original text
        with open(target_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Safely append the proposed section at the end of the file (or merge)
        proposed_block_match = re.search(r"```markdown\n(.*?)\n```", proposal.body, re.DOTALL)
        if not proposed_block_match:
            print("[ProposalEngine] Proposed markdown block parsing failed from proposal body.")
            return False

        proposed_block = proposed_block_match.group(1)

        # Verify the block isn't already appended
        if proposed_block in content:
            print(f"[ProposalEngine] Amendment already exists in file {target_file_path}. Skipping write.")
            return True

        # Append to file
        updated_content = content.rstrip() + "\n\n" + proposed_block + "\n"
        with open(target_file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        print(f"[ProposalEngine] Mutation Triggered: Safely applied proposal {proposal_id} to file {target_file_path}")
        return True
