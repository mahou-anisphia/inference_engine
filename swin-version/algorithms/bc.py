# /algorithms/bc.py
from data.knowledge_base import KnowledgeBase
from collections import OrderedDict  # For consistent ordering


class BackwardChaining:
    """Implementation of the Backward Chaining algorithm"""

    @staticmethod
    def check_entailment(kb: KnowledgeBase, query: str) -> tuple[bool, list[str]]:
        """
        Checks if KB entails query using backward chaining

        Args:
            kb (KnowledgeBase): The knowledge base
            query (str): The query to check

        Returns:
            tuple[bool, list[str]]: (Whether KB entails query,
                                    List of symbols used in proof in order)
        """
        # Use OrderedDict to maintain consistent ordering of inferred symbols
        inferred = OrderedDict()
        goals = set()  # Track current goals for cycle detection

        def bc_or(goal: str) -> bool:
            """
            Tries to prove goal symbol using OR strategy
            (prove goal directly or through any applicable rule)
            """
            # Base case: goal is a known fact
            if goal in kb.facts:
                if goal not in inferred:
                    inferred[goal] = None
                return True

            # Check for cycles
            if goal in goals:
                return False

            goals.add(goal)

            # Sort clauses by conclusion to ensure consistent processing order
            applicable_clauses = sorted(
                [clause for clause in kb.clauses if clause.conclusion.name == goal],
                key=lambda x: x.conclusion.name
            )

            # Try each rule that could prove goal
            for clause in applicable_clauses:
                # Sort premises to ensure consistent order of evaluation
                sorted_premises = sorted(clause.premises, key=lambda x: x.name)
                if bc_and(sorted_premises):
                    if goal not in inferred:
                        inferred[goal] = None
                    goals.remove(goal)
                    return True

            goals.remove(goal)
            return False

        def bc_and(premises) -> bool:
            """
            Tries to prove all premises using AND strategy
            (all premises must be true)
            """
            # Process premises in sorted order for consistency
            return all(bc_or(premise.name) for premise in premises)

        result = bc_or(query)
        return result, list(inferred.keys())


"""
        inferred = set()  # This allowed for inconsistent ordering
        goals = set()

        def bc_or(goal: str) -> bool:
            if goal in kb.facts:
                inferred.add(goal)  # Adding to set - no ordering guaranteed
                return True

            if goal in goals:
                return False

            goals.add(goal)

            # No sorting of clauses - could process in different orders
            for clause in kb.clauses:
                if clause.conclusion.name == goal:
                    # No sorting of premises - could evaluate in different orders
                    if bc_and(clause.premises):
                        inferred.add(goal)
                        goals.remove(goal)
                        return True

            goals.remove(goal)
            return False

        def bc_and(premises) -> bool:
            # No guaranteed order of premise evaluation
            return all(bc_or(premise.name) for premise in premises)

        result = bc_or(query)
        return result, list(inferred)  # Converting set to list - order not guaranteed
"""
