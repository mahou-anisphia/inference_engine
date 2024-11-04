# /data/input_parser.py
from pathlib import Path
from data.knowledge_base import KnowledgeBase, Clause, Literal, KnowledgeBaseError


class InputParserError(Exception):
    """Base exception class for InputParser related errors"""
    pass


class FileFormatError(InputParserError):
    """Raised when the input file format is invalid"""
    pass


class InputParser:
    """Handles parsing of input files into a knowledge base and query"""

    @staticmethod
    def parse_file(filename: str) -> tuple[KnowledgeBase, str]:
        """
        Parses an input file into a knowledge base and query

        Format:
        TELL
        [Horn clauses separated by semicolons]
        ASK
        [query]

        Args:
            filename (str): Path to the input file

        Returns:
            tuple[KnowledgeBase, str]: The parsed knowledge base and query

        Raises:
            FileFormatError: If file format is invalid
            FileNotFoundError: If file doesn't exist
            InputParserError: For other parsing errors
            KnowledgeBaseError: If knowledge base construction fails
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
                    clauses = tell_content.split(';')

                    for clause in clauses:
                        clause = clause.strip()
                        if not clause:
                            continue

                        try:
                            # Parse single fact
                            if '=>' not in clause:
                                if any(op in clause for op in ['&', '||', '<=>']):
                                    raise FileFormatError(
                                        f"Non-Horn clause detected: {clause}")
                                kb.add_clause(
                                    Clause([], Literal(clause.strip())))
                                continue

                            # Parse implication
                            parts = clause.split('=>')
                            if len(parts) != 2:
                                raise FileFormatError(
                                    f"Invalid clause format: {clause}")

                            premises_str, conclusion_str = parts[0].strip(
                            ), parts[1].strip()

                            # Parse premises
                            premises = []
                            if '&' in premises_str:
                                premise_parts = premises_str.split('&')
                                premises = [Literal(p.strip())
                                            for p in premise_parts]
                            else:
                                premises = [Literal(premises_str)]

                            # Parse conclusion
                            conclusion = Literal(conclusion_str)

                            kb.add_clause(Clause(premises, conclusion))

                        except KnowledgeBaseError as e:
                            raise InputParserError(
                                f"Error in clause '{clause}': {str(e)}")

                # Validate and parse ASK section
                query = ask_section.strip()
                if not query:
                    raise FileFormatError("ASK section cannot be empty")
                if any(op in query for op in ['&', '=>', '||', '<=>']):
                    raise FileFormatError(
                        f"Query must be a single proposition: {query}")

                # Validate query is a symbol in the knowledge base
                if query not in kb.symbols:
                    raise InputParserError(
                        f"Query symbol '{query}' not found in knowledge base")

                return kb, query

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error reading file: {str(e)}")
        except FileFormatError as e:
            raise FileFormatError(f"Invalid file format: {str(e)}")
        except KnowledgeBaseError as e:
            raise KnowledgeBaseError(f"Knowledge base error: {str(e)}")
        except Exception as e:
            raise InputParserError(f"Error parsing input: {str(e)}")
