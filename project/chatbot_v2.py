import json
import time
from collections import deque
from typing import Dict, Any, Tuple
from config import Config
from api_handler import APIHandler
from cost_calculator import CostCalculator
from token_tracker import TokenTracker

class Session:
    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.history = deque(maxlen=3) # Store last 3 exchanges
        self.total_cost = 0.0
        self.total_tokens = 0
        self.query_count = 0
        self.start_time = time.time()
        self.logs = []

    def add_interaction(self, query, response, cost, input_tok, output_tok):
        self.history.append({"role": "user", "content": query})
        self.history.append({"role": "assistant", "content": response})
        self.total_cost += cost
        self.total_tokens += (input_tok + output_tok)
        self.query_count += 1
        
        self.logs.append({
            "timestamp": time.time(),
            "query": query,
            "response": response,
            "cost": cost,
            "input_tokens": input_tok,
            "output_tokens": output_tok
        })

class Chatbot:
    """
    Core Chatbot logic class.
    
    Manages customer sessions, product data, and interactions with the LLM API.
    Calculates costs and tracks token usage via TokenTracker.
    """
    
    def __init__(self) -> None:
        """Initialize the Chatbot, load products, and setup components."""
        self.api_handler = APIHandler()
        self.cost_calculator = CostCalculator()
        self.token_tracker = TokenTracker()
        
        # Simplified loading
        self.products = []
        product_text = "Error loading product data."
        
        # Manually load without try-except for debugging
        if True:
            with open("products.json", "r") as f:
                self.products = json.load(f)
            product_text = json.dumps(self.products, indent=2)

        self.system_prompt = Config.SYSTEM_PROMPT.format(product_data=product_text)
        self.sessions: Dict[str, Session] = {}

    def get_session(self, customer_id: str) -> Session:
        """
        Retrieve existing session or create a new one for a customer.
        
        Args:
            customer_id (str): Unique identifier for the customer.
            
        Returns:
            Session: The customer's session object.
        """
        if customer_id not in self.sessions:
            self.sessions[customer_id] = Session(customer_id)
        return self.sessions[customer_id]

    def process_query(self, customer_id: str, query: str, model_service: str = "groq") -> Tuple[str, float]:
        """
        Process a user query, generate a response, and track usage.
        
        Args:
            customer_id (str): The customer's ID.
            query (str): The text query from the customer.
            model_service (str, optional): The LLM service to use. Defaults to "groq".
            
        Returns:
            Tuple[str, float]: The response text and the calculated cost.
        """
        session = self.get_session(customer_id)
        
        # Build context from history
        context_str = ""
        for msg in session.history:
            context_str += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
        full_prompt = f"{context_str}User: {query}"
        
        # Call API
        start_time = time.time()
        response_text, input_tok, output_tok, error = self.api_handler.generate_response(
            full_prompt, 
            model_service=model_service, 
            system_prompt=self.system_prompt
        )
        response_time = time.time() - start_time

        if error:
            return f"Error: {error}", 0.0

        # Calculate cost
        cost = self.cost_calculator.calculate_cost(model_service, input_tok, output_tok)
        
        # Log to tracker for teacher verification
        self.token_tracker.log_query(model_service, input_tok, output_tok, cost, response_time)
        
        # Update session
        session.add_interaction(query, response_text, cost, input_tok, output_tok)
        
        return response_text, cost

    def get_session_stats(self, customer_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific customer session.
        
        Args:
            customer_id (str): The customer's ID.
            
        Returns:
            Dict[str, Any]: Session stats including cost and token counts, or None.
        """
        session = self.sessions.get(customer_id)
        if not session:
            return None
        return {
            "total_cost": session.total_cost,
            "total_tokens": session.total_tokens,
            "query_count": session.query_count
        }
