import sqlite3
from typing import Any

route_key = "futures_dashboard_backend"

class FuturesDashboardBackend:
    def __init__(self, db_path="solomon_soss.db"):
        self.db_path = db_path

    def get_dashboard_data(self) -> dict[str, Any]:
        """
        GET /api/futures/dashboard logic
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                # Use a try block in case table doesn't exist yet on fresh spin up
                try:
                    cur.execute("SELECT * FROM futures_simulation_runs ORDER BY created_at DESC LIMIT 50")
                    rows = cur.fetchall()
                except sqlite3.OperationalError:
                    rows = []

                projections = []
                for row in rows:
                    projections.append({
                        "run_id": row["run_id"],
                        "candidate_id": row["candidate_id"],
                        "status": row["status"],
                        "source_mode": row["source_mode"],
                        "simulation_probability": row["simulation_probability"],
                        "interval_lower": row["interval_lower"],
                        "created_at": row["created_at"]
                    })

                return {
                    "status": "success",
                    "projections": projections,
                    "service_status": "ONLINE",
                    "degraded": False
                }
        except Exception as e: # noqa: BLE001
            return {
                "status": "error",
                "message": str(e),
                "degraded": True
            }
