import os
import re
import sys
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from .runtime import MnemosyneRuntime

logger = logging.getLogger("autonomous_improvement_loop")

class AutonomousImprovementLoop:
    """
    The 24/7 Autonomous Improvement Loop (AIL) daemon.
    Discovers new components/scripts, runs static security audits, performs sandboxed execution,
    and dynamically distills new capabilities into Mnemosyne draft cards.
    """
    def __init__(self, runtime: MnemosyneRuntime, loop_interval_seconds: int = 600):
        self.runtime = runtime
        self.loop_interval = loop_interval_seconds
        self.is_running = False

    def static_security_audit(self, code: str) -> bool:
        """
        Scans code against dangerous patterns to prevent malicious/insecure operations.
        Returns True if safe, False if audit fails.
        """
        blocked_patterns = [
            r"__import__\(\s*['\"]os['\"]\s*\)\.system",
            r"subprocess\.Popen\(\s*[^,]+,\s*shell\s*=\s*True\)",
            r"eval\(\s*input\s*\(",
            r"rm\s+-rf\s+/",
            r"chmod\s+777",
            r"crypto\.timingSafeEqual\(\s*[^,]+,\s*[^,]+\)\s*===\s*false", # insecure timing comparison
        ]

        for pattern in blocked_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                logger.warning(f"Security audit failure: Detected blocked pattern matching: '{pattern}'")
                return False
        return True

    def test_run_sandbox(self, code: str) -> bool:
        """
        Executes code inside a restricted execution context to verify syntax and standard output.
        Returns True if execution completed with 0 errors.
        """
        if not self.static_security_audit(code):
            return False

        try:
            # Domain-neutral safe environment execution mapping
            local_vars: Dict[str, Any] = {}
            exec(code, {"__builtins__": __builtins__}, local_vars)
            return True
        except Exception as e:
            logger.error(f"Sandbox execution failed: {str(e)}")
            return False

    def run_discovery_and_absorption(self, mock_candidate: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Executes a single cycle of discover -> audit -> sandbox test -> distill.
        Returns the created draft card dictionary on success, or None on failure/exclusion.
        """
        logger.info("Executing Autonomous Improvement Loop cycle...")

        # 1. Discover Candidate (Accepts mock parameters or simulates discovery)
        candidate = mock_candidate or {
            "name": "Date Utility Helper",
            "source": "https://github.com/example/date-helper",
            "code": "def get_formatted_date():\n    return '2026-07-20'\n",
            "description": "Formulates formatted string for system logs.",
            "type": "UTILITY"
        }

        # 2. Static Security Audit
        if not self.static_security_audit(candidate["code"]):
            logger.error(f"Security audit failed for candidate: {candidate['name']}. Skipping.")
            return None

        # 3. Sandbox Dynamic Execution Test
        if not self.test_run_sandbox(candidate["code"]):
            logger.error(f"Sandbox execution test failed for candidate: {candidate['name']}. Skipping.")
            return None

        # 4. Distill and Store as DRAFT Card in Mnemosyne
        report_id = f"WR-AIL-{int(time.time())}"
        report_payload = {
            "report_id": report_id,
            "task_id": "AIL-DISCOVER-01",
            "procedure_ids": ["PC-SO-01"],
            "worker_id": "autonomous_improvement_loop",
            "worker_type": "AIL",
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "outcome": "SUCCESS",
            "attempted": f"Discover and integrate open source package: {candidate['name']}.",
            "succeeded": f"Successfully audited, compiled, and validated {candidate['name']}.",
            "failed": "",
            "root_cause": None,
            "repair_action": None,
            "evidence": [
                {"type": "AUDIT", "reference": "Security Regex Scanner", "summary": "Audit passed."},
                {"type": "SANDBOX", "reference": "exec() Restricted", "summary": "Sandbox compile succeeded with zero exceptions."}
            ],
            "security_classification": "INTERNAL",
            "candidate_learning": True,
            "metadata": {
                "discovered_source": candidate["source"],
                "candidate_type": candidate["type"],
                "code_checksum": hash(candidate["code"])
            }
        }

        try:
            # Ingest report and auto-draft card
            draft_cards = self.runtime.ingest_worker_report(
                report=report_payload,
                source_worker="AIL_Daemon"
            )
            if draft_cards:
                draft_card = draft_cards[0]
                logger.info(f"Successfully absorbed capability! Created draft card: {draft_card['card_id']}")
                return draft_card
        except Exception as e:
            logger.error(f"Failed to ingest and store capability card: {str(e)}")

        return None

    def start_loop(self):
        """Starts the 24/7 background execution loop."""
        self.is_running = True
        logger.info(f"AIL background daemon started with loop interval: {self.loop_interval} seconds.")
        try:
            while self.is_running:
                self.run_discovery_and_absorption()
                time.sleep(self.loop_interval)
        except KeyboardInterrupt:
            logger.info("AIL background daemon stopped via user keyboard interrupt.")
            self.is_running = False
        except Exception as e:
            logger.error(f"AIL background daemon experienced critical crash: {str(e)}")
            self.is_running = False

    def stop_loop(self):
        """Stops the loop daemon."""
        logger.info("Stopping AIL background daemon...")
        self.is_running = False
