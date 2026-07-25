import json

class BrowserCompanionBackend:
    """
    Backend integration for the Solomon Browser Companion.
    Parses context from the unified extension and translates user chat
    into actionable DOM steps.
    """

    def process_chat(self, user_message, context, openai_client):
        """
        Processes a chat message with full DOM/URL context and uses LLM
        to propose specific actions like clicking or filling inputs.
        """
        system_prompt = (
            "You are Solomon, integrated into the user's browser companion. "
            "You are observing the following context:\n"
            f"{json.dumps(context, indent=2)}\n\n"
            "Respond helpfully to the user's message. If the user asks you to perform an action on the page, "
            "you MUST output your proposed actions using the following tags exactly:\n"
            "[ACTION: #selector] (for clicks/buttons)\n"
            "[FILL: #selector | value] (for text inputs)\n\n"
            "Do not execute actions automatically; they will be queued for manual user approval."
        )

        response = openai_client.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2
        )

        reply = response.choices[0].message["content"]

        # Parse proposed actions from the text
        proposed_actions = self._extract_actions(reply)

        return {
            "reply": reply,
            "proposed_actions": proposed_actions
        }

    def _extract_actions(self, text):
        actions = []
        import re

        # Match [ACTION: #selector]
        action_pattern = re.compile(r"\[ACTION:\s*([^\]]+)\]")
        for match in action_pattern.finditer(text):
            actions.append({
                "type": "ACTION",
                "selector": match.group(1).strip()
            })

        # Match [FILL: #selector | value]
        fill_pattern = re.compile(r"\[FILL:\s*([^|]+)\s*\|\s*([^\]]+)\]")
        for match in fill_pattern.finditer(text):
            actions.append({
                "type": "FILL",
                "selector": match.group(1).strip(),
                "value": match.group(2).strip()
            })

        return actions
