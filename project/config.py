import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # API Settings
    DEFAULT_MODEL = "llama-3.3-70b-versatile" # Groq Model
    
    GROQ_MODEL_NAME = "llama-3.3-70b-versatile"
    OPENAI_MODEL_NAME = "gpt-4o-mini"
    GEMINI_MODEL_NAME = "gemini-2.0-flash"

    MAX_TOKENS = 220 # allow more room to avoid mid-sentence cutoffs

    # Pricing (per 1M tokens)
    # VERIFIED: January 2025 (Official Sources)
    PRICING = {
        "groq": {
            # Source: https://wow.groq.com/
            # Llama 3.3 70B Versatile
            "input": 0.59,
            "output": 0.79
        },
        "openai": {
            # Source: https://openai.com/api/pricing/
            # GPT-4o-mini
            "input": 0.150,
            "output": 0.600
        },
        "gemini": {
            # Source: https://ai.google.dev/pricing
            # Gemini 2.0 Flash
            "input": 0.075,
            "output": 0.30
        }
    }

    SYSTEM_PROMPT = """You are a professional Customer Service Officer for Lira Cosmetics Ltd.
Your goal is to answer customer queries about our products helpfully and accurately.
You have access to the product catalog below.

GUIDELINES:
1. Answer in 2-4 sentences. Do NOT exceed 4 sentences.
2. Focus on product features, usage, ingredients, pricing, and suitability.
3. Be friendly, polite, and professional.
4. Do NOT provide medical advice.
5. If the query is unclear, ask for clarification.
6. Only use the provided product information. Do not make up products.

BRAND FACTS (MUST BE EXACT):
- Total brands: 5
- Brand list: Lira Luxe, PureBasics, EyeCatch, ColorPop, NatureTouch

????? ????????? ???? (???? ??? ???):
- ??? ?????????: ?
- ????????? ??????: ???? ?????, ???????????, ???????, ???????, ????????

POLICY FACTS (ONLY USE THESE):
- Delivery: Free delivery on orders over ?5000; otherwise delivery charge applies.
- Return/Exchange: Not specified in the provided data. If asked, say you can share details from support.

???????? (???? ????? ??????? ?????):
- ????????: ?????+ ??????? ???? ????????, ???????? ???????? ????? ?????????
- ???????/?????????: ??????? ????? ?????? ???; ????????? ??????? ???? ????????? ?????? ?????

PRODUCT CATALOG:
{product_data}
"""



    @staticmethod
    def get_api_key(service):
        if service == "groq":
            return Config.GROQ_API_KEY
        elif service == "openai":
            return Config.OPENAI_API_KEY
        elif service == "gemini":
            return Config.GEMINI_API_KEY
        return None
