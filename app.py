import os
import openai
from flask import Flask, request, jsonify

from gabriel_engine.core.perpetual_loop import GabrielPerpetualLoop

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Instantiate Gabriel's perpetual absorption loop engine
gabriel_loop = GabrielPerpetualLoop()


@app.route("/chat", methods=["POST"])
def chat():
    """
    Original Chat Completion endpoint.
    """
    data = request.json or {}
    user_message = data.get("message", "")

    # Check if we have an API key configured before making actual OpenAI call
    if not openai.api_key:
        return jsonify({
            "reply": f"Mock ChatGPT response: I received your message '{user_message}'. (OpenAI API key not set)"
        })

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
        )
        return jsonify({"reply": response.choices[0].message["content"]})
    except Exception as e:
        return jsonify({"reply": f"Error communicating with OpenAI: {str(e)}"}), 500


@app.route("/api/gabriel/assimilate", methods=["POST"])
def assimilate():
    """
    Triggers Gabriel's multi-stage assimilation loop on a target project/source path.
    """
    data = request.json or {}
    project_name = data.get("project_name")
    source_location = data.get("source_location")

    if not project_name or not source_location:
        return jsonify({
            "status": "error",
            "message": "Both 'project_name' and 'source_location' parameters are required."
        }), 400

    source_type = data.get("source_type", "source_repository")
    aggressive_mode = data.get("aggressive_mode", True)  # Code Thief Mode enabled by default!
    decision_overrides = data.get("decision_overrides", {})

    try:
        result = gabriel_loop.assimilate_project(
            project_name=project_name,
            source_location=source_location,
            source_type=source_type,
            aggressive_mode=aggressive_mode,
            decision_overrides=decision_overrides
        )
        return jsonify(result)
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": f"An error occurred during assimilation: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/gabriel/execute", methods=["POST"])
def execute_assimilated_code():
    """
    Dynamically executes any code capability that has been assimilated and folded into self.
    """
    data = request.json or {}
    capability_name = data.get("capability_name")
    class_name = data.get("class_name")
    method_name = data.get("method_name")

    if not capability_name or not class_name or not method_name:
        return jsonify({
            "status": "error",
            "message": "Parameters 'capability_name', 'class_name', and 'method_name' are required."
        }), 400

    init_args = data.get("init_args", [])
    init_kwargs = data.get("init_kwargs", {})
    method_args = data.get("method_args", [])
    method_kwargs = data.get("method_kwargs", {})

    try:
        result = gabriel_loop.registry.execute_capability(
            capability_name=capability_name,
            class_name=class_name,
            method_name=method_name,
            init_args=init_args,
            init_kwargs=init_kwargs,
            method_args=method_args,
            method_kwargs=method_kwargs
        )
        return jsonify({
            "status": "success",
            "capability": capability_name,
            "class": class_name,
            "method": method_name,
            "result": result
        })
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": f"Execution failed: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/gabriel/ast-inject", methods=["POST"])
def ast_inject():
    """
    Programmatically mutates class source code using AST injections.
    """
    data = request.json or {}
    file_path = data.get("file_path")
    class_name = data.get("class_name")
    function_source = data.get("function_source")

    if not file_path or not class_name or not function_source:
        return jsonify({
            "status": "error",
            "message": "Parameters 'file_path', 'class_name', and 'function_source' are required."
        }), 400

    output_path = data.get("output_path")

    try:
        new_source = gabriel_loop.ast_injector.inject_function_to_class(
            file_path=file_path,
            class_name=class_name,
            function_source=function_source,
            output_path=output_path
        )
        return jsonify({
            "status": "success",
            "message": f"Function successfully injected into class {class_name} using AST.",
            "source_code_preview": new_source[:300] + "..."
        })
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": f"AST Injection failed: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500


@app.route("/api/gabriel/optimize", methods=["POST"])
def optimize_capability():
    """
    Runs recursive self-optimizing feedback loops on code blocks.
    """
    data = request.json or {}
    capability_name = data.get("capability_name")
    original_code = data.get("original_code")
    crucible_metrics = data.get("crucible_metrics")

    if not capability_name or not original_code or not crucible_metrics:
        return jsonify({
            "status": "error",
            "message": "Parameters 'capability_name', 'original_code', and 'crucible_metrics' are required."
        }), 400

    target_latency_ms = data.get("target_latency_ms", 100.0)

    try:
        opt_code, opt_metrics, rounds = gabriel_loop.recursive_optimizer.optimize_code(
            capability_name=capability_name,
            original_code=original_code,
            crucible_metrics=crucible_metrics,
            target_latency_ms=target_latency_ms
        )
        return jsonify({
            "status": "success",
            "capability_name": capability_name,
            "rounds_completed": rounds,
            "optimized_metrics": opt_metrics,
            "optimized_code": opt_code
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Optimization failed: {str(e)}"
        }), 500


@app.route("/api/gabriel/observe", methods=["POST"])
def observe_and_deconstruct():
    """
    Performs black-box sandboxing deconstruction on closed-source CLI utilities.
    """
    data = request.json or {}
    binary_name = data.get("binary_name")

    if not binary_name:
        return jsonify({
            "status": "error",
            "message": "Parameter 'binary_name' is required."
        }), 400

    try:
        result = gabriel_loop.deconstruct_and_rebuild_binary(binary_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Observational profiling failed: {str(e)}"
        }), 500


@app.route("/api/gabriel/records", methods=["GET"])
def get_records():
    """
    Returns all generated AcquisitionRecords.
    """
    records_dict = {
        name: record.to_dict()
        for name, record in gabriel_loop.acquisition_records.items()
    }
    return jsonify(records_dict)


@app.route("/api/gabriel/anatomies", methods=["GET"])
def get_anatomies():
    """
    Returns all generated ProgramAnatomyCards.
    """
    anatomies_dict = {
        name: card.to_dict()
        for name, card in gabriel_loop.anatomy_cards.items()
    }
    return jsonify(anatomies_dict)


@app.route("/api/gabriel/capabilities", methods=["GET"])
def get_capabilities():
    """
    Returns all extracted CapabilityMemoryCards.
    """
    capabilities_dict = {
        name: [c.to_dict() for c in caps_list]
        for name, caps_list in gabriel_loop.capability_cards.items()
    }
    return jsonify(capabilities_dict)


@app.route("/api/gabriel/crucible", methods=["GET"])
def get_crucible_reports():
    """
    Returns all evaluation crucible reports.
    """
    reports_dict = {
        name: report.to_dict()
        for name, report in gabriel_loop.crucible_reports.items()
    }
    return jsonify(reports_dict)


@app.route("/api/gabriel/implementations", methods=["GET"])
def get_implementations():
    """
    Returns all generated clean-room code implementations.
    """
    return jsonify(gabriel_loop.native_implementations)


@app.route("/api/gabriel/status", methods=["GET"])
def get_status():
    """
    Returns high-level stats on historical assimilation cycles and loop status.
    """
    history = gabriel_loop.assimilation_history
    return jsonify({
        "status": "active",
        "total_assimilations": len(history),
        "history": history,
        "mode": "aggressive_code_thief_enabled"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
