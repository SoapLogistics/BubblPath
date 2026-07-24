from solomon_db_manager import SolomonDBManager
from solomon_perpetual_learning import PerpetualLearningEngine
from solomon_knowledge_graph import KnowledgeGraphEngine
from solomon_autonomous_growth import AutonomousGrowthEngine
from solomon_meta_learning import MetaLearningEngine

class SolomonCognitiveArchitecture:
    """
    Facade class that binds the four modular campaigns together.
    """
    def __init__(self, db_path="cognitive_architecture.db"):
        self.db = SolomonDBManager(db_path)
        self.perpetual_learning = PerpetualLearningEngine(self.db)
        self.knowledge_graph = KnowledgeGraphEngine(self.db)
        self.autonomous_growth = AutonomousGrowthEngine(self.db)
        self.meta_learning = MetaLearningEngine(self.db)

    # --- Campaign I Delegates ---
    def record_learning_event(self, *args, **kwargs):
        return self.perpetual_learning.record_learning_event(*args, **kwargs)

    def get_learning_events(self, *args, **kwargs):
        return self.perpetual_learning.get_learning_events(*args, **kwargs)

    def extract_procedures(self, *args, **kwargs):
        return self.perpetual_learning.extract_procedures(*args, **kwargs)

    # --- Campaign II Delegates ---
    def add_graph_node(self, *args, **kwargs):
        return self.knowledge_graph.add_graph_node(*args, **kwargs)

    def add_graph_edge(self, *args, **kwargs):
        return self.knowledge_graph.add_graph_edge(*args, **kwargs)

    def get_graph(self, *args, **kwargs):
        return self.knowledge_graph.get_graph(*args, **kwargs)

    def semantic_link_nodes(self, *args, **kwargs):
        return self.knowledge_graph.semantic_link_nodes(*args, **kwargs)

    # --- Campaign III Delegates ---
    def log_experiment(self, *args, **kwargs):
        return self.autonomous_growth.log_experiment(*args, **kwargs)

    def add_research_goal(self, *args, **kwargs):
        return self.autonomous_growth.add_research_goal(*args, **kwargs)

    def add_daily_question(self, *args, **kwargs):
        return self.autonomous_growth.add_daily_question(*args, **kwargs)

    # --- Campaign IV Delegates ---
    def log_meta_metric(self, *args, **kwargs):
        return self.meta_learning.log_meta_metric(*args, **kwargs)

    def get_meta_metrics(self, *args, **kwargs):
        return self.meta_learning.get_meta_metrics(*args, **kwargs)

    def log_tool_effectiveness(self, *args, **kwargs):
        return self.meta_learning.log_tool_effectiveness(*args, **kwargs)
