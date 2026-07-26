from services.soss_loki_picks import generate_daily_board

def test_daily_board():
    board1 = generate_daily_board(seed_str="test_seed", source_mode="simulated")
    board2 = generate_daily_board(seed_str="test_seed", source_mode="simulated")

    assert board1["config_hash"] == board2["config_hash"]
    assert "advisory" in board1
    assert board1["source_mode"] == "simulated"
    assert "timestamp" in board1
