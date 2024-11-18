# algorithms/bc.py
from typing import Tuple, Set, List, Dict
from data.knowledge_base import KnowledgeBase, Clause, Literal, Expression, LogicalOperator, InvalidClauseError


class BackwardChaining:
    """
    Implements the Backward Chaining algorithm for Horn clauses
    """

    def __init__(self):
        self.kb: KnowledgeBase = None
        self.inferred: Set[str] = set()
        self.implications: Dict[str, List[Tuple[Set[str], str]]] = {}

    def _process_knowledge_base(self, kb: KnowledgeBase):
        """
        Processes knowledge base to extract implications and facts
        """
        self.kb = kb
        self.implications.clear()

        # Process each clause
        for clause in kb.clauses:
            if not clause.is_horn():
                raise InvalidClauseError(
                    f"Clause {clause} is not a Horn clause")

            def process_expr(expr) -> Tuple[Set[str], str]:
                premises = set()
                conclusion = None

                if isinstance(expr, Literal):
                    if not expr.negative:
                        conclusion = expr.name
                    return premises, conclusion

                if isinstance(expr, Expression):
                    if expr.operator == LogicalOperator.IMPLIES:
                        # Process antecedent
                        antecedent = expr.operands[0]
                        if isinstance(antecedent, Literal):
                            if not antecedent.negative:
                                premises.add(antecedent.name)
                        elif isinstance(antecedent, Expression) and antecedent.operator == LogicalOperator.AND:
                            for op in antecedent.operands:
                                if isinstance(op, Literal) and not op.negative:
                                    premises.add(op.name)

                        # Process consequent
                        consequent = expr.operands[1]
                        if isinstance(consequent, Literal) and not consequent.negative:
                            conclusion = consequent.name
                    else:
                        # Handle single positive literal
                        if expr.operator == LogicalOperator.NOT:
                            return premises, conclusion
                        for op in expr.operands:
                            if isinstance(op, Literal) and not op.negative:
                                conclusion = op.name

                return premises, conclusion

            premises, conclusion = process_expr(clause.expression)

            if conclusion:
                if conclusion not in self.implications:
                    self.implications[conclusion] = []
                if not premises:  # Fact
                    self.inferred.add(conclusion)
                else:  # Implication
                    self.implications[conclusion].append(premises)

    def _bc_or(self, goal: str, visited: Set[str]) -> bool:
        """
        OR step of backward chaining - checks if any clause can prove the goal
        """
        if goal in self.inferred:
            return True

        if goal in visited:
            return False

        visited.add(goal)

        if goal in self.implications:
            for premises in self.implications[goal]:
                if self._bc_and(premises, visited):
                    self.inferred.add(goal)
                    return True

        return False

    def _bc_and(self, goals: Set[str], visited: Set[str]) -> bool:
        """
        AND step of backward chaining - checks if all premises can be proved
        """
        for goal in goals:
            if not self._bc_or(goal, visited):
                return False
        return True

    def check_entailment(self, kb: KnowledgeBase, query: str) -> Tuple[bool, List[str]]:
        """
        Determines if KB entails query using backward chaining

        Args:
            kb (KnowledgeBase): The knowledge base containing Horn clauses
            query (str): The query to check

        Returns:
            Tuple[bool, List[str]]: (True if entailed, list of inferred symbols)
        """
        # Enable Horn-only mode
        kb.horn_only = True

        # Initialize
        self.inferred.clear()
        self._process_knowledge_base(kb)

        # Run backward chaining
        result = self._bc_or(query, set())

        return result, list(self.inferred)
