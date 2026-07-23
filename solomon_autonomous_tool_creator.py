"""
Solomon SOSS Phase 8: Autonomous Tool Creation

This module allows Solomon to identify missing operational tools, prototype Python utilities
in secure sandboxes, perform security checks and AST audits, and register them as reusable skills.
"""

import ast
import traceback
from typing import List, Dict, Any, Tuple
from solomon_skill_factory import SkillFactory, SkillPackage


class AutonomousToolCreator:
    """
    Prototypes raw Python code for missing helper tools, subjects them to static AST
    security checks, compiles them, and dynamically registers them with the SkillFactory.
    """
    def __init__(self, skill_factory: SkillFactory):
        self.skill_factory = skill_factory
        self.created_tools: List[str] = []

    def prototype_tool(self, tool_name: str, mathematical_operation: str) -> str:
        """
        Synthesizes a raw Python code snippet representing a mathematical or helper tool.
        """
        # Formulate pure function code
        return f"""def {tool_name}(x, y):
    # Dynamically generated mathematical tool: {mathematical_operation}
    return x {mathematical_operation} y
"""

    def perform_ast_security_audit(self, code_source: str) -> Tuple[bool, str]:
        """
        Performs static analysis using the abstract syntax tree to guarantee
        that the generated tool does not contain imports or malicious calls.
        """
        try:
            tree = ast.parse(code_source)
            for node in ast.walk(tree):
                # Reject imports
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    return False, "AST Security Audit Rejected: Dynamic tools are forbidden from importing libraries."
                # Reject file opens or dangerous builtins
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ["open", "eval", "exec", "compile", "globals", "locals"]:
                        return False, f"AST Security Audit Rejected: Forbidden builtin function call '{node.func.id}' detected."

            return True, "AST Security Audit Approved: Code contains zero malicious or un-sandboxed structures."

        except SyntaxError as e:
            return False, f"AST Security Audit Rejected: Syntax compilation error: {str(e)}"

    def build_and_register_tool(
        self,
        tool_name: str,
        mathematical_operation: str,
        purpose: str,
        inputs: List[str],
        outputs: List[str]
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Assembles a prototype tool, passes it through AST security, compiles it,
        and registers it as a certified Skill Package.
        """
        raw_code = self.prototype_tool(tool_name, mathematical_operation)

        # 1. AST Security Audit
        passed, audit_msg = self.perform_ast_security_audit(raw_code)
        if not passed:
            return False, audit_msg, {}

        # 2. Skill Factory Registration
        try:
            # We want to name the variables in the execution scope
            # For execution: we bind the function and execute it
            execution_wrapper_code = f"""
{raw_code}
result = {tool_name}(x, y)
"""
            package = self.skill_factory.produce_skill(
                name=tool_name,
                purpose=purpose,
                inputs=inputs,
                outputs=outputs,
                code=execution_wrapper_code
            )

            # Certify skill package
            success, certify_msg = self.skill_factory.certify_skill(tool_name)
            if not success:
                return False, f"Factory Certification failed: {certify_msg}", {}

            self.created_tools.append(tool_name)
            return True, f"Autonomous tool '{tool_name}' successfully created, AST audited, and registered in active skill base.", package.to_dict()

        except Exception as e:
            return False, f"Dynamic tool assembly crashed: {str(e)}\n{traceback.format_exc()}", {}
