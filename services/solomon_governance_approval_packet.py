# services/solomon_governance_approval_packet.py
import mmap
import struct
import os
import time
from typing import Optional, Dict

route_key = "solomon_governance_approval_packet"

class GovernanceApprovalLane:
    def __init__(self):
        self.log_file = "governance_log.bin"
        self._ensure_log_exists()

    def _ensure_log_exists(self):
        # 1024 slots * 256 bytes each = 262144 bytes
        target_size = 262144
        if not os.path.exists(self.log_file):
            with open(self.log_file, "wb") as f:
                f.write(b'\x00' * target_size)
        else:
            # Resize if current file size is less than target size
            current_size = os.path.getsize(self.log_file)
            if current_size < target_size:
                with open(self.log_file, "ab") as f:
                    f.write(b'\x00' * (target_size - current_size))

    def review_packet(self, packet: Dict) -> Dict:
        p_id = packet.get("packet_id", "pkg_auto")
        env = packet.get("environment", "unknown_env")
        action = packet.get("action", "unknown_action")
        author = packet.get("author", "unknown_author")
        v_hash = packet.get("validation_hash", "")
        r_hash = packet.get("rollback_hash", "")

        # Strictly block promotions to SS1 if they lack a rollback_procedure or if validation failed/not successful
        if env == "SS1":
            if not packet.get("rollback_procedure"):
                self._audit_event(p_id, env, "refused", action, author, v_hash, r_hash)
                return {
                    "status": "refused",
                    "reason": "Promotion to SS1 strictly blocked: missing 'rollback_procedure'",
                    "audit_id": "aud_ss1_blocked_rollback"
                }
            if packet.get("validation_failed", False) or not packet.get("validation_success", True):
                self._audit_event(p_id, env, "refused", action, author, v_hash, r_hash)
                return {
                    "status": "refused",
                    "reason": "Promotion to SS1 strictly blocked: validation failed",
                    "audit_id": "aud_ss1_blocked_validation"
                }

        # Check existing approval gates
        if packet.get("requires_approval") and packet.get("approved_by") != "Mark":
            self._audit_event(p_id, env, "refused", action, author, v_hash, r_hash)
            return {"status": "refused", "reason": "Requires Mark approval", "audit_id": "aud_001"}

        # Check SS3 verification
        if packet.get("requires_ss3_review") and not packet.get("ss3_verified", False):
            self._audit_event(p_id, env, "refused", action, author, v_hash, r_hash)
            return {"status": "refused", "reason": "Requires SS3 verification", "audit_id": "aud_002"}

        self._audit_event(p_id, env, "approved", action, author, v_hash, r_hash)
        return {"status": "approved", "audit_id": "aud_003"}

    def _audit_event(self, packet_id, environment, status, action, author, validation_hash, rollback_hash):
        # Hyper-efficient zero-copy append using 256-byte slots
        # Struct format: 32s16s16s32s32s64s56sd
        try:
            with open(self.log_file, "r+b") as f:
                mm = mmap.mmap(f.fileno(), 0)
                # Slot size 256 bytes. Find first empty slot (starting with \x00)
                for i in range(1024):
                    offset = i * 256
                    if mm[offset] == 0:
                        p_id = str(packet_id or "").encode('utf-8')[:32].ljust(32, b'\x00')
                        env = str(environment or "").encode('utf-8')[:16].ljust(16, b'\x00')
                        stat = str(status or "").encode('utf-8')[:16].ljust(16, b'\x00')
                        act = str(action or "").encode('utf-8')[:32].ljust(32, b'\x00')
                        auth = str(author or "").encode('utf-8')[:32].ljust(32, b'\x00')
                        v_hash = str(validation_hash or "").encode('utf-8')[:64].ljust(64, b'\x00')
                        r_hash = str(rollback_hash or "").encode('utf-8')[:56].ljust(56, b'\x00')
                        t_stamp = float(time.time())

                        mm[offset:offset+256] = struct.pack('32s16s16s32s32s64s56sd',
                                                            p_id, env, stat, act, auth, v_hash, r_hash, t_stamp)
                        break
                mm.flush()
                mm.close()
        except Exception:
            pass

    def read_audit_log(self, index: int) -> Optional[Dict]:
        try:
            with open(self.log_file, "rb") as f:
                f.seek(index * 256)
                data = f.read(256)
                if not data or len(data) < 256 or data[0] == 0:
                    return None
                p_id, env, stat, act, auth, v_hash, r_hash, t_stamp = struct.unpack('32s16s16s32s32s64s56sd', data)
                return {
                    "packet_id": p_id.decode('utf-8').rstrip('\x00'),
                    "environment": env.decode('utf-8').rstrip('\x00'),
                    "status": stat.decode('utf-8').rstrip('\x00'),
                    "action": act.decode('utf-8').rstrip('\x00'),
                    "author": auth.decode('utf-8').rstrip('\x00'),
                    "validation_hash": v_hash.decode('utf-8').rstrip('\x00'),
                    "rollback_hash": r_hash.decode('utf-8').rstrip('\x00'),
                    "timestamp": t_stamp
                }
        except Exception:
            return None
