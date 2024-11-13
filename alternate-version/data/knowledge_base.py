# /data/knowledge_base.py
from dataclasses import dataclass
from typing import List, Set, Union
from enum import Enum

class LogicalOperator(Enum):
    """Represents supported logical operators"""
    AND = '&'       # Conjunction (∧)
    OR = '||'       # Disjunction (∨)
    IMPLIES = '=>'  # Implication (⇒)
    BICON = '<=>'   # Biconditional (⇔)
    NOT = '~'       # Negation (¬)

class KnowledgeBaseError(Exception):
    """Base exception class for KnowledgeBase related errors"""
    pass

class InvalidLiteralError(KnowledgeBaseError):
    """Raised when an invalid literal is provided"""
    pass

class InvalidClauseError(KnowledgeBaseError):
    """Raised when an invalid clause is provided"""
    pass

@dataclass
class Literal:
    """
    Represents a propositional logic literal (e.g., 'p' or '~p')

    Attributes:
        name (str): The symbol name (e.g., 'p', 'q')
        negative (bool): True if this is a negated literal (e.g., '~p')
    """
    name: str
    negative: bool = False

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise InvalidLiteralError("Literal name must be a string")
        if not self.name.strip():
            raise InvalidLiteralError("Literal name cannot be empty")
        if not all(c.isalnum() or c == '_' for c in self.name):
            raise InvalidLiteralError(
                f"Invalid literal name '{self.name}'. Only alphanumeric characters and underscores are allowed.")

    def __str__(self):
        return f"{'~' if self.negative else ''}{self.name}"

    def negate(self):
        """Returns a new literal with opposite polarity"""
        return Literal(self.name, not self.negative)

@dataclass
class Expression:
    """
    Represents a logical expression that can contain multiple literals and operators

    Attributes:
        operator (LogicalOperator): The main logical operator of this expression
        operands (List[Union[Literal, 'Expression']]): The operands (can be literals or nested expressions)
    """
    operator: LogicalOperator
    operands: List[Union[Literal, 'Expression']]

    def __str__(self):
        if self.operator == LogicalOperator.NOT:
            return f"~{self.operands[0]}"
        return f" {self.operator.value} ".join(str(op) for op in self.operands)

@dataclass
class Clause:
    """
    Represents a general logical clause that can contain complex expressions

    Attributes:
        expression (Union[Literal, Expression]): The logical expression
    """
    expression: Union[Literal, Expression]

    def is_horn(self) -> bool:
        """Checks if this is a Horn clause"""
        def count_positive_literals(expr) -> int:
            if isinstance(expr, Literal):
                return 0 if expr.negative else 1
            if isinstance(expr, Expression):
                if expr.operator == LogicalOperator.IMPLIES:
                    # For implications, only count positives in conclusion
                    return count_positive_literals(expr.operands[-1])
                return sum(count_positive_literals(op) for op in expr.operands)
            return 0

        return count_positive_literals(self.expression) <= 1

    def get_symbols(self) -> Set[str]:
        """Returns all symbols used in this clause"""
        symbols = set()

        def collect_symbols(expr):
            if isinstance(expr, Literal):
                symbols.add(expr.name)
            elif isinstance(expr, Expression):
                for op in expr.operands:
                    collect_symbols(op)

        collect_symbols(self.expression)
        return symbols

    def __str__(self):
        return str(self.expression)

class KnowledgeBase:
    """
    Stores and manages the knowledge base containing logical clauses

    Attributes:
        clauses (List[Clause]): List of all clauses in the knowledge base
        facts (Set[str]): Set of known facts (atomic propositions)
        symbols (Set[str]): Set of all unique symbols used
        horn_only (bool): Whether to restrict to Horn clauses only
    """
    def __init__(self, horn_only: bool = False):
        self.clauses: List[Clause] = []
        self.facts: Set[str] = set()
        self.symbols: Set[str] = set()
        self.horn_only = horn_only

    def add_clause(self, clause: Clause) -> None:
        """
        Adds a new clause to the knowledge base

        Args:
            clause (Clause): The clause to add

        Raises:
            InvalidClauseError: If the clause is invalid or violates Horn restriction
        """
        if self.horn_only and not clause.is_horn():
            raise InvalidClauseError("Only Horn clauses are allowed in this knowledge base")

        # Extract atomic facts (single positive literals)
        if isinstance(clause.expression, Literal) and not clause.expression.negative:
            self.facts.add(clause.expression.name)

        # Update symbols
        self.symbols.update(clause.get_symbols())

        self.clauses.append(clause)

    def __str__(self):
        return "\n".join(str(clause) for clause in self.clauses)
