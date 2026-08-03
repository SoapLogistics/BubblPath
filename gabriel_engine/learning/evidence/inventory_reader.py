from typing import Dict, Any, List
class InventoryReader:
    def read(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Converts raw inventory data into generic evidence formats
        evidence_list = []
        if "inventory" in data.get("source", ""):
            evidence_list.append({
                "type": "inventory",
                "content": data,
                "confidence": 0.9
            })
        return evidence_list
