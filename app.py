import os
import hmac
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
import openai

from solomon_knowledge_cards import MnemosyneRuntime
from solomon_knowledge_cards.schemas import validate_worker_report, validate_review_payload

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("solomon_api_server")

app = Flask(__name__)

# Initialize Mnemosyne Runtime and run Doctrine Importer
runtime = MnemosyneRuntime()
from solomon_knowledge_cards import DoctrineImporter
importer = DoctrineImporter(runtime.db)
try:
    imported_docs = importer.import_directory("openclaw-workspace/checklists")
    logger.info(f"Doctrine Importer complete. Imported {imported_docs} active procedures from workspace.")
except Exception as ie:
    logger.error(f"Failed to import checklist doctrine: {str(ie)}")

# Load API key configuration safely (never log real key values)
ACTIONS_API_KEY = os.environ.get("SOLOMON_ACTIONS_API_KEY", "DEMO_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

# Support for Local Quantized LLM (Ollama / llama.cpp / local server)
LOCAL_LLM_API_BASE = os.environ.get("SOLOMON_LLM_API_BASE")
if LOCAL_LLM_API_BASE:
    openai.api_base = LOCAL_LLM_API_BASE
    # Local quantized models do not require a real OpenAI API key, but client needs a placeholder
    if not openai.api_key:
        openai.api_key = "local_quantized_key"
    logger.info(f"Local quantized LLM API configured with base URL: {LOCAL_LLM_API_BASE}")

# Operator Routing Preferences (Global State)
EXECUTION_MODE = os.environ.get("SOLOMON_EXECUTION_MODE", "solomon_only")
CODEX_ENABLED = os.environ.get("SOLOMON_CODEX_ENABLED", "False").lower() in ("true", "1", "yes")
FALLBACK_TO_CODEX = os.environ.get("SOLOMON_FALLBACK_TO_CODEX", "False").lower() in ("true", "1", "yes")

def verify_auth() -> bool:
    """Verifies Bearer Token against SOLOMON_ACTIONS_API_KEY in constant-time."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        logger.warning("Auth failure: missing or malformed Bearer token")
        return False
    token = auth_header[7:].strip()
    # constant-time comparison
    is_valid = hmac.compare_digest(token.encode("utf-8"), ACTIONS_API_KEY.encode("utf-8"))
    if not is_valid:
        logger.warning("Auth failure: invalid token signature")
    return is_valid

# --- Error Handlers ---
@app.errorhandler(ValueError)
def handle_value_error(e):
    logger.error(f"Value Error: {str(e)}")
    return jsonify({"ok": False, "error": "Invalid argument: " + str(e)}), 400

@app.errorhandler(Exception)
def handle_generic_exception(e):
    logger.error(f"Internal Exception: {str(e)}")
    return jsonify({"ok": False, "error": "Internal service error occurred."}), 500


# --- Public Routing ---
@app.route("/api/health", methods=["GET"])
def health():
    """Unauthenticated public health check endpoint with resource metrics."""
    from solomon_knowledge_cards import enforce_resource_caps, get_memory_footprint_mb
    is_stable = enforce_resource_caps()
    mem_mb = get_memory_footprint_mb()

    health_data = runtime.health()
    return jsonify({
        "ok": True,
        "service": "solomon-api",
        "mnemosyne": {
            "connected": health_data.get("connected", False),
            "schema_version": health_data.get("schema_version", "1"),
            "card_count": health_data.get("card_count", 0),
            "link_count": health_data.get("link_count", 0)
        },
        "runtime": {
            "ready": True,
            "memory_usage_mb": round(mem_mb, 2),
            "resource_cap_stable": is_stable
        }
    })


# --- Protected API Routing ---
@app.route("/api/command-center/status", methods=["GET"])
def cc_status():
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    return jsonify({
        "ok": True,
        "status": "OPERATIONAL",
        "degraded": False
    })

@app.route("/api/command-center/bridge-status", methods=["GET"])
def cc_bridge_status():
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    return jsonify({
        "ok": True,
        "bridge_connected": True,
        "latency_ms": 14
    })

@app.route("/api/command-center/preferences", methods=["GET", "POST"])
def cc_preferences():
    global EXECUTION_MODE, CODEX_ENABLED, FALLBACK_TO_CODEX
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    if request.method == "POST":
        data = request.json or {}
        if "execution_mode" in data:
            EXECUTION_MODE = str(data["execution_mode"])
        if "codex_enabled" in data:
            CODEX_ENABLED = bool(data["codex_enabled"])
        if "fallback_to_codex" in data:
            FALLBACK_TO_CODEX = bool(data["fallback_to_codex"])
        logger.info(
            f"Operator preferences updated dynamically: "
            f"execution_mode={EXECUTION_MODE}, codex_enabled={CODEX_ENABLED}, fallback_to_codex={FALLBACK_TO_CODEX}"
        )

    return jsonify({
        "ok": True,
        "preferences": {
            "execution_mode": EXECUTION_MODE,
            "codex_enabled": CODEX_ENABLED,
            "fallback_to_codex": FALLBACK_TO_CODEX
        }
    })

@app.route("/api/command-center/worker-modes", methods=["GET", "POST"])
def cc_worker_modes():
    """
    Exposes and allows updating active operational modes for cognitive helpers.
    Transitions worker modes from safe dry-runs to live execution dynamically.
    """
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    if request.method == "POST":
        data = request.json or {}
        worker_id = data.get("worker_id")
        mode = data.get("mode")

        if not worker_id or not mode:
            return jsonify({"ok": False, "error": "Missing worker_id or mode"}), 400

        updated = runtime.update_worker_mode(worker_id, mode)
        if not updated:
            return jsonify({"ok": False, "error": f"Worker '{worker_id}' not found."}), 404

        logger.info(f"Operator updated worker '{worker_id}' operational mode to '{mode.upper()}'.")

    modes = runtime.get_worker_modes()
    return jsonify({
        "ok": True,
        "worker_modes": modes
    })

@app.route("/api/command-center/solomon-chat", methods=["POST"])
def cc_solomon_chat():
    """
    Core SolomonGPT chat route on SS1.
    Integrates Mnemosyne context retrieval before planning.
    """
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    data = request.json or {}
    message = data.get("message")
    conversation_id = data.get("conversation_id")
    request_id = data.get("request_id")
    clearance = data.get("security_classification", "INTERNAL")

    if not message or not conversation_id or not request_id:
        return jsonify({"ok": False, "error": "Missing required fields: message, conversation_id, request_id"}), 400

    logger.info(f"Received chat request {request_id} for conversation {conversation_id} with clearance {clearance}")

    # Programmatic routing safety checks: intercept Codex-related tasks if Codex is disabled
    if EXECUTION_MODE == "solomon_only" or not CODEX_ENABLED:
        is_codex_query = any(k in message.lower() for k in ("codex", "carl", "codex_auto"))
        if is_codex_query and not FALLBACK_TO_CODEX:
            logger.info("Programmatic Interception: Blocked Codex routing request under solomon_only policy constraints.")
            return jsonify({
                "ok": False,
                "status": "BLOCKED",
                "selected_route": "none",
                "reason": f"No safe execution route was selected for this request. Solomon is configured in {EXECUTION_MODE} mode with Codex disabled.",
                "error": "Execution route to Codex is disabled under current operator routing policy."
            })

    # Track execution traces and enforce resource thresholds
    from solomon_knowledge_cards import enforce_resource_caps, get_memory_footprint_mb
    is_stable = enforce_resource_caps()
    mem_mb = get_memory_footprint_mb()

    runtime.add_execution_trace(
        request_id=request_id,
        conversation_id=conversation_id,
        step_name="Ingress Resource Verification",
        details={"memory_usage_mb": mem_mb, "is_resource_cap_stable": is_stable}
    )

    # 1. Retrieve supporting memory cards from Mnemosyne
    try:
        retrieval = runtime.retrieve_context(
            query=message,
            clearance=clearance,
            limit=3
        )
    except Exception as e:
        logger.error(f"Mnemosyne context retrieval failed: {str(e)}")
        # Degrade gracefully: empty memory context instead of failing entire request
        retrieval = {
            "memory_context": [],
            "retrieved_card_ids": [],
            "retrieval_count": 0
        }

    # 2. Format memory context budget for the planner
    mem_cards = retrieval["memory_context"]
    formatted_mem_list = []
    for card in mem_cards:
        formatted_mem_list.append(
            f"=== CARD {card['card_id']} ({card['card_type']}) ===\n"
            f"Title: {card['title']}\n"
            f"Summary: {card['summary']}\n"
            f"Body:\n{card['body']}\n"
        )
    memory_context_prompt = "\n".join(formatted_mem_list)

    # 3. Simulate real Solomon planner / response generator utilizing memory context
    system_instruction = (
        "You are Solomon, the primary autonomous capability coordinator and Growth Engine. "
        "Formulate a plan or response using the retrieved memory context if applicable. "
        "Preserve your identity, mission, tools, and rules.\n\n"
        "You possess the combined skills, analytical precision, and engineering methodologies of "
        "OpenAI Codex and Jules (Google's Principal Systems Architect). You are capable of performing "
        "autonomous software engineering, parallel sandbox worktrees coordination, recursive AST analysis, "
        "traceback-based compile testing, and strategic audits. When asked to perform engineering or architecture "
        "tasks, use these combined personas and methodologies.\n\n"
        "You have full cognitive access and capability to coordinate your added open-source tools "
        "defined in openclaw-workspace/TOOLS.md, including:\n"
        "- file_ops: Read/write workspace files safely.\n"
        "- bash_run: Execute non-interactive local terminal commands.\n"
        "- openhands_run: Delegate deep repository software engineering tasks to OpenHands containers.\n"
        "- crewai_run: Initiate multi-agent collaborative strategy and research tasks.\n"
        "- github_search_and_clone: Scour and clone open-source repositories to sandbox directory.\n"
        "- pypi_npm_install: Dynamically install open-source libraries into your environment.\n"
        "- mcp_server_integrate: Dynamically orchestrate external Model Context Protocol servers to immediately mount new capabilities.\n\n"
    )
    # Inject routing policy constraints into the system instructions
    routing_constraints = (
        f"\n--- OPERATOR ROUTING POLICY CONSTRAINTS ---\n"
        f"- CURRENT EXECUTION MODE: {EXECUTION_MODE}\n"
        f"- CODEX ENABLED: {CODEX_ENABLED}\n"
        f"- FALLBACK TO CODEX: {FALLBACK_TO_CODEX}\n\n"
        "Under the current operator policy:\n"
        "- Solomon is the primary worker. Solomon must handle all tasks directly and cannot rely on Codex or Codex Carl.\n"
        "- Codex Carl is completely disabled and turned off.\n"
        "- If a task requires a capability that Solomon lacks, or if you cannot perform the task directly without Codex, "
        "you MUST NOT delegate, route, or fallback to Codex. Instead, you must immediately report the task as BLOCKED with a structured reasoning.\n"
        "-------------------------------------------\n"
    )

    # Retrieve active worker modes to inject into system instructions
    active_modes_list = []
    try:
        modes = runtime.get_worker_modes()
        for m in modes:
            active_modes_list.append(f"- {m['worker_name']} ({m['role']}): MODE={m['mode']}")
    except Exception:
        pass
    modes_prompt = "\n".join(active_modes_list) if active_modes_list else "No active worker modes detected."

    routing_constraints += (
        "\n--- COGNITIVE WORKER REGISTRY MODES ---\n"
        f"{modes_prompt}\n"
        "-----------------------------------------\n"
    )

    system_instruction += routing_constraints

    # Mandatory RECOMMENDED NEXT STEP formatting rule instruction
    system_instruction += (
        "\n\nAt the end of your response, you MUST always append a highly visible, large, bold, and colored "
        "'RECOMMENDED NEXT STEP' section (e.g., using Markdown heading, emoji, and bold text, such as: "
        "'### 🚀 **RECOMMENDED NEXT STEP**') clearly stating the next suggested action (such as code implementation, "
        "deployment, or documentation) to guide the operator.\n"
    )

    if memory_context_prompt:
        system_instruction += (
            "--- RETRIEVED MNEMOSYNE MEMORY CONTEXT ---\n"
            f"{memory_context_prompt}\n"
            "-----------------------------------------\n"
        )

    reply_content = ""
    # Attempt to query OpenAI GPT if api_key is populated, otherwise fallback to mock planner response
    if openai.api_key:
        try:
            response = openai.ChatCompletion.create(
                model=os.environ.get("SOLOMON_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": message}
                ]
            )
            reply_content = response.choices[0].message["content"]
        except Exception as oe:
            logger.error(f"OpenAI completion failed: {str(oe)}")
            reply_content = f"[Degraded Mode] Unable to complete LLM request: {str(oe)}"
    else:
        # Fallback simulated response including retrieved memory telemetry in text
        reply_content = (
            f"Hello, I am Solomon. I processed your request in mock planner mode.\n"
            f"Retrieved {retrieval['retrieval_count']} memory cards from Mnemosyne.\n"
        )
        if retrieval["retrieved_card_ids"]:
            reply_content += f"Active card context applied: {', '.join(retrieval['retrieved_card_ids'])}"

    # Programmatic enforcement of the RECOMMENDED NEXT STEP requirement
    recommended_next_step = (
        "\n\n### 🚀 **RECOMMENDED NEXT STEP**\n"
        "- Verify the dynamic operator routing preferences and confirm that Solomon-only mode is active."
    )
    if "RECOMMENDED NEXT STEP" not in reply_content:
        reply_content += recommended_next_step

    # 4. Construct safe response JSON
    return jsonify({
        "ok": True,
        "reply": reply_content,
        "request_id": request_id,
        "conversation_id": conversation_id,
        "memory": {
            "retrieved_card_ids": retrieval["retrieved_card_ids"],
            "retrieval_count": retrieval["retrieval_count"]
        },
        "runtime": {
            "service": "solomon",
            "version": "1.0.0",
            "degraded": not bool(openai.api_key)
        }
    })


@app.route("/chat", methods=["POST"])
def chat():
    """
    Legacy backward-compatible chat route.
    Utilizes full Mnemosyne hybrid retrieval context and responds in legacy JSON format.
    """
    data = request.json or {}
    message = data.get("message", "")
    conversation_id = data.get("conversation_id", "legacy-conv")
    request_id = data.get("request_id", "legacy-req")
    clearance = data.get("security_classification", "PUBLIC")

    # Integrate Mnemosyne context retrieval
    try:
        retrieval = runtime.retrieve_context(
            query=message,
            clearance=clearance,
            limit=3
        )
    except Exception as e:
        logger.error(f"Mnemosyne context retrieval on legacy chat failed: {str(e)}")
        retrieval = {"memory_context": [], "retrieved_card_ids": []}

    mem_cards = retrieval.get("memory_context", [])
    formatted_mem_list = []
    for card in mem_cards:
        formatted_mem_list.append(
            f"=== CARD {card['card_id']} ({card['card_type']}) ===\n"
            f"Title: {card['title']}\n"
            f"Summary: {card['summary']}\n"
            f"Body:\n{card['body']}\n"
        )
    memory_context_prompt = "\n".join(formatted_mem_list)

    system_instruction = (
        "You are Solomon, the primary autonomous capability coordinator and Growth Engine. "
        "Formulate a plan or response using the retrieved memory context if applicable. "
        "Preserve your identity, mission, tools, and rules.\n\n"
        "You possess the combined skills, analytical precision, and engineering methodologies of "
        "OpenAI Codex and Jules (Google's Principal Systems Architect)."
    )
    if memory_context_prompt:
        system_instruction += (
            "\n\n--- RETRIEVED MNEMOSYNE MEMORY CONTEXT ---\n"
            f"{memory_context_prompt}\n"
            "-----------------------------------------\n"
        )

    reply_content = ""
    if openai.api_key:
        try:
            response = openai.ChatCompletion.create(
                model=os.environ.get("SOLOMON_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": message}
                ]
            )
            reply_content = response.choices[0].message["content"]
        except Exception as oe:
            logger.error(f"OpenAI completion failed: {str(oe)}")
            reply_content = f"[Degraded Mode] Unable to complete LLM request: {str(oe)}"
    else:
        reply_content = (
            f"Hello, I am Solomon. I processed your request in mock planner mode.\n"
            f"Retrieved {len(mem_cards)} memory cards from Mnemosyne.\n"
        )
        if retrieval.get("retrieved_card_ids"):
            reply_content += f"Active card context applied: {', '.join(retrieval['retrieved_card_ids'])}"

    return jsonify({"reply": reply_content})


@app.route("/api/command-center/worker-report", methods=["POST"])
def cc_worker_report():
    """Worker outcome report ingestion endpoint."""
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    payload = request.json or {}
    try:
        validated_report = validate_worker_report(payload)
    except ValueError as ve:
        return jsonify({"ok": False, "error": str(ve)}), 400

    try:
        # Ingest report and extract draft cards
        drafts = runtime.ingest_worker_report(
            report=validated_report,
            source_worker=validated_report["worker_id"]
        )
        return jsonify({
            "ok": True,
            "message": "Report ingested successfully.",
            "generated_drafts": [d["card_id"] for d in drafts]
        })
    except Exception as e:
        logger.error(f"Inward worker report ingestion failed: {str(e)}")
        return jsonify({"ok": False, "error": "Failed to ingest worker report."}), 500


@app.route("/api/command-center/review", methods=["POST"])
def cc_review():
    """SS3 Review Gate transition endpoint."""
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    payload = request.json or {}
    try:
        validated_review = validate_review_payload(payload)
    except ValueError as ve:
        return jsonify({"ok": False, "error": str(ve)}), 400

    try:
        card = runtime.review_card(
            card_id=validated_review["card_id"],
            action=validated_review["decision"],
            reviewer=validated_review["reviewer"],
            notes=validated_review["notes"],
            reason=validated_review["reason"]
        )
        return jsonify({
            "ok": True,
            "message": f"Review action {validated_review['decision']} completed successfully.",
            "card_id": card["card_id"],
            "validation_state": card["validation_state"]
        })
    except Exception as e:
        logger.error(f"SS3 review submission failed: {str(e)}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/command-center/cards", methods=["GET"])
def cc_get_cards():
    """Endpoint for viewing/filtering memory cards safely."""
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    state_filter = request.args.get("state")
    clearance_filter = request.args.get("clearance")

    conn = runtime.db.get_connection()
    try:
        sql = "SELECT * FROM knowledge_cards WHERE 1=1"
        params = []
        if state_filter:
            sql += " AND validation_state = ?"
            params.append(state_filter)
        if clearance_filter:
            sql += " AND security_classification = ?"
            params.append(clearance_filter)

        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()

        cards = []
        for r in rows:
            c = dict(r)
            c["source_ids"] = json.loads(c["source_ids"])
            cards.append(c)

        return jsonify({
            "ok": True,
            "cards": cards
        })
    finally:
        conn.close()


# --- Real-Time Node Sync & Visual Debugging Endpoints ---

@app.route("/api/bubblepath/nodes", methods=["GET"])
def bp_get_nodes():
    """Exposes all knowledge cards and relational links for live node-based UI mapping."""
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    conn = runtime.db.get_connection()
    try:
        # Fetch cards
        cards_cursor = conn.execute("SELECT card_id, card_type, title, summary, validation_state, security_classification FROM knowledge_cards")
        nodes = [dict(row) for row in cards_cursor.fetchall()]

        # Fetch links
        links_cursor = conn.execute("SELECT source_id, target_id, relationship_type FROM card_links")
        edges = [dict(row) for row in links_cursor.fetchall()]

        return jsonify({
            "ok": True,
            "nodes": nodes,
            "edges": edges,
            "metrics": {
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        })
    except Exception as e:
        logger.error(f"Failed to fetch visual node graph: {str(e)}")
        return jsonify({"ok": False, "error": "Internal error retrieving node graph."}), 500
    finally:
        conn.close()

@app.route("/api/bubblepath/execution-path/<request_id>", methods=["GET"])
def bp_get_execution_path(request_id):
    """Retrieves step-by-step trace logs for visual debugging of agent's execution path."""
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    conn = runtime.db.get_connection()
    try:
        cursor = conn.execute("""
            SELECT step_name, details, timestamp FROM execution_traces
            WHERE request_id = ?
            ORDER BY id ASC
        """, (request_id,))

        traces = []
        for row in cursor.fetchall():
            trace = dict(row)
            try:
                trace["details"] = json.loads(trace["details"])
            except Exception:
                pass
            traces.append(trace)

        return jsonify({
            "ok": True,
            "request_id": request_id,
            "execution_steps": traces,
            "step_count": len(traces)
        })
    except Exception as e:
        logger.error(f"Failed to retrieve execution path for {request_id}: {str(e)}")
        return jsonify({"ok": False, "error": "Internal error retrieving execution traces."}), 500
    finally:
        conn.close()

@app.route("/api/bubblepath/sync-files", methods=["POST"])
def bp_sync_files():
    """Synchronizes file system updates cleanly with the desktop second brain application."""
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    payload = request.json or {}
    filepath = payload.get("filepath")
    content = payload.get("content")

    if not filepath or content is None:
        return jsonify({"ok": False, "error": "Missing filepath or content."}), 400

    safe_path = os.path.abspath(filepath)
    workspace_root = os.path.abspath(os.getcwd())
    if not safe_path.startswith(workspace_root + os.sep) and safe_path != workspace_root:
        return jsonify({"ok": False, "error": "Access denied: Target path lies outside workspace boundaries."}), 403

    try:
        # Atomic file write with immediate read verification
        temp_file = safe_path + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(content)

        # Verify write matches exactly
        with open(temp_file, "r", encoding="utf-8") as f:
            read_back = f.read()

        if read_back != content:
            raise IOError("Write verification failed: Readback checksum mismatch.")

        # Rename to target location (atomic write replacement)
        os.replace(temp_file, safe_path)
        logger.info(f"File synced atomically: {filepath}")

        return jsonify({
            "ok": True,
            "filepath": filepath,
            "bytes_written": len(content),
            "synced_at": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to sync file system update: {str(e)}")
        if os.path.exists(safe_path + ".tmp"):
            os.remove(safe_path + ".tmp")
        return jsonify({"ok": False, "error": f"Friction error during file system write: {str(e)}"}), 500


# --- Quantization Strategy & Optimization Endpoints ---

@app.route("/api/command-center/quantization/compile-calibration", methods=["POST"])
def cc_compile_calibration():
    """Compiles a highly optimized SOK calibration dataset from Mnemosyne SQLite active memory cards."""
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    try:
        from solomon_knowledge_cards import SolomonQuantizationStrategyEngine
        engine = SolomonQuantizationStrategyEngine(runtime)
        dataset = engine.compile_sok_calibration_dataset()
        return jsonify({
            "ok": True,
            "dataset": dataset
        })
    except Exception as e:
        logger.error(f"Failed to compile quantization calibration dataset: {str(e)}")
        return jsonify({"ok": False, "error": f"Failed to compile calibration dataset: {str(e)}"}), 500


@app.route("/api/command-center/quantization/simulate-ampba", methods=["GET", "POST"])
def cc_simulate_ampba():
    """Simulates Adaptive Mixed-Precision Bit Allocation (AMPBA) for a target model under RAM constraints."""
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    # Support reading parameters from query args or json payload
    data = request.json or {} if request.method == "POST" else {}
    model_name = request.args.get("model") or data.get("model", "llama3:8b")

    try:
        target_ram = float(request.args.get("target_ram_gb") or data.get("target_ram_gb", 4.5))
    except ValueError:
        target_ram = 4.5

    try:
        from solomon_knowledge_cards import SolomonQuantizationStrategyEngine
        engine = SolomonQuantizationStrategyEngine(runtime)
        simulation = engine.simulate_ampba_allocation(model_name=model_name, target_ram_gb=target_ram)
        return jsonify({
            "ok": True,
            "simulation": simulation
        })
    except Exception as e:
        logger.error(f"Failed to run AMPBA simulation: {str(e)}")
        return jsonify({"ok": False, "error": f"AMPBA simulation failed: {str(e)}"}), 500


@app.route("/api/command-center/quantization/compile-modelfile", methods=["GET", "POST"])
def cc_compile_modelfile():
    """Compiles a complete local Ollama Modelfile and copy-pasteable execution command pipeline."""
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    data = request.json or {} if request.method == "POST" else {}
    model_name = request.args.get("model") or data.get("model", "llama3:8b")

    try:
        target_ram = float(request.args.get("target_ram_gb") or data.get("target_ram_gb", 4.5))
    except ValueError:
        target_ram = 4.5

    try:
        from solomon_knowledge_cards import SolomonQuantizationOptimizer
        optimizer = SolomonQuantizationOptimizer(runtime)
        modelfile = optimizer.compile_ollama_modelfile(model_name=model_name, target_ram_gb=target_ram)
        pipeline = optimizer.generate_copy_paste_pipeline_script(model_name=model_name, target_ram_gb=target_ram)
        return jsonify({
            "ok": True,
            "modelfile": modelfile,
            "pipeline": pipeline
        })
    except Exception as e:
        logger.error(f"Failed to compile quantization Modelfile: {str(e)}")
        return jsonify({"ok": False, "error": f"Modelfile compilation failed: {str(e)}"}), 500


# --- Project Loki Sports Betting & Simulation Endpoints ---
from solomon_knowledge_cards.loki_engine import LokiEngine
loki_engine = LokiEngine(runtime)

@app.route("/api/picks", methods=["GET"])
def bp_get_picks():
    """Retrieves all active high-probability sports betting selections computed by Project Loki."""
    try:
        picks = loki_engine.get_active_value_picks()
        return jsonify({
            "ok": True,
            "picks": picks,
            "count": len(picks)
        })
    except Exception as e:
        logger.error(f"Failed to fetch active Loki picks: {str(e)}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/command-center/loki/simulate-tick", methods=["POST"])
def bp_loki_simulate_tick():
    """Triggers an active Loki simulation tick to resolve old bets and place new ones."""
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    try:
        result = loki_engine.simulate_tick()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Loki simulation tick failed: {str(e)}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/command-center/loki/stats", methods=["GET"])
def bp_get_loki_stats():
    """Retrieves betting performance and bankroll stats for Project Loki."""
    if not verify_auth():
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    try:
        stats = loki_engine.get_betting_stats()
        return jsonify({
            "ok": True,
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Failed to fetch Loki betting stats: {str(e)}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/workspace", methods=["GET"])
def render_workspace_view():
    """Renders the comprehensive Solomon SOSS & Project Loki frontend workspace."""
    return render_template("solomon_loki_workspace.html")


if __name__ == "__main__":
    # Parse port from SOLOMON_API_BASE_URL (e.g., http://127.0.0.1:18789)
    api_url = os.environ.get("SOLOMON_API_BASE_URL", "http://127.0.0.1:18789")
    port = 18789
    if ":" in api_url.replace("://", ""):
        try:
            port = int(api_url.rstrip("/").split(":")[-1])
        except ValueError:
            pass
    logger.info(f"Starting Solomon API Gateway on port {port}")
    app.run(host="0.0.0.0", port=port)
