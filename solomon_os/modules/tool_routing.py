from solomon_os.kernel import SolomonModule
import re
import logging

logger = logging.getLogger("ToolRoutingModule")

class ToolRoutingModule(SolomonModule):
    def start(self):
        super().start()
        # Expose RPC for action parsing
        self.kernel.register_rpc('parse_action', self.parse_action)

    def parse_action(self, text: str) -> dict:
        """
        Parses text for tags like [ACTION: CLICK | #id]
        and emits the corresponding Kernel events.
        """
        pattern = r"\[ACTION:\s*([^\|\]]+)(?:\|\s*([^\]]+))?\]"
        matches = re.findall(pattern, text)

        parsed_actions = []
        for match in matches:
            action_type = match[0].strip().upper()
            target = match[1].strip() if match[1] else None

            action_payload = {"action": action_type, "target": target}
            parsed_actions.append(action_payload)

            # Route to subsystems via Event Bus
            if action_type in ["CLICK", "TYPE", "SCROLL"]:
                self.kernel.publish("BROWSER_ACTION", self.name, action_payload)
                logger.info(f"Routed BROWSER_ACTION: {action_payload}")
            elif action_type == "BASH":
                self.kernel.publish("SYSTEM_BASH", self.name, action_payload)
                logger.info(f"Routed SYSTEM_BASH: {action_payload}")
            else:
                self.kernel.publish("UNKNOWN_ACTION", self.name, action_payload)
                logger.warning(f"Routed UNKNOWN_ACTION: {action_payload}")

        return {"actions_parsed": len(parsed_actions), "actions": parsed_actions}
