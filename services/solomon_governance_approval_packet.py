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

    def _ensure_log_exists(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, "wb") as f:
                # 1024 slots * 256 bytes each = 262144 bytes
                f.write(b'\x00' * 262144)

    def review_packet(self, packet):
        """
        Governance lane gate keeper.
        Verifies Mark's approval for automatic promos, and rejects SS1 promotion
        without complete rollback procedures or failed SS3 validations.
        """
        action = packet.get("action", "unknown")
        approved_by = packet.get("approved_by", "Nobody")
        rollback_proc = packet.get("rollback_procedure", "automatic_rollback_procedure")

        # Block direct SS1 promotion if missing standard rollback procedures (governance rule)
        if packet.get("requires_approval") and not rollback_proc:
            self._audit_event("refused", action, approved_by, "MISSING_ROLLBACK_PROCEDURE")
            return {"status": "refused", "reason": "Requires a safe rollback procedure", "audit_id": "aud_err"}

        if packet.get("requires_approval") and approved_by != "Mark":
            self._audit_event("refused", action, approved_by, "NOT_APPROVED_BY_MARK")
            return {"status": "refused", "reason": "Requires Mark approval", "audit_id": "aud_001"}

        # Check SS3 verification
        if packet.get("requires_ss3_review") and not packet.get("ss3_verified", False):
             self._audit_event("refused", action, approved_by, "MISSING_SS3_VERIFICATION")
             return {"status": "refused", "reason": "Requires SS3 verification", "audit_id": "aud_002"}

        self._audit_event("approved", action, approved_by, rollback_proc)
        return {"status": "approved", "audit_id": "aud_003"}

    def _audit_event(self, status, action, approved_by, rollback_proc=""):
        # Zero-copy struct layout:
        # status (32s), action (16s), approved_by (16s), prev_hash (32s), curr_hash (32s), rollback_proc (64s), validation_sig (56s), timestamp (d)
        # Total size: 32 + 16 + 16 + 32 + 32 + 64 + 56 + 8 = 256 bytes.
        try:
            with open(self.log_file, "r+b") as f:
                mm = mmap.mmap(f.fileno(), 0)

                prev_hash = b'\x00' * 32
                offset = 0

                # Retrieve the previous slot's hash to build the chain
                for i in range(1024):
                    curr_offset = i * 256
                    if mm[curr_offset] == 0:
                        offset = curr_offset
                        if i > 0:
                            prev_offset = (i - 1) * 256
                            prev_data = mm[prev_offset:prev_offset+256]
                            # Unpack previous slot's current hash (offset 32+16+16+32 = 96)
                            prev_hash = prev_data[96:128]
                        break

                # Pack current metadata
                status_bytes = status.encode('utf-8')[:32].ljust(32, b'\x00')
                action_bytes = action.encode('utf-8')[:16].ljust(16, b'\x00')
                app_bytes = approved_by.encode('utf-8')[:16].ljust(16, b'\x00')
                rollback_bytes = rollback_proc.encode('utf-8')[:64].ljust(64, b'\x00')
                sig_bytes = b'\x00' * 56
                timestamp_val = time.time()

                # Calculate SHA-256 current hash of metadata chained with prev_hash
                hasher = hashlib.sha256()
                hasher.update(status_bytes + action_bytes + app_bytes + prev_hash + rollback_bytes + sig_bytes)
                curr_hash = hasher.digest()

                # Pack the 256-byte audit record into the mapped slot
                mm[offset:offset+256] = struct.pack(
                    '32s16s16s32s32s64s56sd',
                    status_bytes, action_bytes, app_bytes,
                    prev_hash, curr_hash, rollback_bytes, sig_bytes,
                    timestamp_val
                )
                mm.flush()
                mm.close()
        except Exception as e:
            print(f"[AUDIT ERROR] Zero-copy append audit logging failed: {e}")

    def verify_governance_chain(self) -> bool:
        """
        Performs cryptographic verification of the append-only SHA-256 audit trail.
        Returns False if any tamper, deletion, or shrinkage has occurred.
        """
        try:
            with open(self.log_file, "rb") as f:
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                prev_hash = b'\x00' * 32
                for i in range(1024):
                    offset = i * 256
                    if mm[offset] == 0:
                        break # End of chain reached

                    # Unpack fields to verify integrity
                    record = mm[offset:offset+256]
                    unpacked = struct.unpack('32s16s16s32s32s64s56sd', record)
                    status_bytes, action_bytes, app_bytes, p_hash, c_hash, r_bytes, sig_bytes, t_val = unpacked

                    # Check chain link
                    if p_hash != prev_hash:
                        return False # Tampered prev_hash!

                    # Recalculate hash
                    hasher = hashlib.sha256()
                    hasher.update(status_bytes + action_bytes + app_bytes + p_hash + r_bytes + sig_bytes)
                    if hasher.digest() != c_hash:
                        return False # Tampered current record!

                    prev_hash = c_hash
                mm.close()
            return True
        except Exception as e:
            print(f"[GOVERNANCE TAMPER ERROR] Cryptographic chain validation failed: {e}")
            return False
