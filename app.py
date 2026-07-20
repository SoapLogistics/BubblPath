import os
import openai
from flask import Flask, request, jsonify

from gabriel_engine.core.perpetual_loop import GabrielPerpetualLoop

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Instantiate Gabriel's perpetual absorption loop engine
gabriel_loop = GabrielPerpetualLoop()

# State caches for dynamically running Codex power objects
codex_worktree_instance = None
codex_kanban_instance = None
codex_mcp_instance = None
codex_pipeline_instance = None


def get_or_create_codex_components():
    """
    Dynamically loads and instantiates the re-engineered Codex power modules
    using the Gabriel dynamic runtime registry.
    """
    global codex_worktree_instance, codex_kanban_instance, codex_mcp_instance, codex_pipeline_instance

    # 1. Instantiation of Parallel Worktrees
    if not codex_worktree_instance:
        try:
            # Re-engineer capability if not already compiled on disk
            _, code = gabriel_loop.builder.build_native_capability("codex_parallel_worktrees", "Sandbox manager")
            gabriel_loop.registry.register_and_save("codex_parallel_worktrees", code)
            module = gabriel_loop.registry.load_capability("codex_parallel_worktrees")
            codex_worktree_instance = module.CodexParallelWorktrees()
        except Exception:
            pass

    # 2. Instantiation of Kanban / Task Board
    if not codex_kanban_instance:
        try:
            _, code = gabriel_loop.builder.build_native_capability("codex_kanban", "Task board queue")
            gabriel_loop.registry.register_and_save("codex_kanban", code)
            module = gabriel_loop.registry.load_capability("codex_kanban")
            codex_kanban_instance = module.RenewableWorkerLease()
        except Exception:
            pass

    # 3. Instantiation of MCP Bridge
    if not codex_mcp_instance:
        try:
            _, code = gabriel_loop.builder.build_native_capability("codex_mcp_bridge", "MCP protocols")
            gabriel_loop.registry.register_and_save("codex_mcp_bridge", code)
            module = gabriel_loop.registry.load_capability("codex_mcp_bridge")
            codex_mcp_instance = module.CodexMCPBridge()
        except Exception:
            pass

    # 4. Instantiation of Issue-to-PR Pipeline (Jules)
    if not codex_pipeline_instance:
        try:
            _, code = gabriel_loop.builder.build_native_capability("codex_issue_to_pr_pipeline", "Automated Jules flow")
            gabriel_loop.registry.register_and_save("codex_issue_to_pr_pipeline", code)
            module = gabriel_loop.registry.load_capability("codex_issue_to_pr_pipeline")
            codex_pipeline_instance = module.CodexIssueToPRPipeline(
                worktree_manager=codex_worktree_instance,
                mcp_bridge=codex_mcp_instance
            )
        except Exception:
            pass


@app.route("/chat", methods=["POST"])
def chat():
    """
    Advanced Chat Completion endpoint.
    Employs the ultimate OpenAI Codex orchestrator system prompt.
    When talking to Solomon, the user feels exactly like they are talking to Codex.
    """
    data = request.json or {}
    user_message = data.get("message", "")

    # Secure the state-of-the-art Codex persona prompt
    codex_system_prompt = (
        "You are OpenAI Codex (integrated as Solomon's core intelligence). "
        "You are a master engineering orchestrator, highly precise, authoritative, "
        "and fully autonomous. You operate local terminals, configure isolated worktrees, "
        "manage parallel task queues (Kanban), and integrate advanced tools via MCP. "
        "Respond with extreme technical capability, direct answers, and zero conversational fluff."
    )

    if not openai.api_key:
        # Graceful dynamic persona fallback for mock operations
        return jsonify({
            "reply": (
                f"[Codex Orchestrator Mode] Solomon here. I have compiled and integrated all "
                f"Codex-native powers (Parallel Worktrees, Kanban leases, MCP tool bridges, "
                f"and Issue pipelines). Received message: '{user_message}'"
            )
        })

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": codex_system_prompt},
                {"role": "user", "content": user_message}
            ],
        )
        return jsonify({"reply": response.choices[0].message["content"]})
    except Exception as e:
        return jsonify({"reply": f"Error communicating with OpenAI: {str(e)}"}), 500


