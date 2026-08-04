from backend.services.joe_blueprint_facade import JoeBlueprintFacade


def test_joe_facade_dry_run():
    facade = JoeBlueprintFacade()
    result = facade.handle_queue_request({"blueprint": "test_blueprint", "execute": True})
    assert result["status"] == "success"
    assert result["mode"] == "dry_run"
