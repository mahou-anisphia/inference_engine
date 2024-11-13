# /algorithms/bc.py
import logging
from typing import Union, Tuple, List, Set
from data.knowledge_base import (
    KnowledgeBase, Clause, Literal, Expression,
    LogicalOperator, KnowledgeBaseError
)


class BackwardChaining:
    """Implementation of the Backward Chaining algorithm with support for enhanced logical operators"""

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

    def convert_to_horn_clauses(self, kb: KnowledgeBase) -> KnowledgeBase:
        """
        Converts a knowledge base with complex expressions into an equivalent
        knowledge base with only Horn clauses.

        This is necessary because backward chaining requires Horn clauses.

        Args:
            kb (KnowledgeBase): Original knowledge base

        Returns:
            KnowledgeBase: Converted knowledge base with only Horn clauses
        """
        horn_kb = KnowledgeBase(horn_only=True)

        for clause in kb.clauses:
            horn_clauses = self._convert_clause_to_horn(clause)
            for horn_clause in horn_clauses:
                horn_kb.add_clause(horn_clause)

        return horn_kb

    def _convert_clause_to_horn(self, clause: Clause) -> List[Clause]:
        """
        Converts a complex clause into a list of equivalent Horn clauses

        Args:
            clause (Clause): Original clause

        Returns:
            List[Clause]: List of equivalent Horn clauses
        """
        expr = clause.expression
        horn_clauses = []

        if isinstance(expr, Literal):
            # Single literal is already in Horn form
            horn_clauses.append(Clause(expr))

        elif isinstance(expr, Expression):
            if expr.operator == LogicalOperator.IMPLIES:
                # p & q => r is already Horn if antecedent only uses AND
                if self._is_conjunctive_antecedent(expr.operands[0]):
                    premises = self._get_conjuncts(expr.operands[0])
                    conclusion = expr.operands[1]
                    horn_clauses.append(Clause(
                        Expression(LogicalOperator.IMPLIES,
                                 [Expression(LogicalOperator.AND, premises), conclusion])
                    ))

            elif expr.operator == LogicalOperator.AND:
                # Add each conjunct separately
                for operand in expr.operands:
                    if isinstance(operand, Literal):
                        horn_clauses.append(Clause(operand))
                    elif isinstance(operand, Expression) and operand.operator == LogicalOperator.IMPLIES:
                        horn_clauses.extend(self._convert_clause_to_horn(Clause(operand)))

            elif expr.operator == LogicalOperator.BICON:
                # p <=> q becomes p => q and q => p
                left, right = expr.operands
                horn_clauses.extend(self._convert_clause_to_horn(Clause(
                    Expression(LogicalOperator.IMPLIES, [left, right])
                )))
                horn_clauses.extend(self._convert_clause_to_horn(Clause(
                    Expression(LogicalOperator.IMPLIES, [right, left])
                )))

            elif expr.operator == LogicalOperator.OR:
                # Convert OR to implication: p || q => ~p => q
                for i, operand in enumerate(expr.operands):
                    other_operands = expr.operands[:i] + expr.operands[i+1:]
                    for other in other_operands:
                        negated = Expression(LogicalOperator.NOT, [other])
                        horn_clauses.extend(self._convert_clause_to_horn(Clause(
                            Expression(LogicalOperator.IMPLIES, [negated, operand])
                        )))

        return horn_clauses

    def _is_conjunctive_antecedent(self, expr: Union[Literal, Expression]) -> bool:
        """Checks if an expression contains only conjunctions and literals"""
        if isinstance(expr, Literal):
            return True
        if isinstance(expr, Expression):
            if expr.operator == LogicalOperator.AND:
                return all(self._is_conjunctive_antecedent(op) for op in expr.operands)
        return False

    def _get_conjuncts(self, expr: Union[Literal, Expression]) -> List[Literal]:
        """Gets all conjuncts from a conjunctive expression"""
        if isinstance(expr, Literal):
            return [expr]
        if isinstance(expr, Expression) and expr.operator == LogicalOperator.AND:
            result = []
            for op in expr.operands:
                result.extend(self._get_conjuncts(op))
            return result
        return []

    def check_entailment(self, kb: KnowledgeBase, query: str) -> tuple[bool, list[str]]:
        """
        Checks if KB entails query using backward chaining

        First converts the KB to Horn clauses, then applies backward chaining.

        Args:
            kb (KnowledgeBase): The knowledge base
            query (str): The query to check

        Returns:
            tuple[bool, list[str]]: (Whether KB entails query,
                                    List of symbols used in proof)
        """
        self.logger.info(f"Starting Backward Chaining for query: {query}")

        # Convert to Horn clauses if needed
        if not all(clause.is_horn() for clause in kb.clauses):
            self.logger.info("Converting knowledge base to Horn clauses")
            kb = self.convert_to_horn_clauses(kb)

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
            self.indent_level += 1
            for clause in kb.clauses:
                if isinstance(clause.expression, Expression) and \
                   clause.expression.operator == LogicalOperator.IMPLIES and \
                   isinstance(clause.expression.operands[-1], Literal) and \
                   clause.expression.operands[-1].name == goal and \
                   not clause.expression.operands[-1].negative:

                    self.logger.debug(f"{indent}Trying rule: {clause}")

                    # Get premises from the antecedent
                    premises = self._get_conjuncts(clause.expression.operands[0])

                    if bc_and(premises):
                        inferred.add(goal)
                        goals.remove(goal)
                        self.logger.debug(f"{indent}Successfully proved {goal}")
                        self.indent_level -= 1
                        return True

            self.indent_level -= 1
            goals.remove(goal)
            self.logger.debug(f"{indent}Failed to prove {goal}")
            return False

        def bc_and(premises: List[Literal]) -> bool:
            """
            Tries to prove all premises using AND strategy
            (all premises must be true)
            """
            indent = "  " * self.indent_level
            self.logger.debug(
                f"{indent}Attempting to prove premises: {[str(p) for p in premises]}")

            for premise in premises:
                # Handle negation by checking if we can't prove the positive literal
                if premise.negative:
                    if bc_or(premise.name):
                        self.logger.debug(
                            f"{indent}Failed because negated premise {premise} was proven")
                        return False
                else:
                    if not bc_or(premise.name):
                        self.logger.debug(
                            f"{indent}Failed to prove premise: {premise}")
                        return False

            self.logger.debug(f"{indent}Successfully proved all premises")
            return True

        # Parse query into a Literal if it's a string
        query_literal = query if isinstance(query, Literal) else \
                       Literal(query) if '~' not in query else \
                       Literal(query[1:], negative=True)

        # Handle negative query
        if query_literal.negative:
            result = not bc_or(query_literal.name)
        else:
            result = bc_or(query_literal.name)

        self.logger.info(f"Query {'is' if result else 'is not'} entailed")
        self.logger.debug(f"Symbols used in proof: {inferred}")
        return result, list(inferred)
