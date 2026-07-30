# services/solomon_governance_approval_packet.py
import mmap
import struct
import os

route_key = "solomon_governance_approval_packet"

import hashlib
import time

class GovernanceApprovalLane:
    def __init__(self):
        self.log_file = "governance_log.bin"
        self._ensure_log_exists()
        # In-memory revocation cache for active sessions
        self._revocations = set()

    def _ensure_log_exists(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, "wb") as f:
                # 1024 slots * 96 bytes each = 98304 bytes (status:32s, action:32s, prev_hash:32s)
                f.write(b'\x00' * 98304)

    def revoke_approval(self, action: str):
        """Programmatically revoke any active approval for a given action."""
        self._revocations.add(action)

    def review_packet(self, packet):
        # Implementation of governance gate
        action = packet.get("action", "unknown")

        # Check for revocation states
        if action in self._revocations:
            self._audit_event("revoked", action)
            return {"status": "refused", "reason": "Approval has been revoked programmatically", "audit_id": "aud_004"}

        # Strict Governance Segregation: Prevent self-approvals
        if packet.get("requester") and packet.get("approved_by") and packet.get("requester") == packet.get("approved_by"):
            self._audit_event("refused_self_approval", action)
            return {"status": "refused", "reason": "Strict segregation policy violation: self-approval is forbidden", "audit_id": "aud_006"}

        # Expiration Check
        timestamp = packet.get("timestamp", time.time())
        expires_at = packet.get("expires_at", timestamp + 3600)  # Default 1-hour expiration
        if time.time() > expires_at:
            self._audit_event("expired", action)
            return {"status": "refused", "reason": "Governance approval has expired", "audit_id": "aud_005"}

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
        # Hyper-efficient zero-copy append with secure cryptographic hash chaining
        try:
            with open(self.log_file, "r+b") as f:
                mm = mmap.mmap(f.fileno(), 0)
                # Slot size 96 bytes. Find first empty slot (starting with \x00)
                for i in range(1024):
                    offset = i * 96
                    if mm[offset] == 0:
                        # Fetch hash of previous block if exists
                        prev_hash = b'\x00' * 32
                        if i > 0:
                            prev_offset = (i - 1) * 96
                            prev_block = mm[prev_offset:prev_offset+96]
                            prev_hash = hashlib.sha256(prev_block).digest()

                        # Pack status(32s), action(32s), prev_hash(32s)
                        status_bytes = status.encode('utf-8')[:32].ljust(32, b'\x00')
                        action_bytes = action.encode('utf-8')[:32].ljust(32, b'\x00')
                        mm[offset:offset+96] = struct.pack('32s32s32s', status_bytes, action_bytes, prev_hash)
                        break
                mm.flush()
                mm.close()
        except Exception:
            pass

    def verify_integrity(self) -> bool:
        """Sequential cryptographic audit-trail verification to detect history tampering."""
        try:
            with open(self.log_file, "rb") as f:
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                for i in range(1, 1024):
                    offset = i * 96
                    if mm[offset] == 0:
                        break  # reached end of active logs

                    # Read current slot
                    block_bytes = mm[offset:offset+96]
                    status_bytes, action_bytes, recorded_prev_hash = struct.unpack('32s32s32s', block_bytes)

                    # Calculate expected hash of previous slot
                    prev_offset = (i - 1) * 96
                    prev_block = mm[prev_offset:prev_offset+96]
                    expected_hash = hashlib.sha256(prev_block).digest()

                    if recorded_prev_hash != expected_hash:
                        mm.close()
                        return False
                mm.close()
        except Exception:
            return False
        return True
