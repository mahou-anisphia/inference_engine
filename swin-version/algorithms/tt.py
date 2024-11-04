# /algorithms/tt.py
from itertools import product
from data.knowledge_base import KnowledgeBase, Clause, Literal


class TruthTable:
    """Implementation of the Truth Table checking algorithm"""

    @staticmethod
    def check_entailment(kb: KnowledgeBase, query: str) -> tuple[bool, int]:
        """
        Checks if the knowledge base entails the query using truth table method

        Works by checking all possible truth assignments. KB entails query if
        query is true in all models where KB is true.

        Args:
            kb (KnowledgeBase): The knowledge base
            query (str): The query to check

        Returns:
            tuple[bool, int]: (Whether KB entails query, Number of models where KB is true)
        """
        symbols = list(kb.symbols)
        models_count = 0

        # Generate all possible truth assignments
        for values in product([False, True], repeat=len(symbols)):
            model = dict(zip(symbols, values))

            # If KB is true in this model
            if TruthTable._evaluate_kb(kb, model):
                models_count += 1
                # If KB is true but query is false, KB doesn't entail query
                if not model[query]:
                    return False, models_count

        return True, models_count

    @staticmethod
    def _evaluate_kb(kb: KnowledgeBase, model: dict) -> bool:
        """Evaluates if KB is true under given model"""
        return all(TruthTable._evaluate_clause(clause, model) for clause in kb.clauses)

    @staticmethod
    def _evaluate_clause(clause: Clause, model: dict) -> bool:
        """
        Evaluates if a clause is true under given model

        For implications (p & q => r), true except when
        premises are true but conclusion is false
        """
        if not clause.premises:  # It's a fact
            return model[clause.conclusion.name]

        premises_true = all(model[premise.name] for premise in clause.premises)
        return (not premises_true) or model[clause.conclusion.name]
