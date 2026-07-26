from backend.services.joe_blueprint_facade import JoeBlueprintFacade

def test_joe_blueprint_facade_dry_run():
    facade = JoeBlueprintFacade()
    payload = {"blueprint": "test_blueprint", "execute": False}
    result = facade.handle_queue_request(payload)
    assert result["status"] == "success"
    assert result["mode"] == "dry_run"
    assert result["data"] == "test_blueprint"

def test_joe_blueprint_facade_execute_blocked():
    facade = JoeBlueprintFacade()
    payload = {"blueprint": "test_blueprint", "execute": True}
    result = facade.handle_queue_request(payload)
    assert result["status"] == "success"
    assert result["mode"] == "dry_run"
