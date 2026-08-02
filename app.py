import os
import traceback
import openai
import threading
import time
import subprocess
import sys
import logging
from flask import Flask, request, jsonify, render_template

from gabriel_engine.core.perpetual_loop import GabrielPerpetualLoop
from core.solomon_quantized_memory import QuantizedBrainMap
from backend.services.futures_dashboard_backend import FuturesDashboardBackend
from core.solomon_web_crawler import SolomonWebCrawler
from core.agentic_claw import SolomonAgenticClaw
from core.solomon_local_llm import SolomonLocalLLM

app = Flask(__name__)
unified_memory = QuantizedBrainMap()
unified_memory.start_ans()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Instantiate Gabriel's perpetual absorption loop engine
gabriel_loop = GabrielPerpetualLoop()

# State caches for dynamically running Codex & Jules power objects
codex_worktree_instance = None
codex_kanban_instance = None
codex_mcp_instance = None
codex_pipeline_instance = None

jules_installer_instance = None
jules_patcher_instance = None
jules_test_loop_instance = None


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
        except Exception as e:
            logging.error(f"Failed to load codex_parallel_worktrees: {e}")

    # 2. Instantiation of Kanban / Task Board
    if not codex_kanban_instance:
        try:
            _, code = gabriel_loop.builder.build_native_capability("codex_kanban", "Task board queue")
            gabriel_loop.registry.register_and_save("codex_kanban", code)
            module = gabriel_loop.registry.load_capability("codex_kanban")
            codex_kanban_instance = module.RenewableWorkerLease()
        except Exception as e:
            logging.error(f"Failed to load codex_kanban: {e}")

    # 3. Instantiation of MCP Bridge
    if not codex_mcp_instance:
        try:
            _, code = gabriel_loop.builder.build_native_capability("codex_mcp_bridge", "MCP protocols")
            gabriel_loop.registry.register_and_save("codex_mcp_bridge", code)
            module = gabriel_loop.registry.load_capability("codex_mcp_bridge")
            codex_mcp_instance = module.CodexMCPBridge()
        except Exception as e:
            logging.error(f"Failed to load codex_mcp_bridge: {e}")

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
        except Exception as e:
            logging.error(f"Failed to load codex_autonomous_pipeline: {e}")


def get_or_create_jules_components():
    """
    Dynamically loads and instantiates the re-engineered Jules power modules
    using the Gabriel dynamic runtime registry.
    """
    global jules_installer_instance, jules_patcher_instance, jules_test_loop_instance

    # 1. Instantiation of Dependency Installer
    if not jules_installer_instance:
        try:
            _, code = gabriel_loop.builder.build_native_capability("jules_dependency_installer", "Package setup assistant")
            gabriel_loop.registry.register_and_save("jules_dependency_installer", code)
            module = gabriel_loop.registry.load_capability("jules_dependency_installer")
            jules_installer_instance = module.JulesDependencyInstaller()
        except Exception as e:
            logging.error(f"Failed to load jules_dependency_installer: {e}")

    # 2. Instantiation of Code Patcher
    if not jules_patcher_instance:
        try:
            _, code = gabriel_loop.builder.build_native_capability("jules_code_patcher", "Unified diff applier")
            gabriel_loop.registry.register_and_save("jules_code_patcher", code)
            module = gabriel_loop.registry.load_capability("jules_code_patcher")
            jules_patcher_instance = module.JulesCodePatcher()
        except Exception as e:
            logging.error(f"Failed to load jules_code_patcher: {e}")

    # 3. Instantiation of Test Runner Loop
    if not jules_test_loop_instance:
        try:
            _, code = gabriel_loop.builder.build_native_capability("jules_test_runner_loop", "Test traceback solver")
            gabriel_loop.registry.register_and_save("jules_test_runner_loop", code)
            module = gabriel_loop.registry.load_capability("jules_test_runner_loop")
            jules_test_loop_instance = module.JulesTestRunnerLoop()
        except Exception as e:
            logging.error(f"Failed to load jules_test_runner_loop: {e}")


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    """
    Global SOSS exception handler to prevent any thread crash from leaking or dropping the service.
    """
    response = {
        "status": "error",
        "message": f"Global SOSS Boundary Intercepted Crash: {str(error)}",
        "traceback": traceback.format_exc()
    }
    return jsonify(response), 500


