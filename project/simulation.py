import random
import time
import csv
import os
from chatbot import Chatbot
from config import Config
from cost_calculator import CostCalculator

# Realistic query templates
QUERY_TEMPLATES = [
    "What is the price of {product}?",
    "Does {product} contain {ingredient}?",
    "I have {skin_type} skin, is {product} suitable for me?",
    "What are the main ingredients in {product}?",
    "Can you tell me about the features of {product}?",
    "How do I use {product}?",
    "Is {product} good for {skin_type} skin?",
    "Do you have any recommendations for {skin_type} skin?",
    "I'm looking for something from {brand}.",
    "Is {product} waterproof?"
]

SKIN_TYPES = ["dry", "oily", "sensitive", "normal", "combination", "mature", "acne-prone"]
INGREDIENTS = ["parabens", "fragrance", "alcohol", "vitamin C", "retinol", "aloe vera"]

def generate_random_query(products):
    template = random.choice(QUERY_TEMPLATES)
    product = random.choice(products)
    
    query = template.format(
        product=product['name'],
        ingredient=random.choice(INGREDIENTS),
        skin_type=random.choice(SKIN_TYPES),
        brand=product['brand']
    )
    return query

def run_simulation():
    print("Initializing Simulation for 50 customers (Text + Voice)...")
    bot = Chatbot()
    products = bot.products
    calc = CostCalculator()
    
    num_customers = 50
    queries_per_customer_range = (4, 5)
    
    # 50% Voice Users
    voice_user_ratio = 0.5
    
    simulation_results = []
    
    start_time = time.time()
    
    print(f"Simulating {num_customers} customers using {Config.DEFAULT_MODEL}...")
    
    total_tokens_input = 0
    total_tokens_output = 0
    total_stt_cost = 0
    total_tts_cost = 0
    total_queries = 0
    
    # Pre-calculated costs for voice reporting
    
    for customer_i in range(1, num_customers + 1):
        customer_id = f"sim_user_{customer_i}"
        num_queries = random.randint(*queries_per_customer_range)
        
        is_voice_user = random.random() < voice_user_ratio
        mode = "voice" if is_voice_user else "text"
        
        print(f"Customer {customer_i} ({mode})...", end="\r")
        
        for _ in range(num_queries):
            query = generate_random_query(products)
            total_queries += 1
            
            # Simulate processing
            # For the purpose of this assignment, we use the real bot logic 
            # but we assume audio costs based on text length for simulation speed
            
            # 1. STT Simulation (if voice)
            stt_cost = 0
            audio_duration = 0
            if mode == "voice":
                # Estimate 1 sec roughly per 2 words? Or just random 5-15s
                audio_duration = random.uniform(5.0, 15.0) 
                stt_cost, _ = calc.calculate_voice_costs(audio_duration, 0)
                total_stt_cost += stt_cost

            # 2. Bot Processing
            # We use 'groq' as per requirement
            response, ai_cost = bot.process_query(customer_id, query, model_service="groq")
            
            # Retrieve token counts from the bot's internal tracking (log)
            # This is bit of a hack to get the tokens out without changing process_query signature
            if bot.sessions[customer_id].logs:
                last_log = bot.sessions[customer_id].logs[-1]
                input_tok = last_log['input_tokens']
                output_tok = last_log['output_tokens']
                total_tokens_input += input_tok
                total_tokens_output += output_tok
            else:
                input_tok = 0
                output_tok = 0
            
            # 3. TTS Simulation (if voice)
            tts_cost = 0
            if mode == "voice":
                # Edge TTS is free, but we track it logic anyway
                char_count = len(response)
                _, tts_cost = calc.calculate_voice_costs(0, char_count)
                total_tts_cost += tts_cost

            simulation_results.append({
                "customer_id": customer_id,
                "mode": mode,
                "query": query,
                "response": response,
                "ai_cost": ai_cost,
                "stt_cost": stt_cost,
                "tts_cost": tts_cost,
                "total_cost": ai_cost + stt_cost + tts_cost,
                "input_tokens": input_tok,
                "output_tokens": output_tok,
                "audio_duration": audio_duration
            })

    print(f"\nSimulation Complete! Time: {time.time() - start_time:.2f}s")
    
    # Export logs
    os.makedirs("logs", exist_ok=True)
    csv_filename = f"logs/voice_simulation_{int(time.time())}.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "customer_id", "mode", "query", "response", "ai_cost", 
            "stt_cost", "tts_cost", "total_cost", "input_tokens", 
            "output_tokens", "audio_duration"
        ])
        writer.writeheader()
        writer.writerows(simulation_results)
        
    print(f"Detailed logs saved to {csv_filename}")
    
    # Summary Report
    total_ai_cost = sum(r['ai_cost'] for r in simulation_results)
    grand_total = total_ai_cost + total_stt_cost + total_tts_cost
    
    print("\n--- Final Cost Analysis ---")
    print(f"Total Queries: {total_queries}")
    print(f"AI Cost (Groq): ${total_ai_cost:.6f}")
    print(f"STT Cost (Whisper): ${total_stt_cost:.6f}")
    print(f"TTS Cost (Edge): ${total_tts_cost:.6f}")
    print(f"GRAND TOTAL: ${grand_total:.6f}")
    print("-" * 30)

if __name__ == "__main__":
    run_simulation()
