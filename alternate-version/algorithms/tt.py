# /algorithms/tt.py
import logging
from itertools import product
from typing import Union, Tuple
from data.knowledge_base import (
    KnowledgeBase, Clause, Literal, Expression,
    LogicalOperator
)


class TruthTable:
    """Implementation of the Truth Table checking algorithm with support for all logical operators"""

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
        Checks if the knowledge base entails the query using truth table method.

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

        # Get all unique symbols from KB and query
        symbols = list(kb.symbols)

        # Parse query into an expression if it's not already
        query_expr = query if isinstance(query, (Literal, Expression)) else \
                    Literal(query) if '~' not in query else \
                    Expression(LogicalOperator.NOT, [Literal(query[1:])])

        self.logger.debug(f"Symbols in knowledge base: {symbols}")
        self.logger.debug(f"Query expression: {query_expr}")

        models_count = 0
        total_models = 2 ** len(symbols)
        self.logger.info(f"Checking {total_models} possible models")

        # Generate all possible truth assignments
        for values in product([False, True], repeat=len(symbols)):
            model = dict(zip(symbols, values))
            self.logger.debug(f"Checking model: {model}")

            # If KB is true in this model
            kb_value = all(self._evaluate_clause(clause, model) for clause in kb.clauses)
            if kb_value:
                models_count += 1
                self.logger.debug(f"Model {model} satisfies KB")

                # If KB is true but query is false, KB doesn't entail query
                query_value = self._evaluate_expression(query_expr, model)
                if not query_value:
                    self.logger.info(
                        f"Found counterexample model where KB is true but query is false: {model}")
                    return False, models_count

        self.logger.info(
            f"Query is entailed. KB satisfied in {models_count}/{total_models} models")
        return True, models_count

    def _evaluate_expression(self, expr: Union[Literal, Expression], model: dict) -> bool:
        """
        Recursively evaluates a logical expression under a given model

        Args:
            expr (Union[Literal, Expression]): The expression to evaluate
            model (dict): The truth assignment to evaluate under

        Returns:
            bool: The truth value of the expression under the model
        """
        if isinstance(expr, Literal):
            value = model[expr.name]
            return not value if expr.negative else value

        if not isinstance(expr, Expression):
            raise ValueError(f"Unknown expression type: {type(expr)}")

        if expr.operator == LogicalOperator.NOT:
            return not self._evaluate_expression(expr.operands[0], model)

        elif expr.operator == LogicalOperator.AND:
            return all(self._evaluate_expression(op, model) for op in expr.operands)

        elif expr.operator == LogicalOperator.OR:
            return any(self._evaluate_expression(op, model) for op in expr.operands)

        elif expr.operator == LogicalOperator.IMPLIES:
            antecedent = all(self._evaluate_expression(op, model)
                           for op in expr.operands[:-1])  # All but last
            consequent = self._evaluate_expression(expr.operands[-1], model)  # Last operand
            return (not antecedent) or consequent

        elif expr.operator == LogicalOperator.BICON:
            if len(expr.operands) != 2:
                raise ValueError("Biconditional must have exactly two operands")
            left = self._evaluate_expression(expr.operands[0], model)
            right = self._evaluate_expression(expr.operands[1], model)
            return left == right

        raise ValueError(f"Unknown operator: {expr.operator}")

    def _evaluate_clause(self, clause: Clause, model: dict) -> bool:
        """Evaluates if a clause is true under given model"""
        return self._evaluate_expression(clause.expression, model)

    def print_truth_table(self, kb: KnowledgeBase, query: str) -> None:
        """
        Prints a complete truth table for the knowledge base and query

        Args:
            kb (KnowledgeBase): The knowledge base
            query (str): The query to check
        """
        symbols = sorted(list(kb.symbols))

        # Print header
        header = " | ".join(symbols)
        header += " || KB | Q | KB⊨Q"
        print("\n" + "=" * len(header))
        print(header)
        print("=" * len(header))

        # Parse query
        query_expr = query if isinstance(query, (Literal, Expression)) else \
                    Literal(query) if '~' not in query else \
                    Expression(LogicalOperator.NOT, [Literal(query[1:])])

        # Generate and print each row
        for values in product([False, True], repeat=len(symbols)):
            model = dict(zip(symbols, values))

            # Evaluate KB and query
            kb_value = all(self._evaluate_clause(clause, model) for clause in kb.clauses)
            query_value = self._evaluate_expression(query_expr, model)

            # Format row
            row = " | ".join("T" if v else "F" for v in values)
            row += f" || {'T' if kb_value else 'F'}"
            row += f" | {'T' if query_value else 'F'}"
            row += f" | {'T' if (not kb_value or query_value) else 'F'}"
            print(row)

        print("=" * len(header) + "\n")
