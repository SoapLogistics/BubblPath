import pytest
from gabriel_engine.core.dynamic_loader import DynamicCapabilityRegistry

def test_dynamic_loader_blocks_anonymous_capabilities():
    loader = DynamicCapabilityRegistry(target_dir="/tmp/assimilated")

    # Simulate saving an anonymous (unregistered) capability
    loader.register_and_save("hacker_module", "print('I should not run')")

    with pytest.raises(PermissionError) as exc_info:
        loader.load_capability("hacker_module")

    assert "prohibited by Solomon Governance" in str(exc_info.value)

def test_dynamic_loader_blocks_approval_blocked_capabilities():
    loader = DynamicCapabilityRegistry(target_dir="/tmp/assimilated")

    # solomon_joe_bridge is approval_blocked
    with pytest.raises(PermissionError) as exc_info:
        loader.load_capability("solomon_joe_bridge")

    assert "prohibited by Solomon Governance" in str(exc_info.value)
