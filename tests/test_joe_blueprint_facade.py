import pytest
from backend.services.joe_blueprint_facade import JoeBlueprintFacade

def test_joe_facade_dry_run_default():
    facade = JoeBlueprintFacade()
    result = facade.handle_queue_request({"blueprint": "test_blueprint"})
    assert result.get("mode") == "dry_run"

def test_joe_facade_blocks_execute():
    facade = JoeBlueprintFacade()
    result = facade.handle_queue_request({"blueprint": "test_blueprint", "execute": True})
    assert result.get("mode") == "dry_run" # Should still be dry run because facade hardcodes it

if __name__ == "__main__":
    test_joe_facade_dry_run_default()
    test_joe_facade_blocks_execute()
    print("Facade tests passed")
