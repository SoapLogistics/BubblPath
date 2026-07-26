import mmap
import struct
import os

route_key = "solomon_governance_approval_packet"

class GovernanceApprovalLane:
    def __init__(self):
        self.log_file = "governance_log.bin"
        self._ensure_log_exists()

    def _ensure_log_exists(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, "wb") as f:
                # 1 header slot (64 bytes) + 1024 data slots (64 bytes each) = 65600 bytes
                f.write(b'\x00' * 65600)

    def review_packet(self, packet):
        action = packet.get("action", "unknown")
        high_risk_actions = {"jules_subprocess", "worker_activation", "git_push", "sudo", "ss1_mutation"}

        # Phase 7 Governance Gate Integration
        if action in high_risk_actions:
            if not packet.get("mark_approval") or not packet.get("ss3_review"):
                self._audit_event("refused", action)
                return {"status": "refused", "reason": "High-risk actions require explicit mark_approval and ss3_review", "audit_id": "aud_high_risk"}

        if packet.get("requires_approval") and packet.get("approved_by") != "Mark":
            self._audit_event("refused", action)
            return {"status": "refused", "reason": "Requires Mark approval", "audit_id": "aud_001"}

        # Check SS3 verification
        if packet.get("requires_ss3_review") and not packet.get("ss3_verified", False):
             self._audit_event("refused", action)
             return {"status": "refused", "reason": "Requires SS3 verification", "audit_id": "aud_002"}

        self._audit_event("approved", action)
        return {"status": "approved", "audit_id": "aud_003"}

    def _audit_event(self, status, action):
        # Hyper-efficient zero-copy append O(1) implementation
        try:
            with open(self.log_file, "r+b") as f:
                mm = mmap.mmap(f.fileno(), 0)
                # Read index from header (offset 0)
                current_idx = struct.unpack_from('I', mm, 0)[0]
                if current_idx >= 1024:
                    current_idx = 0 # Ring buffer wrap-around

                offset = 64 + (current_idx * 64)

                status_bytes = status.encode('utf-8')[:32].ljust(32, b'\x00')
                action_bytes = action.encode('utf-8')[:32].ljust(32, b'\x00')
                struct.pack_into('32s32s', mm, offset, status_bytes, action_bytes)

                # Increment index and store in header
                struct.pack_into('I', mm, 0, (current_idx + 1) % 1024)

                mm.flush()
                mm.close()
        except Exception:
            pass

    def get_audit_history(self, limit=10):
        # O(1) backward lookup for perpetual learning machines
        history = []
        try:
            with open(self.log_file, "rb") as f:
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                current_idx = struct.unpack_from('I', mm, 0)[0]

                for i in range(limit):
                    idx = (current_idx - 1 - i) % 1024
                    offset = 64 + (idx * 64)

                    status_bytes, action_bytes = struct.unpack_from('32s32s', mm, offset)
                    status = status_bytes.rstrip(b'\x00').decode('utf-8')
                    action = action_bytes.rstrip(b'\x00').decode('utf-8')

                    if status or action:
                        history.append({"status": status, "action": action})

                mm.close()
        except Exception:
            pass
        return history
