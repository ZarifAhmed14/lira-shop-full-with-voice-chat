import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cost_calculator import CostCalculator
from config import Config

class TestCostCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = CostCalculator()

    def test_calculate_cost_zero(self):
        cost = self.calc.calculate_cost("claude", 0, 0)
        self.assertEqual(cost, 0.0)

    def test_calculate_cost_claude_simple(self):
        # Claude: $3/1M input, $15/1M output
        # 1M input should be $3
        cost = self.calc.calculate_cost("claude", 1_000_000, 0)
        self.assertAlmostEqual(cost, 3.0)
        
        # 1M output should be $15
        cost = self.calc.calculate_cost("claude", 0, 1_000_000)
        self.assertAlmostEqual(cost, 15.0)

    def test_calculate_cost_openai_simple(self):
        # OpenAI: $0.15/1M input, $0.60/1M output
        cost = self.calc.calculate_cost("openai", 1_000_000, 1_000_000)
        self.assertAlmostEqual(cost, 0.75)

    def test_unknown_model(self):
        cost = self.calc.calculate_cost("unknown_model", 100, 100)
        self.assertEqual(cost, 0.0)

if __name__ == '__main__':
    unittest.main()
