from typing import List, Dict, Optional

class ContextPack:
    """
    Context Packing Standard per JOE_PACKET_04_QUANTIZED_EFFICIENCY_RUNTIME.
    Compact context packs for future Codex agents to resume quickly.
    """
    __slots__ = ['objective', 'registry_summary', 'test_status', 'active_blockers',
                 'changed_files', 'artifact_status', 'next_safe_step', 'approval_posture']

    def __init__(self,
                 objective: str,
                 registry_summary: Dict[str, int],
                 test_status: str,
                 active_blockers: List[str],
                 changed_files: List[str],
                 artifact_status: str,
                 next_safe_step: str,
                 approval_posture: str):
        self.objective = objective
        self.registry_summary = registry_summary
        self.test_status = test_status
        self.active_blockers = active_blockers
        self.changed_files = changed_files
        self.artifact_status = artifact_status
        self.next_safe_step = next_safe_step
        self.approval_posture = approval_posture

    def to_dict(self):
        return {slot: getattr(self, slot) for slot in self.__slots__}