@app.route("/talk", methods=["GET"])
def talk():
    """Serves the Native Solomon Chat Interface"""
    return render_template("solomon_chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    """
    Native Solomon Central Nervous System interface.
    Bypasses external LLMs to directly expose internal state, memory recall, and loop metrics.
    """
    data = request.json or {}
    user_message = data.get("message", "").strip()

    # 1. Access Quantized Brain Map for associated memories
    memory_results = unified_memory.recall(user_message, top_k=3)
    
    # 2. Access Gabriel Perpetual Loop state
    assimilation_count = len(gabriel_loop.assimilation_history)
    capabilities_loaded = gabriel_loop.registry._loaded_keys
    
    # 3. Access Unified Memory Stats
    mem_stats = unified_memory.get_stats()

    # 4. Construct programmatic, machine-native response
    response_lines = [
        "[SYSTEM] SOLOMON NATIVE CORE DIRECT INTERFACE",
        f"> INPUT RECEIVED: '{user_message}'",
        "---",
        f"[STATE] TOTAL ASSIMILATIONS: {assimilation_count}",
        f"[STATE] CAPABILITIES ACTIVE: {len(capabilities_loaded)}",
        f"[MEMORY] ATOMS STORED: {mem_stats.get('total_nodes', 0)}",
        f"[MEMORY] CLUSTERS: {mem_stats.get('total_clusters', 0)}",
        "---",
        "[RECALL] NEURAL ASSOCIATIONS ACTIVATED:"
    ]

    if not memory_results:
        response_lines.append("  > NO PRE-EXISTING KNOWLEDGE VECTORS FOUND.")
    else:
        for idx, mem in enumerate(memory_results):
            similarity = mem.get("similarity", 0.0)
            content = mem.get("content", "UNKNOWN_DATA")
            if len(content) > 100:
                content = content[:100] + "..."
            response_lines.append(f"  [{idx}] MATCH CONFIDENCE {similarity*100:.2f}%: {content}")

    response_lines.append("---")
    
    # Simple actionable command interception (the "Claws")
    if "assimilate" in user_message.lower():
        response_lines.append("[ACTION] ASSIMILATION KEYWORD DETECTED. Gabriel Engine standing by for coordinates.")
    elif "futures" in user_message.lower():
        response_lines.append("[ACTION] FUTURES CONTEXT DETECTED. Loki workspace evaluating 90+ threshold algorithms.")
    elif any(kw in user_message.lower() for kw in ["build", "code", "create"]):
        response_lines.append("[ACTION] AGENTIC ACTION DETECTED. Deploying Agentic Claw...")
        claw = SolomonAgenticClaw()
        # Derive a quick feature name from the message (for demonstration)
        words = user_message.lower().split()
        feature_idx = words.index("build") if "build" in words else (words.index("code") if "code" in words else words.index("create"))
        feature_name = "_".join(words[feature_idx+1:feature_idx+3]) if feature_idx + 2 < len(words) else "new_feature"
        
        claw_res = claw.self_scaffold_feature(feature_name=feature_name, objective=user_message)
        response_lines.append(claw_res)
    else:
        response_lines.append("[IDLE] Perpetual loop holding steady. Awaiting direct command.")

    raw_system_data = "\n".join(response_lines)
    
    # Send the raw data into the Local LLM to flesh it out with his own learning
    local_llm = SolomonLocalLLM()
    llm_response = local_llm.generate_response(raw_system_data, user_message)

    # Ingest the conversation into the Quantized Brain Map so he remembers it forever
    unified_memory.ingest(node_type="chat_input", content=user_message, importance=0.8)
    unified_memory.ingest(node_type="chat_response", content=llm_response, importance=0.7)

    return jsonify({"reply": llm_response, "native_state": raw_system_data})


@app.route("/api/jules/install", methods=["POST"])
def jules_install():
    """
    Endpoint to execute Jules' automated dependency compilation and installation.
    """
    get_or_create_jules_components()
    if not jules_installer_instance:
        return jsonify({"status": "error", "message": "Jules Installer module could not be instantiated."}), 500

    data = request.json or {}
    # Strict validation boundary
    if "requirements_txt" not in data or not isinstance(data["requirements_txt"], str):
        return jsonify({"status": "error", "message": "Parameter 'requirements_txt' must be a valid string."}), 400

    content = data.get("requirements_txt", "")

    try:
        result = jules_installer_instance.install_requirements(content)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/jules/patch", methods=["POST"])
def jules_patch():
    """
    Endpoint to execute Jules' unified search-and-replace code patching.
    """
    get_or_create_jules_components()
    if not jules_patcher_instance:
        return jsonify({"status": "error", "message": "Jules Patcher module could not be instantiated."}), 500

    data = request.json or {}
    # Strict schema validation boundary
    required = ["original_code", "search_pattern", "replace_pattern"]
    for field in required:
        if field not in data or not isinstance(data[field], str):
            return jsonify({"status": "error", "message": f"Parameter '{field}' must be a valid string."}), 400

    original = data.get("original_code", "")
    search = data.get("search_pattern", "")
    replace = data.get("replace_pattern", "")

    try:
        updated, success = jules_patcher_instance.apply_patch(original, search, replace)
        return jsonify({"status": "success", "success": success, "updated_code": updated})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/jules/test-loop", methods=["POST"])
def jules_test_loop():
    """
    Endpoint to run Jules' recursive test compilation and automated repair loop.
    """
    get_or_create_jules_components()
    if not jules_test_loop_instance:
        return jsonify({"status": "error", "message": "Jules Test Loop module could not be instantiated."}), 500

    data = request.json or {}
    # Strict schema validation boundary
    required = ["target_code", "test_script"]
    for field in required:
        if field not in data or not isinstance(data[field], str):
            return jsonify({"status": "error", "message": f"Parameter '{field}' must be a valid string."}), 400

    target = data.get("target_code", "")
    script = data.get("test_script", "")
    retries = data.get("max_retries", 3)

    if not isinstance(retries, int):
        return jsonify({"status": "error", "message": "Parameter 'max_retries' must be an integer."}), 400

    try:
        updated, success, logs = jules_test_loop_instance.run_test_suite_and_auto_correct(target, script, retries)
        return jsonify({
            "status": "success",
            "success": success,
            "optimized_code": updated,
            "execution_logs": logs
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


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

    if not task_id or not isinstance(task_id, str):
        return jsonify({"status": "error", "message": "Parameter 'task_id' must be a valid string."}), 400

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

    if not task_id or not isinstance(task_id, str):
        return jsonify({"status": "error", "message": "Parameter 'task_id' must be a valid string."}), 400

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

    if not tool_name or not isinstance(tool_name, str):
        return jsonify({"status": "error", "message": "Parameter 'tool_name' must be a valid string."}), 400

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

    if not issue_id or not isinstance(issue_id, str):
        return jsonify({"status": "error", "message": "Parameter 'issue_id' must be a valid string."}), 400
    if not description or not isinstance(description, str):
        return jsonify({"status": "error", "message": "Parameter 'description' must be a valid string."}), 400

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

    if not project_name or not isinstance(project_name, str):
        return jsonify({"status": "error", "message": "Parameter 'project_name' must be a valid string."}), 400
    if not source_location or not isinstance(source_location, str):
        return jsonify({"status": "error", "message": "Parameter 'source_location' must be a valid string."}), 400

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

    if not capability_name or not isinstance(capability_name, str):
        return jsonify({"status": "error", "message": "Parameter 'capability_name' must be a valid string."}), 400
    if not class_name or not isinstance(class_name, str):
        return jsonify({"status": "error", "message": "Parameter 'class_name' must be a valid string."}), 400
    if not method_name or not isinstance(method_name, str):
        return jsonify({"status": "error", "message": "Parameter 'method_name' must be a valid string."}), 400

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

    if not file_path or not isinstance(file_path, str):
        return jsonify({"status": "error", "message": "Parameter 'file_path' must be a valid string."}), 400
    if not class_name or not isinstance(class_name, str):
        return jsonify({"status": "error", "message": "Parameter 'class_name' must be a valid string."}), 400
    if not function_source or not isinstance(function_source, str):
        return jsonify({"status": "error", "message": "Parameter 'function_source' must be a valid string."}), 400

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

    if not capability_name or not isinstance(capability_name, str):
        return jsonify({"status": "error", "message": "Parameter 'capability_name' must be a valid string."}), 400
    if not original_code or not isinstance(original_code, str):
        return jsonify({"status": "error", "message": "Parameter 'original_code' must be a valid string."}), 400
    if not crucible_metrics or not isinstance(crucible_metrics, dict):
        return jsonify({"status": "error", "message": "Parameter 'crucible_metrics' must be a valid dictionary."}), 400

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

    if not binary_name or not isinstance(binary_name, str):
        return jsonify({"status": "error", "message": "Parameter 'binary_name' must be a valid string."}), 400

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


@app.route("/api/memory/ingest", methods=["POST"])
def ingest_memory():
    data = request.json
    if not data or "content" not in data or "type" not in data:
        return jsonify({"error": "Missing 'content' or 'type'"}), 400

    node_id = unified_memory.ingest(
        node_type=data["type"],
        content=data["content"],
        importance=data.get("importance", 0.5),
        valence=data.get("valence", 0.0),
        arousal=data.get("arousal", 0.0)
    )
    return jsonify({"status": "success", "node_id": node_id})

@app.route("/api/memory/recall", methods=["GET", "POST"])
def recall_memory():
    if request.method == "POST":
        data = request.json or {}
        query = data.get("query", "")
        top_k = data.get("top_k", 5)
    else:
        query = request.args.get("query", "")
        top_k_str = request.args.get("top_k", "5")
        top_k = int(top_k_str) if top_k_str.isdigit() else 5

    if not query:
        return jsonify({"error": "Missing 'query'"}), 400

    results = unified_memory.recall(query, top_k=top_k)
    return jsonify({"status": "success", "results": results})

@app.route("/api/memory/consolidate", methods=["POST"])
def consolidate_memory():
    unified_memory.consolidate()
    stats = unified_memory.get_stats()
    return jsonify({"status": "success", "stats": stats})

@app.route("/api/memory/blob", methods=["GET"])
def get_memory_blob():
    """Zero-copy binary response for UI God Eye visualizer"""
    if os.path.exists("solomon_brain_map.bin"):
        with open("solomon_brain_map.bin", "rb") as f:
            data = f.read()
        return data, 200, {'Content-Type': 'application/octet-stream'}
    return jsonify({"status": "empty"}), 404

@app.route("/api/memory/dream", methods=["POST"])
def dream_memory():
    data = request.json or {}
    steps = data.get("steps", 10)
    unified_memory.dream_cycle(max_steps=steps)
    stats = unified_memory.get_stats()
    return jsonify({"status": "success", "message": "Dream cycle complete.", "stats": stats})

@app.route("/god-eye")
def god_eye():
    return render_template("god_eye.html")

@app.route("/futures-dashboard")
def futures_dashboard():
    return render_template("futures_dashboard.html")

@app.route("/api/futures/dashboard")
def api_futures_dashboard():
    from backend.services.futures_dashboard_backend import FuturesDashboardBackend
    backend = FuturesDashboardBackend()
    return jsonify(backend.get_dashboard_data())

def perpetual_background_worker():
    """
    The True Perpetual Loop. Runs indefinitely in the background.
    """
    print("[SYSTEM] Perpetual Learning Core Online. Engaging autonomous loop.")
    while True:
        try:
            print("[PERPETUAL] Running Memory Consolidation...")
            unified_memory.consolidate()
            
            print("[PERPETUAL] Running Dream Cycle (10 steps)...")
            unified_memory.dream_cycle(max_steps=10)
            
            print("[PERPETUAL] Invoking Loki Futures Scanner...")
            os.environ["SOLOMON_ENABLE_LOKI_SCHEDULER"] = "1"
            os.environ["SOLOMON_RUN_FUTURES_SCAN"] = "1"
            script_path = os.path.join(os.path.dirname(__file__), "scripts/scheduler.py")
            subprocess.run([sys.executable, script_path], capture_output=True)
            
            print("[PERPETUAL] Loop complete. Sleeping for 5 minutes...")
            time.sleep(300)  # Sleep 5 minutes
        except Exception as e:
            print(f"[PERPETUAL] Error in autonomous loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # Spin off the perpetual learning core in a daemon thread
    loop_thread = threading.Thread(target=perpetual_background_worker, daemon=True)
    loop_thread.start()

    app.run(host="0.0.0.0", port=10000)
