import unittest
from pathlib import Path
from data.input_parser import InputParser, FileFormatError
from data.knowledge_base import KnowledgeBase, Clause, Literal, KnowledgeBaseError
from algorithms.fc import ForwardChaining
from algorithms.bc import BackwardChaining
from algorithms.tt import TruthTable


class TestLogicEngine(unittest.TestCase):
    def setUp(self):
        self.test_files_dir = Path("test_files")
        self.test_files_dir.mkdir(exist_ok=True)

    def create_test_file(self, content: str) -> Path:
        file_path = self.test_files_dir / "test_input.txt"
        file_path.write_text(content)
        return file_path

    def test_input_parser_valid_file(self):
        content = """TELL
        p2 => p3; p3 => p1; p1 => p2; p2
        ASK
        p1"""
        file_path = self.create_test_file(content)
        kb, query = InputParser.parse_file(str(file_path))
        self.assertEqual(len(kb.clauses), 4)
        self.assertEqual(query, "p1")

    def test_input_parser_invalid_format(self):
        content = """TELL p1 => p2
        p2"""
        file_path = self.create_test_file(content)
        with self.assertRaises(FileFormatError):
            InputParser.parse_file(str(file_path))

    def test_knowledge_base_construction(self):
        kb = KnowledgeBase()
        kb.add_clause(Clause([], Literal("p1")))
        kb.add_clause(Clause([Literal("p1")], Literal("p2")))
        self.assertEqual(len(kb.clauses), 2)
        self.assertEqual(len(kb.facts), 1)
        self.assertEqual(len(kb.symbols), 2)

    def test_forward_chaining_simple(self):
        kb = KnowledgeBase()
        kb.add_clause(Clause([], Literal("p1")))
        kb.add_clause(Clause([Literal("p1")], Literal("p2")))
        entailed, order = ForwardChaining.check_entailment(kb, "p2")
        self.assertTrue(entailed)
        self.assertEqual(order, ["p1", "p2"])

    def test_backward_chaining_simple(self):
        kb = KnowledgeBase()
        kb.add_clause(Clause([], Literal("p1")))
        kb.add_clause(Clause([Literal("p1")], Literal("p2")))
        entailed, order = BackwardChaining.check_entailment(kb, "p2")
        self.assertTrue(entailed)
        self.assertEqual(order, ["p1", "p2"])

    def test_truth_table_simple(self):
        kb = KnowledgeBase()
        kb.add_clause(Clause([], Literal("p1")))
        kb.add_clause(Clause([Literal("p1")], Literal("p2")))
        entailed, models = TruthTable.check_entailment(kb, "p2")
        self.assertTrue(entailed)
        self.assertEqual(models, 1)

    def test_algorithm_consistency(self):
        kb = KnowledgeBase()
        kb.add_clause(Clause([], Literal("p1")))
        kb.add_clause(Clause([Literal("p1")], Literal("p2")))
        kb.add_clause(Clause([Literal("p2")], Literal("p3")))

        fc_result, _ = ForwardChaining.check_entailment(kb, "p3")
        bc_result, _ = BackwardChaining.check_entailment(kb, "p3")
        tt_result, _ = TruthTable.check_entailment(kb, "p3")

        self.assertEqual(fc_result, bc_result)
        self.assertEqual(bc_result, tt_result)

    def test_complex_inference(self):
        kb = KnowledgeBase()
        kb.add_clause(Clause([], Literal("p1")))
        kb.add_clause(Clause([Literal("p1"), Literal("p2")], Literal("p3")))
        kb.add_clause(Clause([Literal("p3")], Literal("p4")))
        kb.add_clause(Clause([], Literal("p2")))

        self.assertTrue(ForwardChaining.check_entailment(kb, "p4")[0])
        self.assertTrue(BackwardChaining.check_entailment(kb, "p4")[0])
        self.assertTrue(TruthTable.check_entailment(kb, "p4")[0])

    def tearDown(self):
        for file in self.test_files_dir.iterdir():
            file.unlink()
        self.test_files_dir.rmdir()


if __name__ == '__main__':
    unittest.main()
