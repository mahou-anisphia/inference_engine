from collections import deque
import logging
from typing import Union, List, Set, Tuple, Dict
from data.knowledge_base import (
    KnowledgeBase, Clause, Literal, Expression,
    LogicalOperator, KnowledgeBaseError
)


class ForwardChaining:
    """Implementation of the Forward Chaining algorithm with support for propositional logic"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def convert_to_horn_clauses(self, kb: KnowledgeBase) -> Tuple[List[Tuple[List[Literal], Literal]], Set[str], Set[str]]:
        """
        Converts knowledge base expressions into Horn clauses

        Args:
            kb (KnowledgeBase): Original knowledge base

        Returns:
            Tuple[List[Tuple[List[Literal], Literal]], Set[str], Set[str]]:
                (Horn clauses as (premises, conclusion) pairs,
                 Known true symbols,
                 Known false symbols)
        """
        horn_clauses = []
        true_symbols = set()
        false_symbols = set()

        # First pass: collect direct facts and their negations
        for clause in kb.clauses:
            if isinstance(clause.expression, Literal):
                if clause.expression.negative:
                    false_symbols.add(clause.expression.name)
                else:
                    true_symbols.add(clause.expression.name)
            elif isinstance(clause.expression, Expression) and \
                 clause.expression.operator == LogicalOperator.NOT:
                false_symbols.add(clause.expression.operands[0].name)

        self.logger.debug(f"Initial true symbols: {true_symbols}")
        self.logger.debug(f"Initial false symbols: {false_symbols}")

        # Second pass: convert expressions to Horn clauses
        for clause in kb.clauses:
            try:
                # Skip processing of direct facts/negations as we already handled them
                if isinstance(clause.expression, Literal) or \
                   (isinstance(clause.expression, Expression) and
                    clause.expression.operator == LogicalOperator.NOT):
                    continue

                horn_forms = self._convert_expression_to_horn(
                    clause.expression, true_symbols, false_symbols)

                for premises, conclusion in horn_forms:
                    if premises is not None and conclusion is not None:
                        horn_clauses.append((premises, conclusion))

            except ValueError as e:
                self.logger.warning(f"Skipping problematic clause: {clause} - {str(e)}")
                continue

        return horn_clauses, true_symbols, false_symbols

    def _convert_expression_to_horn(
        self, expr: Union[Literal, Expression],
        true_symbols: Set[str],
        false_symbols: Set[str]
    ) -> List[Tuple[List[Literal], Literal]]:
        """
        Converts a single expression into one or more Horn clauses
        """
        if isinstance(expr, Literal):
            return [([], expr)]

        if expr.operator == LogicalOperator.IMPLIES:
            if len(expr.operands) != 2:
                raise ValueError("Implication must have exactly two operands")

            antecedent = expr.operands[0]
            consequent = expr.operands[1]

            if isinstance(antecedent, Expression) and antecedent.operator == LogicalOperator.OR:
                # Handle r || i => p type expressions
                horn_forms = []
                for operand in antecedent.operands:
                    premises = []
                    if isinstance(operand, Literal):
                        if operand.name not in false_symbols:  # Only add if not known to be false
                            premises = [operand]
                            horn_forms.append((premises, consequent))
                return horn_forms
            else:
                # Regular implication
                premises = self._get_conjunctive_literals(antecedent)
                if isinstance(consequent, Literal):
                    return [(premises, consequent)]

        elif expr.operator == LogicalOperator.AND:
            premises = self._get_conjunctive_literals(expr)
            return [(premises[1:], premises[0])] if premises else []

        elif expr.operator == LogicalOperator.OR:
            # For r || i, if we know ~r, we can conclude i
            horn_forms = []
            for i, operand in enumerate(expr.operands):
                if isinstance(operand, Literal):
                    name = operand.name
                    if name in false_symbols:  # If one operand is false
                        # Other operands must be true
                        for j, other_op in enumerate(expr.operands):
                            if i != j and isinstance(other_op, Literal):
                                horn_forms.append(([], other_op))
            return horn_forms

        elif expr.operator == LogicalOperator.BICON:
            if len(expr.operands) != 2:
                raise ValueError("Biconditional must have exactly two operands")

            left = expr.operands[0]
            right = expr.operands[1]

            # Convert A <=> B to A => B and B => A
            return [
                ([left], right),
                ([right], left)
            ]

        return []

    def _get_conjunctive_literals(self, expr: Union[Literal, Expression]) -> List[Literal]:
        """Extracts positive literals from a conjunction"""
        if isinstance(expr, Literal):
            return [expr] if not expr.negative else []

        if not isinstance(expr, Expression):
            return []

        if expr.operator == LogicalOperator.AND:
            result = []
            for op in expr.operands:
                result.extend(self._get_conjunctive_literals(op))
            return result

        if expr.operator == LogicalOperator.NOT:
            return []

        return [expr] if not isinstance(expr, Expression) else []

    def check_entailment(self, kb: KnowledgeBase, query: str) -> tuple[bool, list[str]]:
        """
        Checks if KB entails query using forward chaining
        """
        self.logger.info(f"Starting Forward Chaining for query: {query}")

        # Convert KB to Horn clauses and get known true/false symbols
        horn_clauses, true_symbols, false_symbols = self.convert_to_horn_clauses(kb)
        self.logger.debug(f"Converted to Horn clauses: {horn_clauses}")
        self.logger.debug(f"True symbols: {true_symbols}")
        self.logger.debug(f"False symbols: {false_symbols}")

        # Initialize with known true facts
        agenda = deque(true_symbols)
        inferred = set(true_symbols)
        inferred_order = list(true_symbols)

        # Track remaining premises for each clause
        count = {}
        for i, (premises, conclusion) in enumerate(horn_clauses):
            # Only count premises that aren't known false
            valid_premises = [p for p in premises if p.name not in false_symbols]
            count[i] = len(valid_premises)

            # If no valid premises remain, add conclusion to agenda
            if count[i] == 0 and conclusion.name not in inferred:
                agenda.append(conclusion.name)
                inferred.add(conclusion.name)
                inferred_order.append(conclusion.name)

        self.logger.debug(f"Initial premise counts: {count}")

        # Forward chaining process
        while agenda:
            p = agenda.popleft()
            self.logger.debug(f"Processing fact: {p}")

            for i, (premises, conclusion) in enumerate(horn_clauses):
                if count[i] == 0:  # Skip if clause already triggered
                    continue

                # Check if p appears in premises and isn't known false
                for premise in premises:
                    if premise.name == p and premise.name not in false_symbols:
                        count[i] -= 1
                        self.logger.debug(
                            f"Matched premise in clause {i}, remaining premises: {count[i]}")

                        if count[i] == 0:  # All premises are satisfied
                            conclusion_name = conclusion.name
                            if conclusion_name not in inferred and \
                               conclusion_name not in false_symbols:
                                self.logger.info(f"New fact derived: {conclusion_name}")
                                agenda.append(conclusion_name)
                                inferred.add(conclusion_name)
                                inferred_order.append(conclusion_name)

        result = query in inferred
        self.logger.info(f"Query {'is' if result else 'is not'} entailed")
        self.logger.debug(f"Final inferred facts: {inferred}")
        return result, inferred_order
