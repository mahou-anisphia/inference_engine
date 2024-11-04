# /data/knowledge_base.py
from dataclasses import dataclass
from typing import List, Set


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


@dataclass
class Clause:
    """
    Represents a Horn clause in the knowledge base

    A Horn clause is either:
    1. A fact (empty premises, just a conclusion)
    2. An implication (premises => conclusion)

    Attributes:
        premises (List[Literal]): List of literals in the antecedent
        conclusion (Literal): The consequent literal
    """
    premises: List[Literal]
    conclusion: Literal

    def __post_init__(self):
        if not isinstance(self.premises, list):
            raise InvalidClauseError("Premises must be a list")
        if not isinstance(self.conclusion, Literal):
            raise InvalidClauseError("Conclusion must be a Literal")
        if any(not isinstance(p, Literal) for p in self.premises):
            raise InvalidClauseError("All premises must be Literals")

    def __str__(self):
        if not self.premises:  # It's a fact
            return str(self.conclusion)
        return f"{' & '.join(str(p) for p in self.premises)} => {self.conclusion}"


class KnowledgeBase:
    """
    Stores and manages the knowledge base containing Horn clauses

    Attributes:
        clauses (List[Clause]): List of all clauses in the knowledge base
        facts (Set[str]): Set of known facts (clauses with no premises)
        symbols (Set[str]): Set of all unique symbols used in the knowledge base
    """

    def __init__(self):
        self.clauses: List[Clause] = []
        self.facts: Set[str] = set()
        self.symbols: Set[str] = set()

    def add_clause(self, clause: Clause) -> None:
        """
        Adds a new clause to the knowledge base and updates facts and symbols sets

        Args:
            clause (Clause): The clause to add

        Raises:
            InvalidClauseError: If the clause is invalid or contains invalid symbols
        """
        try:
            if not isinstance(clause, Clause):
                raise InvalidClauseError("Must provide a valid Clause object")

            self.clauses.append(clause)
            self.symbols.add(clause.conclusion.name)

            if not clause.premises:  # If it's a fact
                if clause.conclusion.negative:
                    raise InvalidClauseError(
                        "Facts cannot be negative literals")
                self.facts.add(clause.conclusion.name)

            for premise in clause.premises:
                self.symbols.add(premise.name)

        except Exception as e:
            raise InvalidClauseError(f"Error adding clause: {str(e)}")
