# /algorithms/tt.py
import logging
from itertools import product
from data.knowledge_base import KnowledgeBase, Clause, Literal


class TruthTable:
    """Implementation of the Truth Table checking algorithm"""

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

    def check_entailment(self, kb: KnowledgeBase, query: str) -> tuple[bool, int]:
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
        self.logger.info(
            f"Starting Truth Table entailment check for query: {query}")
        self.logger.debug(f"Knowledge base contains {len(kb.clauses)} clauses")

        symbols = list(kb.symbols)
        self.logger.debug(f"Symbols in knowledge base: {symbols}")

        models_count = 0
        total_models = 2 ** len(symbols)
        self.logger.info(f"Checking {total_models} possible models")

        # Generate all possible truth assignments
        for values in product([False, True], repeat=len(symbols)):
            model = dict(zip(symbols, values))
            self.logger.debug(f"Checking model: {model}")

            # If KB is true in this model
            if self._evaluate_kb(kb, model):
                models_count += 1
                self.logger.debug(f"Model {model} satisfies KB")

                # If KB is true but query is false, KB doesn't entail query
                if not model[query]:
                    self.logger.info(
                        f"Found counterexample model where KB is true but query is false: {model}")
                    return False, models_count

        self.logger.info(
            f"Query is entailed. KB satisfied in {models_count}/{total_models} models")
        return True, models_count

    def _evaluate_kb(self, kb: KnowledgeBase, model: dict) -> bool:
        """Evaluates if KB is true under given model"""
        for clause in kb.clauses:
            if not self._evaluate_clause(clause, model):
                self.logger.debug(f"Clause {clause} is false in model {model}")
                return False
        return True

    def _evaluate_clause(self, clause: Clause, model: dict) -> bool:
        """
        Evaluates if a clause is true under given model

        For implications (p & q => r), true except when
        premises are true but conclusion is false
        """
        if not clause.premises:  # It's a fact
            result = model[clause.conclusion.name]
            self.logger.debug(f"Evaluating fact {clause.conclusion}: {result}")
            return result

        premises_true = all(model[premise.name] for premise in clause.premises)
        result = (not premises_true) or model[clause.conclusion.name]
        self.logger.debug(
            f"Evaluating clause {clause}: premises={premises_true}, result={result}")
        return result
