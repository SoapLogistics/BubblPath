import json

class KnowledgeGraphEngine:
    def __init__(self, db_manager):
        self.db = db_manager

    def add_graph_node(self, node_id, node_type, properties=None, cluster_id=None):
        if properties is None:
            properties = {}
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO graph_nodes (id, type, properties, cluster_id) VALUES (?, ?, ?, ?)",
            (node_id, node_type, json.dumps(properties), cluster_id)
        )
        conn.commit()
        return node_id

    def add_graph_edge(self, source_id, target_id, relationship, weight=1.0,
                       confidence=1.0, temporal_start=None, temporal_end=None, source_attribution=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO graph_edges
               (source_id, target_id, relationship, weight, confidence, temporal_start, temporal_end, source_attribution)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (source_id, target_id, relationship, weight, confidence, temporal_start, temporal_end, source_attribution)
        )
        conn.commit()
        return cursor.lastrowid

    def get_graph(self):
         conn = self.db.get_connection()
         cursor = conn.cursor()
         cursor.execute("SELECT * FROM graph_nodes")
         nodes = []
         for row in cursor.fetchall():
             n = dict(row)
             if n.get('properties'):
                 try:
                     n['properties'] = json.loads(n['properties'])
                 except json.JSONDecodeError:
                     pass
             nodes.append(n)

         cursor.execute("SELECT * FROM graph_edges")
         edges = [dict(row) for row in cursor.fetchall()]

         return {"nodes": nodes, "edges": edges}

    def summarize_graph_cluster(self, cluster_id):
        """Phase 2: Graph summarization - aggregations for a node cluster."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM graph_nodes WHERE cluster_id = ?", (cluster_id,))
        node_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM graph_edges
            WHERE source_id IN (SELECT id FROM graph_nodes WHERE cluster_id = ?)
            OR target_id IN (SELECT id FROM graph_nodes WHERE cluster_id = ?)
        """, (cluster_id, cluster_id))
        edge_count = cursor.fetchone()[0]

        return {
            "cluster_id": cluster_id,
            "total_nodes": node_count,
            "total_edges_connected": edge_count
        }

    def semantic_link_nodes(self):
         """Detect semantic similarity, dependencies, causal links."""
         conn = self.db.get_connection()
         cursor = conn.cursor()

         # Mock implementation:
         # 1. Randomly link disconnected nodes that share similar type
         # 2. Add prerequisites if node names imply order (e.g. Phase 1 -> Phase 2)
         cursor.execute("SELECT * FROM graph_nodes")
         nodes = cursor.fetchall()

         new_edges = 0
         for i in range(len(nodes)):
             for j in range(i + 1, len(nodes)):
                 n1 = nodes[i]
                 n2 = nodes[j]

                 # Basic similarity linking
                 if n1['type'] == n2['type']:
                     cursor.execute("SELECT id FROM graph_edges WHERE source_id = ? AND target_id = ?", (n1['id'], n2['id']))
                     if not cursor.fetchone():
                         self.add_graph_edge(n1['id'], n2['id'], "similar_type", 0.5)
                         new_edges += 1

                 # Prerequisite linking
                 if "phase 1" in n1['id'].lower() and "phase 2" in n2['id'].lower():
                     self.add_graph_edge(n1['id'], n2['id'], "prerequisite", 1.0)
                     new_edges += 1

         # Advanced Relationships (Causal/Dependency mock)
         # Find a node labeled 'bug' and link it to a 'fix' node if one exists
         cursor.execute("SELECT id FROM graph_nodes WHERE type = 'bug'")
         bugs = cursor.fetchall()
         cursor.execute("SELECT id FROM graph_nodes WHERE type = 'fix'")
         fixes = cursor.fetchall()

         for b in bugs:
             for f in fixes:
                 cursor.execute("SELECT id FROM graph_edges WHERE source_id = ? AND target_id = ?", (b['id'], f['id']))
                 if not cursor.fetchone():
                     self.add_graph_edge(b['id'], f['id'], "resolved_by", 0.9)
                     new_edges += 1

         return new_edges

    def detect_orphan_nodes(self):
        """Find and repair/remove orphan nodes."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM graph_nodes
            WHERE id NOT IN (SELECT source_id FROM graph_edges)
            AND id NOT IN (SELECT target_id FROM graph_edges)
        """)
        orphans = cursor.fetchall()

        # Link orphans to a central "Uncategorized" node
        if orphans:
            self.add_graph_node("Uncategorized", "cluster")
            for orphan in orphans:
                self.add_graph_edge(orphan['id'], "Uncategorized", "belongs_to", 0.1)

        return len(orphans)
