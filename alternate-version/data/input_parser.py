# /data/input_parser.py
from pathlib import Path
import re
from typing import Union, Tuple
from data.knowledge_base import (
    KnowledgeBase, Clause, Literal, Expression,
    LogicalOperator, KnowledgeBaseError
)

class InputParserError(Exception):
    """Base exception class for InputParser related errors"""
    pass

class FileFormatError(InputParserError):
    """Raised when the input file format is invalid"""
    pass

class InputParser:
    """Handles parsing of input files into a knowledge base and query"""

    # Operator precedence (higher number = higher precedence)
    PRECEDENCE = {
        LogicalOperator.BICON: 1,
        LogicalOperator.IMPLIES: 2,
        LogicalOperator.OR: 3,
        LogicalOperator.AND: 4,
        LogicalOperator.NOT: 5
    }

    @staticmethod
    def tokenize(expression: str) -> list:
        """
        Tokenizes a logical expression into components

        Args:
            expression (str): The logical expression to tokenize

        Returns:
            list: List of tokens (operators and operands)
        """
        # Define regex pattern for tokenization
        pattern = r'(~|\(|\)|&|\|\||=>|<=>|[a-zA-Z_][a-zA-Z0-9_]*)'
        tokens = re.findall(pattern, expression.strip())
        return [t.strip() for t in tokens if t.strip()]

    @classmethod
    def parse_expression(cls, tokens: list) -> Union[Literal, Expression]:
        """
        Parses a list of tokens into a logical expression using precedence climbing

        Args:
            tokens (list): List of tokens to parse

        Returns:
            Union[Literal, Expression]: The parsed expression
        """
        def parse_primary():
            token = tokens.pop(0)
            if token == '(':
                expr = parse_expression(0)
                if not tokens or tokens.pop(0) != ')':
                    raise InputParserError("Missing closing parenthesis")
                return expr
            elif token == '~':
                operand = parse_primary()
                return Expression(LogicalOperator.NOT, [operand])
            else:
                return Literal(token)

        def parse_expression(min_precedence: int):
            left = parse_primary()

            while tokens and any(op.value == tokens[0] for op in LogicalOperator):
                op_token = tokens[0]
                op = next(op for op in LogicalOperator if op.value == op_token)

                if cls.PRECEDENCE[op] < min_precedence:
                    break

                tokens.pop(0)  # consume operator

                # Handle right associativity for implication and biconditional
                next_precedence = cls.PRECEDENCE[op]
                if op in (LogicalOperator.IMPLIES, LogicalOperator.BICON):
                    next_precedence -= 1

                right = parse_expression(next_precedence)
                left = Expression(op, [left, right])

            return left

        return parse_expression(0)

    @classmethod
    def parse_file(cls, filename: str) -> tuple[KnowledgeBase, str]:
        """
        Parses an input file into a knowledge base and query

        Format:
        TELL
        [logical expressions separated by semicolons]
        ASK
        [query]

        Args:
            filename (str): Path to the input file

        Returns:
            tuple[KnowledgeBase, str]: The parsed knowledge base and query
        """
        try:
            file_path = Path(filename)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {filename}")

            with open(file_path, 'r') as file:
                content = file.read().strip()

                # Split into TELL and ASK sections
                tell_ask = content.split('ASK')
                if len(tell_ask) != 2:
                    raise FileFormatError(
                        "File must contain exactly one TELL and one ASK section")

                tell_section = tell_ask[0].strip()
                ask_section = tell_ask[1].strip()

                # Validate TELL section
                if not tell_section.startswith('TELL'):
                    raise FileFormatError("File must start with TELL")

                # Parse TELL section
                kb = KnowledgeBase()
                tell_content = tell_section[4:].strip()

                if tell_content:  # Only process if there's content
                    expressions = tell_content.split(';')

                    for expr in expressions:
                        expr = expr.strip()
                        if not expr:
                            continue

                        # Tokenize and parse the expression
                        tokens = cls.tokenize(expr)
                        parsed_expr = cls.parse_expression(tokens)

                        # Add to knowledge base
                        kb.add_clause(Clause(parsed_expr))

                # Parse and validate query
                query = ask_section.strip()
                if not query:
                    raise FileFormatError("ASK section cannot be empty")

                # Parse query as expression
                query_tokens = cls.tokenize(query)
                query_expr = cls.parse_expression(query_tokens)

                # Convert to string representation
                query_str = str(query_expr)

                return kb, query_str

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error reading file: {str(e)}")
        except FileFormatError as e:
            raise FileFormatError(f"Invalid file format: {str(e)}")
        except KnowledgeBaseError as e:
            raise KnowledgeBaseError(f"Knowledge base error: {str(e)}")
        except Exception as e:
            raise InputParserError(f"Error parsing input: {str(e)}")
