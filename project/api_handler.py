import os
import json
import time
from config import Config
try:
    import anthropic
except ImportError:
    anthropic = None
try:
    import openai
except ImportError:
    openai = None
try:
    import google.generativeai as genai
except ImportError:
    genai = None
try:
    from groq import Groq
except ImportError:
    Groq = None

class APIHandler:
    def __init__(self):
        self.claude_client = None
        self.openai_client = None
        self.gemini_configured = False
        
        # Initialize clients if keys are present
        # Note: Claude support removed - using Groq as primary model
            
        if Config.OPENAI_API_KEY and openai:
            self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            
        if Config.GEMINI_API_KEY and genai:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.gemini_configured = True

    def generate_response(self, prompt, model_service="claude", system_prompt=""):
        """
        Generates a response from the specified model service.
        Returns a tuple: (response_text, input_tokens, output_tokens, error_msg)
        """
        response_text = ""
        input_tokens = 0
        output_tokens = 0
        error_msg = None

        try:
            if model_service == "claude":
                # Fallback to Groq for Claude requests (keeping compatibility)
                if not Groq or not Config.GROQ_API_KEY:
                    return "", 0, 0, "Claude not available and Groq API key missing."
                
                if not getattr(self, 'groq_client', None):
                    self.groq_client = Groq(api_key=Config.GROQ_API_KEY)

                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model=Config.GROQ_MODEL_NAME,
                    max_tokens=Config.MAX_TOKENS,
                )
                response_text = chat_completion.choices[0].message.content
                input_tokens = chat_completion.usage.prompt_tokens
                output_tokens = chat_completion.usage.completion_tokens

            elif model_service == "groq":
                if not Groq or not Config.GROQ_API_KEY:
                    return "", 0, 0, "Groq API key missing or SDK not installed."
                
                if not getattr(self, 'groq_client', None):
                    self.groq_client = Groq(api_key=Config.GROQ_API_KEY)

                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model=Config.GROQ_MODEL_NAME,
                    max_tokens=Config.MAX_TOKENS,
                )
                response_text = chat_completion.choices[0].message.content
                input_tokens = chat_completion.usage.prompt_tokens
                output_tokens = chat_completion.usage.completion_tokens

            elif model_service == "openai":
                if not self.openai_client:
                    return "", 0, 0, "OpenAI API key missing or SDK not installed."
                
                # OpenAI API call
                response = self.openai_client.chat.completions.create(
                    model=Config.OPENAI_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=Config.MAX_TOKENS
                )
                response_text = response.choices[0].message.content
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens

            elif model_service == "gemini":
                if not self.gemini_configured:
                    return "", 0, 0, "Gemini API key missing or SDK not installed."
                
                # Gemini API call
                model = genai.GenerativeModel(Config.GEMINI_MODEL_NAME)
                # Gemini system instruction is set at model init or via specific call params in newer SDKs, 
                # but for simplicity we can prepend it to the prompt or use the 'system_instruction' arg if supported.
                # simpler approach:
                full_prompt = f"System: {system_prompt}\nUser: {prompt}"
                response = model.generate_content(full_prompt)
                
                response_text = response.text
                # Usage metadata is available in response.usage_metadata
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count

            elif model_service == "mock":
                # Mock response logic
                import random
                products_snippet = system_prompt # Contains product data in the system prompt
                
                # Simple keyword matching to make it feel somewhat real
                lower_p = prompt.lower()
                response_text = "I'm sorry, I'm just a simulation. "
                
                if "brand" in lower_p:
                    response_text = "We have several great brands like Lira Luxe, PureBasics, and EyeCatch. Each offers unique products for different skin needs."
                elif "price" in lower_p or "cost" in lower_p or "how much" in lower_p:
                    response_text = "Our products range from $14 to $55. For example, the Hydra Glow Serum is $45, while our Velvet Lip Liner is $14."
                elif "skin" in lower_p:
                    response_text = "We have products for all skin types including Dry, Oily, Sensitive, and Mature. The Hydra Glow Serum is excellent for Dry skin."
                elif "ingredient" in lower_p:
                    response_text = "Our products use high-quality ingredients like Hyaluronic Acid, Vitamin C, and Aloe Vera to ensure the best results."
                else:
                    response_text = "That's a great question about Lira Cosmetics! I recommend checking our product catalog for more details on our range."
                
                input_tokens = len(prompt.split()) # Rough estimate
                output_tokens = len(response_text.split())

            else:
                error_msg = f"Unknown model service: {model_service}"

        except Exception as e:
            error_msg = str(e)

        return response_text, input_tokens, output_tokens, error_msg
