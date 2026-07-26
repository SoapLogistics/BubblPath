import os
import pytest
from services.solomon_capability_registry import CapabilityRegistry

@pytest.fixture
def registry():
    filepath = "test_cap_registry.bin"
    reg = CapabilityRegistry(filepath)
    yield reg
    reg.close()
    if os.path.exists(filepath):
        os.remove(filepath)

def test_registry_registration(registry):
    success = registry.register_capability(
        uid="cap_01",
        name="Capability One",
        module_path="modules.cap1",
        version="1.0.0",
        owner="Jules",
        description="First test capability",
        inputs="input1",
        outputs="output1",
        permissions="exec",
        dependencies="",
        health_state="healthy",
        ss_class="SS1"
    )
    assert success is True

    cap = registry.get_capability("cap_01")
    assert cap is not None
    assert cap["uid"] == "cap_01"
    assert cap["name"] == "Capability One"
    assert cap["module_path"] == "modules.cap1"
    assert cap["version"] == "1.0.0"
    assert cap["owner"] == "Jules"
    assert cap["description"] == "First test capability"
    assert cap["inputs"] == "input1"
    assert cap["outputs"] == "output1"
    assert cap["permissions"] == "exec"
    assert cap["dependencies"] == ""
    assert cap["health_state"] == "healthy"
    assert cap["ss_class"] == "SS1"

def test_duplicate_registration(registry):
    registry.register_capability(
        uid="cap_02",
        name="Capability Two",
        module_path="modules.cap2",
        version="1.0.0",
        owner="Jules",
        description="Second test capability",
        inputs="none",
        outputs="none",
        permissions="none",
        dependencies="",
        health_state="healthy",
        ss_class="SS2"
    )

    with pytest.raises(ValueError, match="Capability already registered: cap_02"):
        registry.register_capability(
            uid="cap_02",
            name="Capability Two Duplicate",
            module_path="modules.cap2",
            version="1.0.1",
            owner="Jules",
            description="Duplicate test capability",
            inputs="none",
            outputs="none",
            permissions="none",
            dependencies="",
            health_state="healthy",
            ss_class="SS2"
        )

def test_force_update(registry):
    registry.register_capability(
        uid="cap_update",
        name="Cap Old",
        module_path="modules.cap",
        version="1.0",
        owner="Jules",
        description="Old",
        inputs="none",
        outputs="none",
        permissions="none",
        dependencies="",
        health_state="healthy",
        ss_class="SS3"
    )

    registry.register_capability(
        uid="cap_update",
        name="Cap New",
        module_path="modules.cap",
        version="1.1",
        owner="Jules",
        description="New",
        inputs="none",
        outputs="none",
        permissions="none",
        dependencies="",
        health_state="healthy",
        ss_class="SS3",
        force_update=True
    )

    cap = registry.get_capability("cap_update")
    assert cap["name"] == "Cap New"
    assert cap["version"] == "1.1"

def test_missing_dependency(registry):
    with pytest.raises(ValueError, match="Missing dependency: missing_dep"):
        registry.register_capability(
            uid="cap_03",
            name="Capability Three",
            module_path="modules.cap3",
            version="1.0.0",
            owner="Jules",
            description="Third test capability",
            inputs="none",
            outputs="none",
            permissions="none",
            dependencies="missing_dep",
            health_state="healthy",
            ss_class="SS2"
        )

def test_valid_dependency(registry):
    registry.register_capability(
        uid="base_cap",
        name="Base Cap",
        module_path="modules.base",
        version="1.0",
        owner="Jules",
        description="Base capability",
        inputs="none",
        outputs="none",
        permissions="none",
        dependencies="",
        health_state="healthy",
        ss_class="SS2"
    )

    success = registry.register_capability(
        uid="dependent_cap",
        name="Dep Cap",
        module_path="modules.dep",
        version="1.0",
        owner="Jules",
        description="Dependent capability",
        inputs="none",
        outputs="none",
        permissions="none",
        dependencies="base_cap",
        health_state="healthy",
        ss_class="SS2"
    )
    assert success is True

def test_remove_capability(registry):
    registry.register_capability(
        uid="cap_remove",
        name="Cap Remove",
        module_path="modules.remove",
        version="1.0",
        owner="Jules",
        description="To be removed",
        inputs="none",
        outputs="none",
        permissions="none",
        dependencies="",
        health_state="healthy",
        ss_class="SS2"
    )

    assert registry.get_capability("cap_remove") is not None

    success = registry.remove_capability("cap_remove")
    assert success is True

    assert registry.get_capability("cap_remove") is None

    # Verify free offset is reused
    registry.register_capability(
        uid="cap_reused",
        name="Cap Reused",
        module_path="modules.reused",
        version="1.0",
        owner="Jules",
        description="Reused offset",
        inputs="none",
        outputs="none",
        permissions="none",
        dependencies="",
        health_state="healthy",
        ss_class="SS2"
    )

    cap = registry.get_capability("cap_reused")
    assert cap is not None
    assert cap["name"] == "Cap Reused"
