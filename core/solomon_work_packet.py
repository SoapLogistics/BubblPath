from typing import List, Optional

class WorkPacket:
    """
    Quantized Work Unit per JOE_PACKET_04_QUANTIZED_EFFICIENCY_RUNTIME.
    """
    __slots__ = ['packet_id', 'size_class', 'owner_family', 'objective',
                 'inputs', 'outputs', 'tests', 'risk', 'approval_required',
                 'memory_writeback', 'runtime_tier']

    VALID_SIZE_CLASSES = {'micro', 'small', 'medium', 'large', 'blocked'}
    VALID_RUNTIME_TIERS = {
        'T0_registry', 'T1_deterministic', 'T2_cached',
        'T3_small_reasoner', 'T4_large_reasoner', 'T5_human_gate'
    }

    def __init__(self,
                 packet_id: str,
                 size_class: str,
                 owner_family: str,
                 objective: str,
                 inputs: List[str],
                 outputs: List[str],
                 tests: List[str],
                 risk: str,
                 approval_required: bool,
                 memory_writeback: List[str],
                 runtime_tier: str = 'T1_deterministic'):

        if size_class not in self.VALID_SIZE_CLASSES:
            raise ValueError(f"Invalid size_class {size_class}. Must be one of {self.VALID_SIZE_CLASSES}")

        if runtime_tier not in self.VALID_RUNTIME_TIERS:
            raise ValueError(f"Invalid runtime_tier {runtime_tier}. Must be one of {self.VALID_RUNTIME_TIERS}")

        self.packet_id = packet_id
        self.size_class = size_class
        self.owner_family = owner_family
        self.objective = objective
        self.inputs = inputs
        self.outputs = outputs
        self.tests = tests
        self.risk = risk
        self.approval_required = approval_required
        self.memory_writeback = memory_writeback
        self.runtime_tier = runtime_tier

    def to_dict(self):
        return {slot: getattr(self, slot) for slot in self.__slots__}
