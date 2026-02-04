import json
import time
import re
import os
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
        
        # Simplified loading with error handling
        self.products = []
        product_text = "Error loading product data."
        
        # Load products with proper error handling (prefer Supabase if configured)
        try:
            self.products = self._load_products()
            product_text = json.dumps(self.products, indent=2)
        except Exception as e:
            print(f"Warning: Error loading products: {e}")
            # Fallback to local products.json
            try:
                with open("products.json", "r") as f:
                    self.products = json.load(f)
                product_text = json.dumps(self.products, indent=2)
            except FileNotFoundError:
                print("Warning: products.json not found")
            except json.JSONDecodeError:
                print("Warning: Invalid JSON in products.json")
            except Exception as e2:
                print(f"Warning: Error loading products: {e2}")

        self.system_prompt = Config.SYSTEM_PROMPT.format(product_data=product_text)
        self.sessions: Dict[str, Session] = {}
        
        # Session cleanup timer (24 hours)
        self.last_cleanup = time.time()

    def _load_products(self):
        """Load products from Supabase if configured; otherwise return local list."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = (
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
            or os.getenv("SUPABASE_KEY")
        )

        if supabase_url and supabase_key:
            try:
                import requests
                headers = {
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}",
                }
                resp = requests.get(
                    f"{supabase_url}/rest/v1/products?select=*",
                    headers=headers,
                    timeout=10,
                )
                if resp.ok:
                    data = resp.json()
                    if isinstance(data, list) and data:
                        return data
            except Exception as e:
                print(f"Warning: Supabase fetch failed: {e}")

        raise RuntimeError("Supabase not configured")
    
    def _cleanup_old_sessions(self):
        """Clean up sessions older than 24 hours to prevent memory leaks."""
        current_time = time.time()
        if current_time - self.last_cleanup < 86400:  # 24 hours
            return
            
        expired_sessions = []
        for customer_id, session in self.sessions.items():
            if current_time - session.start_time > 86400:
                expired_sessions.append(customer_id)
        
        for customer_id in expired_sessions:
            del self.sessions[customer_id]
            
        self.last_cleanup = current_time

    def get_session(self, customer_id: str) -> Session:
        """
        Retrieve existing session or create a new one for a customer.
        
        Args:
            customer_id (str): Unique identifier for the customer.
            
        Returns:
            Session: The customer's session object.
        """
        # Clean up old sessions periodically
        self._cleanup_old_sessions()
        
        if customer_id not in self.sessions:
            self.sessions[customer_id] = Session(customer_id)
        return self.sessions[customer_id]


    def _limit_sentences(self, text: str, max_sentences: int = 4, language: str | None = None) -> str:
        """Trim response to a maximum number of sentences without cutting mid-sentence."""
        if not text:
            return text
        # Normalize whitespace to keep sentence splitting predictable
        cleaned = " ".join(str(text).strip().split())
        parts = re.split(r'(?<=[.!?।])\s+', cleaned)
        if len(parts) <= max_sentences:
            return cleaned
        trimmed = " ".join(parts[:max_sentences]).strip()
        # If we don't end with sentence punctuation, drop the last partial sentence
        if not re.search(r'[.!?।]\s*$', trimmed):
            trimmed = re.sub(r'[^.!?।]*$', '', trimmed).strip()
        final_text = trimmed or cleaned
        # Ensure we end with sentence punctuation to avoid mid-sentence feel
        if not re.search(r'[.!?।]\s*$', final_text):
            final_text = final_text + ("।" if language == "bn" else ".")
        return final_text

    def process_query(self, customer_id: str, query: str, model_service: str = "groq", ui_language: str | None = None) -> Tuple[str, float]:
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
        system_prompt = self.system_prompt
        if ui_language == "bn":
            system_prompt = system_prompt + (
                "\nIMPORTANT: The user may speak Bangla. "
                "Translate the user's input to English internally for reasoning, "
                "but respond in Bangla (বাংলা) for the user. "
                "Keep responses very short (1-2 sentences) and to the point.\n"
            )
        else:
            # English UI: always respond in English, translate non-English input internally if needed
            if any('\u0980' <= ch <= '\u09ff' for ch in query):
                system_prompt = system_prompt + (
                    "\nIMPORTANT: The user's input may be Bangla. "
                    "Translate it to English internally and respond in English.\n"
                )

        response_text, input_tok, output_tok, error = self.api_handler.generate_response(
            full_prompt,
            model_service=model_service,
            system_prompt=system_prompt
        )
        response_time = time.time() - start_time

        if error:
            return f"Error: {error}", 0.0

        max_sentences = 2 if ui_language == "bn" else 4
        response_text = self._limit_sentences(response_text, max_sentences=max_sentences, language=ui_language)

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
            Dict[str, Any]: Session stats including cost and token counts.
        """
        session = self.sessions.get(customer_id)
        if not session:
            return {"total_cost": 0, "total_tokens": 0, "query_count": 0}
        return {
            "total_cost": session.total_cost,
            "total_tokens": session.total_tokens,
            "query_count": session.query_count
        }
