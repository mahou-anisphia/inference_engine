# /algorithms/bc.py
import logging
from data.knowledge_base import KnowledgeBase


class BackwardChaining:
    """Implementation of the Backward Chaining algorithm"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create handler if it doesn't exist
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.indent_level = 0  # For tracking recursion depth in logs

    def check_entailment(self, kb: KnowledgeBase, query: str) -> tuple[bool, list[str]]:
        """
        Checks if KB entails query using backward chaining

        Backward chaining starts with the query and works
        backwards to known facts. It succeeds if it can
        find a chain of rules leading from facts to query.

        Args:
            kb (KnowledgeBase): The knowledge base
            query (str): The query to check

        Returns:
            tuple[bool, list[str]]: (Whether KB entails query,
                                    List of symbols used in proof)
        """
        self.logger.info(f"Starting Backward Chaining for query: {query}")
        self.logger.debug(f"Initial facts: {kb.facts}")

        inferred = set()  # Track symbols used in proof
        goals = set()     # Track current goals (for cycle detection)

        def bc_or(goal: str) -> bool:
            """
            Tries to prove goal symbol using OR strategy
            (prove goal directly or through any applicable rule)
            """
            indent = "  " * self.indent_level
            self.logger.debug(f"{indent}Attempting to prove: {goal}")

            if goal in kb.facts:
                self.logger.debug(f"{indent}Found fact: {goal}")
                inferred.add(goal)
                return True

            if goal in goals:
                self.logger.debug(f"{indent}Cycle detected with goal: {goal}")
                return False

            goals.add(goal)
            self.logger.debug(f"{indent}Current goals: {goals}")

            # Try each rule that could prove goal
            applicable_rules = [i for i, clause in enumerate(kb.clauses)
                                if clause.conclusion.name == goal]
            self.logger.debug(
                f"{indent}Applicable rules for {goal}: {applicable_rules}")

            self.indent_level += 1
            for i, clause in enumerate(kb.clauses):
                if clause.conclusion.name == goal:
                    self.logger.debug(f"{indent}Trying rule {i}: {clause}")
                    if bc_and(clause.premises):
                        inferred.add(goal)
                        goals.remove(goal)
                        self.logger.debug(
                            f"{indent}Successfully proved {goal}")
                        self.indent_level -= 1
                        return True

            self.indent_level -= 1
            goals.remove(goal)
            self.logger.debug(f"{indent}Failed to prove {goal}")
            return False

        def bc_and(premises) -> bool:
            """
            Tries to prove all premises using AND strategy
            (all premises must be true)
            """
            indent = "  " * self.indent_level
            self.logger.debug(
                f"{indent}Attempting to prove premises: {[str(p) for p in premises]}")

            for premise in premises:
                if not bc_or(premise.name):
                    self.logger.debug(
                        f"{indent}Failed to prove premise: {premise}")
                    return False

            self.logger.debug(f"{indent}Successfully proved all premises")
            return True

        result = bc_or(query)
        self.logger.info(f"Query {'is' if result else 'is not'} entailed")
        self.logger.debug(f"Symbols used in proof: {inferred}")
        return result, list(inferred)
