from backend.core.reader import Reader

def test_continuity_artifacts():
    reader = Reader()
    reader.save_artifact("art1", "data")
    assert reader.artifacts["art1"]["status"] == "saved"

    reader.reopen_artifact("art1")
    assert reader.artifacts["art1"]["status"] == "reopened"

    reader.recover_artifact("art1")
    assert reader.artifacts["art1"]["status"] == "recovered"
