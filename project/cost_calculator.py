from config import Config

class CostCalculator:
    def __init__(self):
        self.pricing = Config.PRICING
        
        # Voice Pricing
        # STT: Groq Whisper Large V3 ($0.111 per hour)
        self.stt_price_per_hour = 0.111 
        self.stt_price_per_minute = self.stt_price_per_hour / 60
        
        # TTS: Edge TTS (Free)
        self.tts_price_per_char = 0.0

    def calculate_cost(self, model_key, input_tokens, output_tokens):
        """
        Calculates the cost for a single interaction with HIGH PRECISION.
        """
        price_info = self.pricing.get(model_key.lower())
        if not price_info:
            return 0.0

        # CRITICAL: Exact formula as requested
        # Cost = (Tokens / 1,000,000) * Price_per_Million
        input_cost = (input_tokens / 1_000_000) * price_info['input']
        output_cost = (output_tokens / 1_000_000) * price_info['output']
        
        total_cost = input_cost + output_cost
        
        # Return with high precision (8 decimals) as requested for intermediate calcs
        return round(total_cost, 8)

    def calculate_daily_cost(self, queries_per_day, avg_input, avg_output, model_key):
        """
        Calculate daily cost projection based on averages.
        """
        price_info = self.pricing.get(model_key.lower())
        if not price_info: return {}

        daily_input_tokens = queries_per_day * avg_input
        daily_output_tokens = queries_per_day * avg_output
        
        daily_input_cost = (daily_input_tokens / 1_000_000) * price_info['input']
        daily_output_cost = (daily_output_tokens / 1_000_000) * price_info['output']
        daily_total_cost = daily_input_cost + daily_output_cost

        return {
            "daily_input_tokens": round(daily_input_tokens, 2),
            "daily_output_tokens": round(daily_output_tokens, 2),
            "daily_input_cost": round(daily_input_cost, 6),
            "daily_output_cost": round(daily_output_cost, 6),
            "daily_total_cost": round(daily_total_cost, 6)
        }

    def calculate_voice_costs(self, audio_duration_seconds, text_char_count):
        """Calculate STT and TTS costs"""
        # STT Cost
        duration_minutes = audio_duration_seconds / 60.0
        stt_cost = duration_minutes * self.stt_price_per_minute
        
        # TTS Cost
        tts_cost = text_char_count * self.tts_price_per_char
        
        return round(stt_cost, 8), round(tts_cost, 8)

    def format_cost(self, cost):
        return f"${cost:.6f}"
