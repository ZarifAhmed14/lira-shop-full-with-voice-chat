from datetime import datetime
import os

class TokenTracker:
    """Track and calculate accurate token averages across all queries."""
    
    def __init__(self):
        self.query_logs = []
    
    def log_query(self, model: str, input_tokens: int, output_tokens: int, 
                  cost: float, response_time: float):
        """Log each individual query with ACTUAL token counts."""
        self.query_logs.append({
            "model": model,
            "input_tokens": input_tokens,    # From API response
            "output_tokens": output_tokens,  # From API response
            "cost": cost,
            "response_time": response_time,
            "timestamp": datetime.now()
        })
        
        # Also append to a persistent verification file immediately
        self._append_to_verification_log(model, input_tokens, output_tokens, cost)
    
    def _append_to_verification_log(self, model, input_tok, output_tok, cost):
        os.makedirs("logs", exist_ok=True)
        filename = f"logs/verification_{model}.txt"
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] In: {input_tok} | Out: {output_tok} | Cost: ${cost:.8f}\n")

    def get_averages(self, model: str) -> dict:
        """
        Calculate averages using ONLY actual measured values.
        """
        model_queries = [q for q in self.query_logs if q["model"] == model]
        
        if not model_queries:
            # Return zeros if no queries yet to avoid divide by zero
            return {
                "total_queries": 0,
                "avg_input_tokens": 0,
                "avg_output_tokens": 0,
                "avg_cost_per_query": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost": 0
            }
        
        total_queries = len(model_queries)
        total_input = sum(q["input_tokens"] for q in model_queries)
        total_output = sum(q["output_tokens"] for q in model_queries)
        total_cost = sum(q["cost"] for q in model_queries)
        
        return {
            "total_queries": total_queries,
            "avg_input_tokens": round(total_input / total_queries, 2),
            "avg_output_tokens": round(total_output / total_queries, 2),
            "avg_cost_per_query": round(total_cost / total_queries, 8),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_cost": round(total_cost, 6)
        }
