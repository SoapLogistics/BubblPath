# services/solomon_governance_approval_packet.py
import mmap
import struct
import os
import time

route_key = "solomon_governance_approval_packet"

class GovernanceApprovalLane:
    def __init__(self):
        self.log_file = "governance_log.bin"
        self._ensure_log_exists()

    def _ensure_log_exists(self):
        # Overwrite/create with the compliant 256-byte slot size (262144 bytes total)
        if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) != 262144:
            with open(self.log_file, "wb") as f:
                # 1024 slots * 256 bytes each = 262144 bytes
                f.write(b'\x00' * 262144)

    def review_packet(self, packet):
        # Phase 7 Governance Gate explicitly blocks high-risk actions unless approved by Mark (or mark_approval is True)
        if packet.get("requires_approval") or packet.get("high_risk"):
            approved_by = packet.get("approved_by")
            mark_approval = packet.get("mark_approval", False)
            if approved_by != "Mark" and not mark_approval:
                self._audit_event("refused", packet.get("action", "unknown"), stage="authorization", payload="Requires Mark approval")
                return {"status": "refused", "reason": "Requires Mark approval", "audit_id": "aud_001"}

        # Check SS3 verification context requirements
        if packet.get("requires_ss3_review"):
            ss3_verified = packet.get("ss3_verified", False)
            ss3_review = packet.get("ss3_review", False)
            if not ss3_verified and not ss3_review:
                 self._audit_event("refused", packet.get("action", "unknown"), stage="ss3_review", payload="Requires SS3 verification")
                 return {"status": "refused", "reason": "Requires SS3 verification", "audit_id": "aud_002"}

        self._audit_event(
            "approved",
            packet.get("action", "unknown"),
            stage="ss3_review" if packet.get("requires_ss3_review") else "authorization",
            reviewer=packet.get("approved_by", "Mark"),
            payload="All context requirements successfully met"
        )
        return {"status": "approved", "audit_id": "aud_003"}

    def _audit_event(self, status, action, stage="main", reviewer="Mark", checksum="", payload=""):
        # Hyper-efficient zero-copy append
        # Here we'll append to the first empty slot we find, simulating a ring buffer logic
        try:
            with open(self.log_file, "r+b") as f:
                mm = mmap.mmap(f.fileno(), 0)
                # Slot size 256 bytes. Find first empty slot (starting with \x00)
                for i in range(1024):
                    offset = i * 256
                    if mm[offset] == 0:
                        # Pack status(32s), stage(16s), reviewer(16s), action(32s), checksum(32s), payload(64s), padding(56s), timestamp(d)
                        status_bytes = status.encode('utf-8')[:32].ljust(32, b'\x00')
                        stage_bytes = stage.encode('utf-8')[:16].ljust(16, b'\x00')
                        reviewer_bytes = reviewer.encode('utf-8')[:16].ljust(16, b'\x00')
                        action_bytes = action.encode('utf-8')[:32].ljust(32, b'\x00')
                        checksum_bytes = checksum.encode('utf-8')[:32].ljust(32, b'\x00')
                        payload_bytes = payload.encode('utf-8')[:64].ljust(64, b'\x00')
                        padding_bytes = b'\x00' * 56
                        timestamp = time.time()

                        packed = struct.pack(
                            '!32s16s16s32s32s64s56sd',
                            status_bytes,
                            stage_bytes,
                            reviewer_bytes,
                            action_bytes,
                            checksum_bytes,
                            payload_bytes,
                            padding_bytes,
                            timestamp
                        )
                        mm[offset:offset+256] = packed
                        break
                mm.flush()
                mm.close()
        except Exception:
            pass
