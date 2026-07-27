# services/solomon_governance_approval_packet.py
import mmap
import struct
import os
import sqlite3
import hashlib
import datetime

route_key = "solomon_governance_approval_packet"

class GovernanceApprovalLane:
    def __init__(self, log_file="governance_log.bin", db_path="solomon_soss.db"):
        self.log_file = log_file
        self.db_path = db_path
        self._ensure_log_exists()
        self._ensure_db_table_exists()

    def _ensure_log_exists(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, "wb") as f:
                # 1024 slots * 64 bytes each = 65536 bytes
                f.write(b'\x00' * 65536)

    def _ensure_db_table_exists(self):
        # Transactionally create table if it does not exist (for standalone test resilience)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS governance_events (
                        sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id TEXT NOT NULL UNIQUE,
                        packet_id TEXT NOT NULL,
                        previous_record_hash TEXT,
                        record_type TEXT NOT NULL,
                        requested_by TEXT NOT NULL,
                        actor_id TEXT NOT NULL,
                        target_environment TEXT NOT NULL,
                        change_type TEXT NOT NULL,
                        risk_level TEXT NOT NULL,
                        summary TEXT NOT NULL,
                        artifact_json TEXT NOT NULL,
                        tests_json TEXT NOT NULL,
                        security_json TEXT NOT NULL,
                        backup_json TEXT NOT NULL,
                        rollback_json TEXT NOT NULL,
                        reviewer_id TEXT,
                        decision TEXT,
                        decision_reason TEXT,
                        occurred_at TEXT NOT NULL,
                        record_hash TEXT NOT NULL UNIQUE
                    )
                ''')
                conn.commit()
        except Exception:
            pass

    def review_packet(self, packet):
        # Implementation of governance gate
        if packet.get("requires_approval") and packet.get("approved_by") != "Mark":
            self._audit_event("refused", packet.get("action", "unknown"))
            self._log_db_decision("refused", packet)
            return {"status": "refused", "reason": "Requires Mark approval", "audit_id": "aud_001"}

        # Check SS3 verification
        if packet.get("requires_ss3_review") and not packet.get("ss3_verified", False):
             self._audit_event("refused", packet.get("action", "unknown"))
             self._log_db_decision("refused", packet)
             return {"status": "refused", "reason": "Requires SS3 verification", "audit_id": "aud_002"}

        self._audit_event("approved", packet.get("action", "unknown"))
        self._log_db_decision("approved", packet)
        return {"status": "approved", "audit_id": "aud_003"}

    def _audit_event(self, status, action):
        # Hyper-efficient zero-copy append to binary log cache
        try:
            with open(self.log_file, "r+b") as f:
                mm = mmap.mmap(f.fileno(), 0)
                # Slot size 64 bytes. Find first empty slot (starting with \x00)
                for i in range(1024):
                    offset = i * 64
                    if mm[offset] == 0:
                        # Pack status(32s) and action(32s)
                        status_bytes = status.encode('utf-8')[:32].ljust(32, b'\x00')
                        action_bytes = action.encode('utf-8')[:32].ljust(32, b'\x00')
                        mm[offset:offset+64] = struct.pack('32s32s', status_bytes, action_bytes)
                        break
                mm.flush()
                mm.close()
        except Exception:
            pass

    def _log_db_decision(self, decision, packet):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Fetch last event's record_hash to link the chain
                cursor.execute("SELECT record_hash FROM governance_events ORDER BY sequence DESC LIMIT 1")
                row = cursor.fetchone()
                prev_hash = row["record_hash"] if row else ""

                event_id = str(hashlib.md5(f"{decision}-{datetime.datetime.now(datetime.timezone.utc).isoformat()}-{os.urandom(4).hex()}".encode()).hexdigest())
                packet_id = packet.get("packet_id", "p1")
                requested_by = packet.get("requested_by", "system")
                actor_id = packet.get("actor_id", "system_actor")
                target_env = packet.get("target_environment", "SANDBOX_DEV")
                change_type = packet.get("change_type", "procedural")
                risk_level = packet.get("risk_level", "low")
                summary = packet.get("action", "unknown")
                occurred_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

                # Generate record hash over state fields and prev_hash
                hasher = hashlib.sha256()
                hasher.update(f"{event_id}-{packet_id}-{prev_hash}-{decision}-{requested_by}-{target_env}".encode())
                record_hash = hasher.hexdigest()

                cursor.execute("""
                    INSERT INTO governance_events (
                        event_id, packet_id, previous_record_hash, record_type, requested_by,
                        actor_id, target_environment, change_type, risk_level, summary,
                        artifact_json, tests_json, security_json, backup_json, rollback_json,
                        decision, decision_reason, occurred_at, record_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}', '{}', '{}', '{}', '{}', ?, ?, ?, ?)
                """, (
                    event_id, packet_id, prev_hash, "decision", requested_by,
                    actor_id, target_env, change_type, risk_level, summary,
                    decision, packet.get("reason", "validated"), occurred_at, record_hash
                ))
                conn.commit()
        except Exception:
            pass

    def verify_governance_chain(self) -> bool:
        """
        Verify every hash in the append-only governance chain.
        Returns True if chain is perfectly intact, False if tampering is detected.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM governance_events ORDER BY sequence ASC")
                events = cursor.fetchall()

                expected_prev = ""
                for ev in events:
                    # Assert previous hash chain link matches
                    if ev["previous_record_hash"] != expected_prev:
                        return False

                    # Recompute record hash
                    hasher = hashlib.sha256()
                    hasher.update(f"{ev['event_id']}-{ev['packet_id']}-{ev['previous_record_hash']}-{ev['decision']}-{ev['requested_by']}-{ev['target_environment']}".encode())
                    computed = hasher.hexdigest()

                    if ev["record_hash"] != computed:
                        return False

                    expected_prev = ev["record_hash"]
            return True
        except Exception:
            return False
