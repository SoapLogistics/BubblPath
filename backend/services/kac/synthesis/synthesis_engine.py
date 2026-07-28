from typing import List, Dict, Any, Tuple
import uuid
from .synthesis_models import ConflictCard, ConsensusNode, ResearchCampaign

class SynthesisEngine:
    """
    Orchestrates consensus discovery, contradiction detection, and research campaigns.
    """

    def synthesize_knowledge(self, new_facts: List[Dict[str, Any]], existing_knowledge_stub: List[Dict[str, Any]]) -> Tuple[List[ConsensusNode], List[ConflictCard], List[ResearchCampaign]]:
        """
        Takes newly extracted facts and compares them against existing memory.
        Returns newly generated Consensus Nodes, Conflict Cards, and Research Campaigns.
        """
        consensus = []
        conflicts = []
        campaigns = []

        for fact in new_facts:
            # Naive stub simulation of semantic comparison
            fact_content = fact.get("content", "").lower()

            conflict_found = False
            consensus_found = False

            for memory in existing_knowledge_stub:
                mem_content = memory.get("content", "").lower()

                # Simulate finding a contradiction (very naive inverse match)
                if "not " in fact_content and mem_content == fact_content.replace("not ", ""):
                    conflict = ConflictCard(
                        conflict_id=str(uuid.uuid4()),
                        topic="Simulated Semantic Overlap",
                        claim_a=memory,
                        claim_b=fact,
                        evidence=[memory.get("source", {}), fact.get("source", {})],
                        confidence=0.5,
                        suggested_research="Determine which source has stronger primary evidence."
                    )
                    conflicts.append(conflict)
                    conflict_found = True

                    # Create Research Campaign out of conflict
                    campaign = ResearchCampaign(
                        campaign_id=str(uuid.uuid4()),
                        question=f"Resolve conflict regarding: {conflict.topic}",
                        known_evidence=[str(memory.get("source", {}))],
                        conflicting_evidence=[str(fact.get("source", {}))],
                        missing_information="Primary data confirming either state."
                    )
                    campaigns.append(campaign)

                # Simulate finding consensus (naive exact string match or high similarity)
                elif mem_content == fact_content and mem_content != "":
                    node = ConsensusNode(
                        consensus_id=str(uuid.uuid4()),
                        topic="Simulated Consensus",
                        statement=fact_content,
                        supporting_sources=[str(memory.get("source", {})), str(fact.get("source", {}))],
                        opposing_sources=[],
                        confidence=0.9
                    )
                    consensus.append(node)
                    consensus_found = True

            if not conflict_found and not consensus_found and fact_content != "":
                # Orphaned novel fact, no synthesis action yet
                pass

        return consensus, conflicts, campaigns