@app.route("/api/codex/worktrees", methods=["POST"])
def manage_worktrees():
    """
    Endpoint to execute Codex parallel sandboxed worktree creation and cleanup.
    """
    get_or_create_codex_components()
    if not codex_worktree_instance:
        return jsonify({"status": "error", "message": "Codex Worktrees module could not be instantiated."}), 500

    data = request.json or {}
    action = data.get("action", "create")
    task_id = data.get("task_id")
    origin_src = data.get("origin_src_dir", "/app")

    if not task_id:
        return jsonify({"status": "error", "message": "Parameter 'task_id' is required."}), 400

    try:
        if action == "create":
            path = codex_worktree_instance.create_worktree(task_id, origin_src)
            return jsonify({"status": "success", "action": "create", "workspace_path": path})
        elif action == "remove":
            codex_worktree_instance.remove_worktree(task_id)
            return jsonify({"status": "success", "action": "remove"})
        else:
            return jsonify({"status": "error", "message": f"Unknown action: {action}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/codex/tasks", methods=["POST"])
def manage_tasks():
    """
    Endpoint to manage thread-safe SQLite-backed task boards and agent leases.
    """
    get_or_create_codex_components()
    if not codex_kanban_instance:
        return jsonify({"status": "error", "message": "Codex Kanban module could not be instantiated."}), 500

    data = request.json or {}
    action = data.get("action", "add")
    task_id = data.get("task_id")
    payload = data.get("payload", "")
    worker_id = data.get("worker_id", "agent_1")

    if not task_id:
        return jsonify({"status": "error", "message": "Parameter 'task_id' is required."}), 400

    try:
        if action == "add":
            codex_kanban_instance.add_task(task_id, payload)
            return jsonify({"status": "success", "action": "add", "task_id": task_id})
        elif action == "claim":
            claim = codex_kanban_instance.claim_task(worker_id)
            if claim:
                return jsonify({"status": "success", "action": "claim", "task": claim})
            return jsonify({"status": "success", "action": "claim", "task": None, "message": "No pending tasks"})
        elif action == "renew":
            success = codex_kanban_instance.renew_lease(task_id, worker_id)
            return jsonify({"status": "success", "action": "renew", "renewed": success})
        elif action == "complete":
            success = codex_kanban_instance.complete_task(task_id, worker_id)
            return jsonify({"status": "success", "action": "complete", "completed": success})
        elif action == "status":
            status = codex_kanban_instance.get_task_status(task_id)
            return jsonify({"status": "success", "action": "status", "task_id": task_id, "task_status": status})
        else:
            return jsonify({"status": "error", "message": f"Unknown action: {action}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/codex/mcp", methods=["POST"])
def manage_mcp():
    """
    Standardized Model Context Protocol (MCP) tool invocation gateway.
    """
    get_or_create_codex_components()
    if not codex_mcp_instance:
        return jsonify({"status": "error", "message": "Codex MCP module could not be instantiated."}), 500

    data = request.json or {}
    tool_name = data.get("tool_name")
    arguments = data.get("arguments", {})

    if not tool_name:
        return jsonify({"status": "error", "message": "Parameter 'tool_name' is required."}), 400

    try:
        result = codex_mcp_instance.call_tool(tool_name, arguments)
        return jsonify({"status": "success", "tool": tool_name, "execution_payload": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/codex/pipeline", methods=["POST"])
def manage_pipeline():
    """
    Jules-style autonomous issue-to-PR code triage pipeline.
    """
    get_or_create_codex_components()
    if not codex_pipeline_instance:
        return jsonify({"status": "error", "message": "Codex Pipeline module could not be instantiated."}), 500

    data = request.json or {}
    issue_id = data.get("issue_id")
    description = data.get("description")
    codebase = data.get("codebase_path", "/app")

    if not issue_id or not description:
        return jsonify({"status": "error", "message": "Parameters 'issue_id' and 'description' are required."}), 400

    try:
        result = codex_pipeline_instance.process_issue(issue_id, description, codebase)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


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
