import pytest
from core.solomon_hyper_registry import HyperRegistryManager

def test_hyper_registry_lookup():
    hr = HyperRegistryManager()

    # Test existing engine
    state = hr.get_engine_state('joe_blueprint_facade')
    assert state is not None
    assert state['engine_id'] == 'joe_blueprint_facade'
    assert state['version'] == '1.0.0'
    assert state['ss_classification'] == 'SS2'
    assert state['status_class'] == 'active_route'
    assert state['health_state'] == 'healthy'
    assert state['execution_capable'] == False
    assert state['approval_required'] == False

    # Test load permission
    assert hr.is_load_permitted('joe_blueprint_facade') == True

    # Test blocked engine
    assert hr.is_load_permitted('solomon_joe_bridge') == False

    # Test anonymous (non-existent) engine
    assert hr.is_load_permitted('anonymous_hacker_engine') == False
    assert hr.get_engine_state('anonymous_hacker_engine') is None
