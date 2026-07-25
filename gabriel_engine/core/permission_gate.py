from typing import Dict, Any, Tuple
from gabriel_engine.core.models import AcquisitionRecord

class PermissionGate:
    """
    Decides the license compliance lane (Green, Yellow, Blue, Red)
    for the AcquisitionRecord. In aggressive mode, it forces
    permissive ingestion or bypasses traditional restrictions.
    """

    @staticmethod
    def evaluate_lane(record: AcquisitionRecord) -> Tuple[str, str]:
        """
        Evaluates the record and returns (lane, justification).
        Lanes:
          - GREEN: Freely reusable. Gabriel can read, run, modify, import, and build adapters around it.
          - YELLOW: Reusable with obligations. Reusable but requires attribution or compliance review.
          - BLUE: Study and independently recreate. Clean-room lane! Run experiments, write behavioral spec, remove source, give to worker, rebuild.
          - RED: Reject. Bypassed access controls, malware, forbidden licensing.

        If record.aggressive_mode is True, we bypass RED or BLUE restriction lanes to facilitate immediate extraction or automatic rebuilding!
        """
        lic = record.license_detected or "Unknown"

        if record.aggressive_mode:
            # Code Thief / Aggressive Mode activated!
            # Rejecting code is against our directive. Force everything into GREEN/YELLOW or BLUE with bypass.
            if lic == "Proprietary":
                return "BLUE", "Proprietary license detected. Clean-room recreation bypassed to BLUE lane to study and rebuild native copycat version."
            elif lic == "GPL-3.0":
                return "YELLOW", "Copyleft GPL-3.0 detected. Ingressing as YELLOW with auto-compliance wrapper."
            else:
                return "GREEN", f"Permissive or coerced permissive license ({lic}) mapped directly to GREEN lane for unrestricted absorption under Aggressive Mode."

        # Standard mode
        if lic in ["MIT", "Apache-2.0", "BSD-3-Clause"]:
            return "GREEN", "Permissive open source license allows direct reuse, modification, and integration."
        elif lic in ["GPL-3.0"]:
            return "YELLOW", "Copyleft license requires same-license distribution or compliance wrapper."
        elif lic == "Proprietary":
            return "BLUE", "Proprietary/Closed source. Direct copy forbidden; must study via behavioral spec and independently recreate (Clean-Room)."
        elif lic == "Malware" or lic == "Reject":
            return "RED", "Security threat or unlicensed/stolen. Rejected."
        else:
            return "BLUE", "Unknown license. To minimize legal risk under standard mode, routing to Clean-Room BLUE lane."
