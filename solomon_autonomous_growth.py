class AutonomousGrowthEngine:
    def __init__(self, db_manager):
        self.db = db_manager

    # --- Observation Engine ---
    def record_observation(self, source, observation_type, content):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO observations (source, observation_type, content) VALUES (?, ?, ?)",
            (source, observation_type, content)
        )
        conn.commit()
        return cursor.lastrowid

    def detect_opportunities(self):
        """Analyze observations to detect technical debt, missing docs, slow code."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM observations WHERE observation_type = 'code_execution'")
        obs = cursor.fetchall()

        detected = 0
        for o in obs:
            content_lower = o['content'].lower()
            if "timed out" in content_lower or "timeout" in content_lower or "slow" in content_lower:
                self.add_research_goal(f"Optimize code related to observation {o['id']}", 5.0, 2)
                detected += 1
        return detected

    def schedule_improvement(self, experiment_id):
        """Schedule a winning experiment for deployment to SS1."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Verify the experiment won
        cursor.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,))
        exp = cursor.fetchone()

        if exp and exp['experiment_metric'] and exp['baseline_metric'] and exp['experiment_metric'] > exp['baseline_metric']:
            # Schedule for promotion
            cursor.execute("UPDATE experiments SET status = 'scheduled_for_promotion' WHERE id = ?", (experiment_id,))
            conn.commit()
            return True
        return False

    # --- Experiment Engine ---
    def log_experiment(self, name, baseline_metric=None, experiment_metric=None, status="pending", result=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO experiments
               (name, baseline_metric, experiment_metric, status, result)
               VALUES (?, ?, ?, ?, ?)""",
            (name, baseline_metric, experiment_metric, status, result)
        )
        conn.commit()
        return cursor.lastrowid

    def evaluate_experiment(self, experiment_id):
        """Measure experiment results against baseline."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,))
        exp = cursor.fetchone()

        if exp and exp['experiment_metric'] is not None and exp['baseline_metric'] is not None:
            if exp['experiment_metric'] > exp['baseline_metric']:
                cursor.execute("UPDATE experiments SET result = 'success', status = 'completed' WHERE id = ?", (experiment_id,))
            else:
                cursor.execute("UPDATE experiments SET result = 'failure', status = 'rejected' WHERE id = ?", (experiment_id,))
            conn.commit()
            return True
        return False

    # --- Curiosity Engine ---
    def add_research_goal(self, topic, expected_value=0.0, priority=1):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO research_goals (topic, expected_value, priority) VALUES (?, ?, ?)",
            (topic, expected_value, priority)
        )
        conn.commit()
        return cursor.lastrowid

    def add_daily_question(self, question):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO daily_questions (question) VALUES (?)",
            (question,)
        )
        conn.commit()
        return cursor.lastrowid
