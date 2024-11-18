# algorithms/fc.py
from typing import Tuple, Set, List, Dict
from data.knowledge_base import KnowledgeBase, Clause, Literal, Expression, LogicalOperator, InvalidClauseError


class ForwardChaining:
    """
    Implements the Forward Chaining algorithm for Horn clauses
    """

    def __init__(self):
        self.inferred: Set[str] = set()  # Set of inferred symbols
        self.agenda: Set[str] = set()    # Set of symbols to process
        # Maps symbols to clauses where they appear in premise
        self.implications: Dict[str, List[Clause]] = {}

    def _process_clause(self, clause: Clause) -> Tuple[Set[str], str]:
        """
        Processes a clause to extract premises and conclusion

        Returns:
            Tuple[Set[str], str]: (premises, conclusion)
        """
        premises = set()
        conclusion = None

        def extract_elements(expr):
            nonlocal conclusion

            if isinstance(expr, Literal):
                if not expr.negative:
                    conclusion = expr.name
                return

            if isinstance(expr, Expression):
                if expr.operator == LogicalOperator.IMPLIES:
                    # Process antecedent (left side)
                    antecedent = expr.operands[0]
                    if isinstance(antecedent, Literal):
                        if not antecedent.negative:
                            premises.add(antecedent.name)
                    elif isinstance(antecedent, Expression) and antecedent.operator == LogicalOperator.AND:
                        for op in antecedent.operands:
                            if isinstance(op, Literal) and not op.negative:
                                premises.add(op.name)

                    # Process consequent (right side)
                    consequent = expr.operands[1]
                    if isinstance(consequent, Literal) and not consequent.negative:
                        conclusion = consequent.name
                else:
                    # Handle single positive literal
                    if expr.operator == LogicalOperator.NOT:
                        return
                    for op in expr.operands:
                        if isinstance(op, Literal) and not op.negative:
                            conclusion = op.name

        extract_elements(clause.expression)
        return premises, conclusion

    def check_entailment(self, kb: KnowledgeBase, query: str) -> Tuple[bool, List[str]]:
        """
        Determines if KB entails query using forward chaining

        Args:
            kb (KnowledgeBase): The knowledge base containing Horn clauses
            query (str): The query to check

        Returns:
            Tuple[bool, List[str]]: (True if entailed, list of inferred symbols in order)
        """
        # Enable Horn-only mode
        kb.horn_only = True

        # Initialize data structures
        self.inferred.clear()
        self.agenda.clear()
        self.implications.clear()

        # Count number of premises for each clause
        count = {}  # Maps clause index to number of unfulfilled premises

        # Process each clause
        for i, clause in enumerate(kb.clauses):
            if not clause.is_horn():
                raise InvalidClauseError(
                    f"Clause {clause} is not a Horn clause")

            premises, conclusion = self._process_clause(clause)

            if not premises:  # Fact
                self.agenda.add(conclusion)
            else:  # Implication
                count[i] = len(premises)
                # Index the clause by each premise
                for premise in premises:
                    if premise not in self.implications:
                        self.implications[premise] = []
                    self.implications[premise].append(
                        (i, premises, conclusion))

        # Track inference order
        inference_order = []

        # Main forward chaining loop
        while self.agenda:
            p = self.agenda.pop()
            if p not in self.inferred:
                self.inferred.add(p)
                inference_order.append(p)

                # Check all implications where p appears in premise
                if p in self.implications:
                    for clause_idx, premises, conclusion in self.implications[p]:
                        count[clause_idx] -= 1
                        if count[clause_idx] == 0 and conclusion not in self.inferred:
                            self.agenda.add(conclusion)

        return query in self.inferred, inference_order
