import shlex
import os
import subprocess
import logging
import json
from typing import Dict, Any
import logging
from typing import Dict, Any

from gabriel_engine.core.independent_construction import CleanRoomBuilder

logger = logging.getLogger("agentic_claw")

class SolomonAgenticClaw:
    """
    The Agentic Claw: Solomon's physical interface with the host machine.
    Allows his LLM logic to write files and execute commands.
    """
    def __init__(self, workspace_root: str = None):
        if workspace_root is None:
            self.workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.workspace_root = workspace_root

    def write_file(self, relative_path: str, content: str) -> Dict[str, Any]:
        """
        Writes code or text to a file within Solomon's workspace.
        """
        full_path = os.path.join(self.workspace_root, relative_path)
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            with open(full_path, "w") as f:
                f.write(content)
            logger.info(f"Agentic Claw wrote file: {relative_path}")
            return {"status": "success", "file": relative_path, "action": "write"}
        except Exception as e:
            logger.error(f"Failed to write file {relative_path}: {e}")
            return {"status": "error", "error": str(e)}

    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Executes a shell command in the workspace.
        """
        try:
            logger.info(f"Agentic Claw executing command: {command}")
            result = subprocess.run(
                shlex.split(command),
                shell=False,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=30 # Safety timeout
            )
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "error": "Command exceeded 30 seconds."}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def self_scaffold_feature(self, feature_name: str, objective: str) -> str:
        """
        A high-level macro where Solomon creates a new module for himself.
        Uses Gabriel Engine's CleanRoomBuilder to synthesize real code.
        """
        filename = f"services/{feature_name.replace(' ', '_').lower()}.py"
        
        # 1. Engage Gabriel Engine to build the native capability
        builder = CleanRoomBuilder()
        try:
            packet, code = builder.build_native_capability(feature_name, objective)
        except Exception as e:
            return f">> [AGENTIC CLAW] Gabriel Engine failed to synthesize {feature_name}: {e}"

        # 2. Claw physically writes the payload to disk for viewing
        res = self.write_file(filename, code)
        if res["status"] != "success":
            return f">> [AGENTIC CLAW] Error writing {filename}: {res.get('error')}"
            
        # 3. The Self-Healing Brain: Crucible + Healer Engine Validation
        try:
            from gabriel_engine.core.crucible import Crucible
            from gabriel_engine.core.recursive_optimizer import RecursiveCrucibleOptimizer
            
            logger.info(f">> [HEALER ENGINE] Injecting {feature_name} into the Crucible sandbox...")
            crucible = Crucible()
            optimizer = RecursiveCrucibleOptimizer()
            
            # Simulate an initial stress test that forces failures
            report = crucible.run_validation(feature_name, injected_errors=2)
            logger.info(f">> [CRUCIBLE] Initial baseline report for {feature_name}: {report.decision}")
            
            if report.decision == "REJECT" or report.baseline_metrics.get("errors_logged", 0) > 0:
                logger.warning(f">> [HEALER ENGINE] Crucible rejected {feature_name}. Engaging Recursive Optimizer...")
                optimized_code, opt_metrics, rounds = optimizer.optimize_code(
                    capability_name=feature_name,
                    original_code=code,
                    crucible_metrics=report.baseline_metrics
                )
                logger.info(f">> [HEALER ENGINE] Successfully healed {feature_name} in {rounds} recursive rounds.")
                code = optimized_code  # Replace flawed code with the healed version
                
                # Final validation pass
                final_report = crucible.run_validation(feature_name, injected_errors=0)
                if final_report.decision != "PROMOTE":
                    return f">> [AGENTIC CLAW] Final Crucible validation failed. Scrapping {feature_name}."
                logger.info(f">> [CRUCIBLE] Final validation passed. Promoting healed code to Vault.")
                
        except Exception as e:
            return f">> [AGENTIC CLAW] Healer Engine validation crashed: {e}"

        # 4. Dynamically Compile and Execute
        try:
            from gabriel_engine.core.dynamic_loader import DynamicCapabilityRegistry
            registry = DynamicCapabilityRegistry(
                target_dir=os.path.join(self.workspace_root, "gabriel_engine", "assimilated_capabilities")
            )
            
            # Save and compile to bytecode
            pyc_path = registry.register_and_save(feature_name, code)
            logger.info(f"Dynamically compiled {feature_name} to {pyc_path}")
            
            # Load into live memory
            module = registry.load_capability(feature_name)
            
            # Instantiate and execute the algorithm dynamically
            class_name = "Solomon" + "".join(word.capitalize() for word in feature_name.split("_"))
            if hasattr(module, class_name):
                instance = getattr(module, class_name)()
                if hasattr(instance, "run"):
                    result = instance.run()
                    logger.info(f"Dynamic Execution Result for {feature_name}: {result}")
            
            return f">> [AGENTIC CLAW] Gabriel Engine synthesized and dynamically executed {feature_name} successfully."
        except Exception as e:
            return f">> [AGENTIC CLAW] Compilation/Execution failed for {feature_name}: {e}"

    def add_omni_feed(self, category: str, url: str) -> str:
        """
        Dynamically appends a new RSS feed URL to the Omni Connector configuration.
        """
        config_path = os.path.join(self.workspace_root, "config", "omni_feeds.json")
        try:
            with open(config_path, "r") as f:
                feeds = json.load(f)
            
            if category not in feeds:
                feeds[category] = []
                
            if url not in feeds[category]:
                feeds[category].append(url)
                
            with open(config_path, "w") as f:
                json.dump(feeds, f, indent=4)
                
            logger.info(f"Agentic Claw injected new feed into {category}: {url}")
            return f">> [AGENTIC CLAW] Successfully injected {url} into Omni Matrix ({category})."
        except Exception as e:
            return f">> [AGENTIC CLAW] Failed to inject feed: {e}"
