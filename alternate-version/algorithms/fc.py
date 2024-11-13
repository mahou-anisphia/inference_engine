# /algorithms/fc.py
from collections import deque
import logging
from data.knowledge_base import KnowledgeBase


class ForwardChaining:
    """Implementation of the Forward Chaining algorithm"""

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

    def check_entailment(self, kb: KnowledgeBase, query: str) -> tuple[bool, list[str]]:
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
        self.logger.info(f"Starting Forward Chaining for query: {query}")
        self.logger.debug(f"Initial facts: {kb.facts}")

        # Track how many premises remain unknown for each clause
        count = {i: len(clause.premises)
                 for i, clause in enumerate(kb.clauses)}
        self.logger.debug(f"Initial premise counts: {count}")

        # Start with known facts
        agenda = deque(kb.facts)
        inferred = set(kb.facts)
        inferred_order = list(kb.facts)

        self.logger.info("Beginning forward chaining process")
        while agenda:
            p = agenda.popleft()
            self.logger.debug(f"Processing fact: {p}")

            # Check each clause
            for i, clause in enumerate(kb.clauses):
                if count[i] == 0:  # Skip if clause already triggered
                    continue

                self.logger.debug(f"Checking clause {i}: {clause}")

                # Check if p appears in premises
                for premise in clause.premises:
                    if premise.name == p and not premise.negative:
                        count[i] -= 1
                        self.logger.debug(
                            f"Matched premise in clause {i}, remaining premises: {count[i]}")

                        if count[i] == 0:  # All premises are known
                            conclusion = clause.conclusion.name
                            if conclusion not in inferred:
                                self.logger.info(
                                    f"New fact derived: {conclusion}")
                                agenda.append(conclusion)
                                inferred.add(conclusion)
                                inferred_order.append(conclusion)

        result = query in inferred
        self.logger.info(f"Query {'is' if result else 'is not'} entailed")
        self.logger.debug(f"Final inferred facts: {inferred}")
        return result, inferred_order
