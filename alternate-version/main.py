# main.py
import logging
import sys
from data.input_parser import InputParser
from algorithms.tt import TruthTable
from algorithms.fc import ForwardChaining
from algorithms.bc import BackwardChaining
from data.knowledge_base import KnowledgeBase, InvalidClauseError


def setup_logging(level=logging.INFO):
    """Configure logging for the application"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('inference_engine.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """
    Main entry point for the inference engine

    Usage: python main.py <filename> <method>
    where method is one of: TT, FC, BC
    """
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    if len(sys.argv) != 3:
        logger.error("Invalid number of arguments")
        print("Usage: python main.py <filename> <method>")
        sys.exit(1)

    filename = sys.argv[1]
    method = sys.argv[2].upper()

    try:
        # Create knowledge base with appropriate settings
        horn_only = method in ("FC", "BC")
        kb = KnowledgeBase(horn_only=horn_only)

        # Parse input file
        logger.info(f"Parsing input file: {filename}")
        try:
            kb, query = InputParser.parse_file(filename)
            logger.info(f"Successfully parsed input file. Query: {query}")
        except InvalidClauseError as e:
            if horn_only:
                logger.error("Non-Horn clauses detected in input file")
                print(
                    "Error: Forward Chaining and Backward Chaining methods require Horn clauses only.")
                sys.exit(1)
            raise

        # Run requested inference method
        if method == "TT":
            logger.info("Using Truth Table method")
            tt = TruthTable()
            result, models = tt.check_entailment(kb, query)
            print(f"YES: {models}" if result else "NO")

        elif method == "FC":
            logger.info("Using Forward Chaining method")
            fc = ForwardChaining()
            result, inferred = fc.check_entailment(kb, query)
            print(f"YES: {', '.join(inferred)}" if result else "NO")

        elif method == "BC":
            logger.info("Using Backward Chaining method")
            bc = BackwardChaining()
            result, inferred = bc.check_entailment(kb, query)
            print(f"YES: {', '.join(inferred)}" if result else "NO")

        else:
            logger.error(f"Unknown method: {method}")
            print(f"Unknown method: {method}")
            sys.exit(1)

        logger.info("Inference completed successfully")

    except Exception as e:
        logger.error(f"Error during execution: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
