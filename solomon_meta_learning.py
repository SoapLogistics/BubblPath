class MetaLearningEngine:
    def __init__(self, db_manager):
        self.db = db_manager

    def log_meta_metric(self, metric_name, metric_value, context=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO meta_learning_metrics (metric_name, metric_value, context) VALUES (?, ?, ?)",
            (metric_name, metric_value, context)
        )
        conn.commit()
        return cursor.lastrowid

    def get_meta_metrics(self, limit=10):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM meta_learning_metrics ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def log_tool_effectiveness(self, tool_name, category, success_rate):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO tool_effectiveness
               (tool_name, category, success_rate, usage_count)
               VALUES (?, ?, ?, 1)
               ON CONFLICT(tool_name) DO UPDATE SET
               success_rate = (tool_effectiveness.success_rate * tool_effectiveness.usage_count + ?) / (tool_effectiveness.usage_count + 1),
               usage_count = tool_effectiveness.usage_count + 1""",
            (tool_name, category, success_rate, success_rate)
        )
        conn.commit()
        return cursor.lastrowid

    def optimize_chunk_size(self):
        """Analyze retrieval accuracy metrics to optimize vector chunk sizes."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT metric_value FROM meta_learning_metrics WHERE metric_name = 'retrieval_accuracy' ORDER BY timestamp DESC LIMIT 5")
        accuracies = [row['metric_value'] for row in cursor.fetchall()]

        if not accuracies:
            return 512

        avg_acc = sum(accuracies) / len(accuracies)
        if avg_acc < 0.8:
            new_size = 256
        elif avg_acc > 0.95:
            new_size = 1024
        else:
            new_size = 512

        self.log_meta_metric("optimized_chunk_size", new_size, context="auto_tuned")
        return new_size
