# /algorithms/fc.py
from collections import deque
from data.knowledge_base import KnowledgeBase


class ForwardChaining:
    """Implementation of the Forward Chaining algorithm"""

    @staticmethod
    def check_entailment(kb: KnowledgeBase, query: str) -> tuple[bool, list[str]]:
        """
        Checks if KB entails query using forward chaining

        Forward chaining starts with known facts and applies
        rules to derive new facts until either:
        1. Query is derived (entailed)
        2. No new facts can be derived (not entailed)

        Args:
            kb (KnowledgeBase): The knowledge base
            query (str): The query to check

        Returns:
            tuple[bool, list[str]]: (Whether KB entails query,
                                    List of symbols derived in order)
        """
        # Track how many premises remain unknown for each clause
        count = {i: len(clause.premises)
                 for i, clause in enumerate(kb.clauses)}

        # Start with known facts
        agenda = deque(kb.facts)
        inferred = set(kb.facts)
        inferred_order = list(kb.facts)

        while agenda:
            p = agenda.popleft()

            # Check each clause
            for i, clause in enumerate(kb.clauses):
                if count[i] == 0:  # Skip if clause already triggered
                    continue

                # Check if p appears in premises
                for premise in clause.premises:
                    if premise.name == p and not premise.negative:
                        count[i] -= 1
                        if count[i] == 0:  # All premises are known
                            conclusion = clause.conclusion.name
                            if conclusion not in inferred:
                                agenda.append(conclusion)
                                inferred.add(conclusion)
                                inferred_order.append(conclusion)

        return query in inferred, inferred_order
