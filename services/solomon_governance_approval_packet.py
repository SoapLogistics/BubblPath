# services/solomon_governance_approval_packet.py
import mmap
import struct
import os
import time

route_key = "solomon_governance_approval_packet"

class GovernanceApprovalLane:
    # 256 bytes per slot
    # struct format: 32s (packet_id), 16s (environment), 16s (status), 32s (action), 32s (author), 64s (validation_hash), 56s (rollback_hash), d (timestamp)
    STRUCT_FORMAT = '32s16s16s32s32s64s56sd'
    SLOT_SIZE = 256
    MAX_SLOTS = 1024
    HIGH_RISK_ACTIONS = {"jules_subprocess", "worker_activation", "git_push", "sudo", "ss1_mutation"}

    def __init__(self, log_file="governance_log.bin"):
        self.log_file = log_file
        self._ensure_log_exists()

    def _ensure_log_exists(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, "wb") as f:
                f.write(b'\x00' * (self.SLOT_SIZE * self.MAX_SLOTS))

    def review_packet(self, packet):
        action = packet.get("action", "unknown")

        # High risk actions require Mark approval and SS3 verification
        if action in self.HIGH_RISK_ACTIONS:
            if packet.get("approved_by") != "Mark":
                self._audit_event(packet, "refused")
                return {"status": "refused", "reason": "Requires Mark approval for high-risk action", "audit_id": packet.get("packet_id", "unknown")}
            if not packet.get("ss3_verified", False):
                self._audit_event(packet, "refused")
                return {"status": "refused", "reason": "Requires SS3 verification for high-risk action", "audit_id": packet.get("packet_id", "unknown")}

        # Standard checks
        if packet.get("requires_approval") and packet.get("approved_by") != "Mark":
            self._audit_event(packet, "refused")
            return {"status": "refused", "reason": "Requires Mark approval", "audit_id": packet.get("packet_id", "unknown")}

        if packet.get("requires_ss3_review") and not packet.get("ss3_verified", False):
             self._audit_event(packet, "refused")
             return {"status": "refused", "reason": "Requires SS3 verification", "audit_id": packet.get("packet_id", "unknown")}

        self._audit_event(packet, "approved")
        return {"status": "approved", "audit_id": packet.get("packet_id", "unknown")}

    def promote_packet(self, packet):
        # Strict promotion flow SS2 -> SS3 -> SS1
        current_env = packet.get("environment", "SS2")
        target_env = packet.get("target_environment", "SS1")

        if current_env == "SS2" and target_env == "SS1":
            self._audit_event(packet, "refused")
            return {"status": "refused", "reason": "Cannot promote directly from SS2 to SS1. Must go through SS3."}

        # Review packet
        review_result = self.review_packet(packet)
        if review_result["status"] != "approved":
            return review_result

        # If approved, perform promotion logic and log as promoted
        self._audit_event(packet, "promoted")
        return {"status": "promoted", "audit_id": packet.get("packet_id", "unknown")}

    def rollback(self, rollback_hash):
        # find the audit event with the rollback hash
        try:
            with open(self.log_file, "r+b") as f:
                mm = mmap.mmap(f.fileno(), 0)
                for i in range(self.MAX_SLOTS):
                    offset = i * self.SLOT_SIZE
                    if mm[offset] == 0:
                        break

                    data = struct.unpack(self.STRUCT_FORMAT, mm[offset:offset+self.SLOT_SIZE])
                    current_rollback_hash = data[6].decode('utf-8').rstrip('\x00')

                    if current_rollback_hash == rollback_hash:
                        # Found the entry, let's append a rollback event
                        packet = {
                            "packet_id": data[0].decode('utf-8').rstrip('\x00') + "_rollback",
                            "environment": data[1].decode('utf-8').rstrip('\x00'),
                            "action": "rollback_" + data[3].decode('utf-8').rstrip('\x00'),
                            "author": "system",
                            "validation_hash": data[5].decode('utf-8').rstrip('\x00'),
                            "rollback_hash": current_rollback_hash
                        }
                        self._audit_event(packet, "rolled_back")
                        mm.close()
                        return {"status": "rolled_back", "rollback_hash": rollback_hash}
                mm.close()
        except Exception:
            pass
        return {"status": "failed", "reason": "Rollback hash not found"}

    def _audit_event(self, packet, status):
        packet_id = packet.get("packet_id", "unknown")
        if not isinstance(packet_id, str):
            packet_id = str(packet_id)
        packet_id_bytes = packet_id.encode('utf-8')[:32].ljust(32, b'\x00')

        environment = packet.get("environment", "unknown").encode('utf-8')[:16].ljust(16, b'\x00')
        status_bytes = status.encode('utf-8')[:16].ljust(16, b'\x00')
        action = packet.get("action", "unknown").encode('utf-8')[:32].ljust(32, b'\x00')
        author = packet.get("author", "unknown").encode('utf-8')[:32].ljust(32, b'\x00')
        val_hash = packet.get("validation_hash", "").encode('utf-8')[:64].ljust(64, b'\x00')
        roll_hash = packet.get("rollback_hash", "").encode('utf-8')[:56].ljust(56, b'\x00')
        ts = time.time()

        try:
            with open(self.log_file, "r+b") as f:
                mm = mmap.mmap(f.fileno(), 0)
                for i in range(self.MAX_SLOTS):
                    offset = i * self.SLOT_SIZE
                    if mm[offset] == 0:
                        mm[offset:offset+self.SLOT_SIZE] = struct.pack(
                            self.STRUCT_FORMAT,
                            packet_id_bytes, environment, status_bytes, action, author, val_hash, roll_hash, ts
                        )
                        break
                mm.flush()
                mm.close()
        except Exception:
            pass
