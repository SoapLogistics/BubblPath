from flask import Blueprint, jsonify, request

cognitive_bp = Blueprint('cognitive', __name__, url_prefix='/api/v2/cognitive-core')

@cognitive_bp.route('/health', methods=['GET'])
def health_check():
    """Liveness probe for the Cognitive Core."""
    return jsonify({"status": "active", "module": "GabrielRouter"}), 200

@cognitive_bp.route('/run-loop', methods=['POST'])
def run_loop():
    """Triggers a cycle of the Perpetual Learning Engine via Gabriel Router."""
    from solomon_core.gabriel.router import GabrielTaskRouter

    data = request.json or {}
    prompt = data.get("prompt", "Analyze system state.")

    router = GabrielTaskRouter()
    result = router.execute_task(prompt=prompt)

    return jsonify({"status": "success", "data": result}), 202

@cognitive_bp.route('/soss/mutate', methods=['POST'])
def trigger_soss_mutation():
    """Triggers the Advanced AST Injector for self-healing/live-coding."""
    # In a real scenario, this would be heavily authenticated.
    from solomon_core.soss.ast_injector import AdvancedASTInjector

    # Dummy target function to demonstrate capability
    import solomon_core.soss.ast_injector as soss_mod

    def dummy_func():
        return "original"

    setattr(soss_mod, 'dummy_func', dummy_func)

    success = AdvancedASTInjector.mutate_function(soss_mod.dummy_func, "return 'mutated by SOSS'")

    return jsonify({
        "status": "success" if success else "rollback",
        "message": "AST Mutation cycle complete."
    }), 200
