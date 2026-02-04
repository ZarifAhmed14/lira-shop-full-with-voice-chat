import unittest
from cost_calculator import CostCalculator

class TestCalculations(unittest.TestCase):
    def setUp(self):
        self.calc = CostCalculator()

    def test_cost_accuracy(self):
        """Test exact cost formula with known values"""
        # Known usage
        input_tokens = 1000
        output_tokens = 500
        
        # Test Groq (0.59 / 0.79)
        # Input cost: 1000/1M * 0.59 = 0.00059
        # Output cost: 500/1M * 0.79 = 0.000395
        # Total: 0.000985
        cost = self.calc.calculate_cost("groq", input_tokens, output_tokens)
        self.assertAlmostEqual(cost, 0.000985, places=8)

    def test_daily_scaling(self):
        """Test daily cost scaling"""
        # Daily: 225 queries
        queries = 225
        avg_in = 100
        avg_out = 50
        
        results = self.calc.calculate_daily_cost(queries, avg_in, avg_out, "groq")
        
        expected_daily_input_tokens = 22500
        expected_daily_output_tokens = 11250
        
        self.assertEqual(results['daily_input_tokens'], expected_daily_input_tokens)
        self.assertEqual(results['daily_output_tokens'], expected_daily_output_tokens)
        
        # Cost check
        # In: 22500/1M * 0.59 = 0.013275
        # Out: 11250/1M * 0.79 = 0.0088875
        # Total: 0.0221625 -> round to 6: 0.022163
        self.assertAlmostEqual(results['daily_total_cost'], 0.022163, places=5)

if __name__ == '__main__':
    unittest.main()
