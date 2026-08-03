from typing import Dict, Any, List
class MissionReader:
    def read(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        evidence_list = []
        # The logic was too restrictive (only matching "source" == "mission").
        # We'll extract if called.
        evidence_list.append({
            "type": "mission",
            "content": data,
            "success": data.get("success", False),
            "confidence": 1.0
        })
        return evidence_list
