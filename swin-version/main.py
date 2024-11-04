# main.py
import sys
from data.input_parser import InputParser
from algorithms.tt import TruthTable
from algorithms.fc import ForwardChaining
from algorithms.bc import BackwardChaining


def main():
    """
    Main entry point for the inference engine

    Usage: python main.py <filename> <method>
    where method is one of: TT, FC, BC
    """
    if len(sys.argv) != 3:
        print("Usage: python main.py <filename> <method>")
        sys.exit(1)

    filename = sys.argv[1]
    method = sys.argv[2].upper()

    try:
        # Parse input file
        kb, query = InputParser.parse_file(filename)

        # Run requested inference method
        if method == "TT":
            result, models = TruthTable.check_entailment(kb, query)
            print(f"YES: {models}" if result else "NO")

        elif method == "FC":
            result, inferred = ForwardChaining.check_entailment(kb, query)
            print(f"YES: {', '.join(inferred)}" if result else "NO")

        elif method == "BC":
            result, inferred = BackwardChaining.check_entailment(kb, query)
            print(f"YES: {', '.join(inferred)}" if result else "NO")

        else:
            print(f"Unknown method: {method}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
