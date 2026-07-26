from backend.services.futures.futures_dashboard_facade import FuturesDashboardFacade

def test_dashboard_facade():
    facade = FuturesDashboardFacade()
    res = facade.get_dashboard_data({})
    assert res["status"] == "success"
