import argparse
import sys
from chatbot import Chatbot
from config import Config
try:
    from simulation import run_simulation
except ImportError:
    run_simulation = None

def interactive_chat():
    print("Initializing Lira Cosmetics Chatbot...")
    bot = Chatbot()
    customer_id = "user_interactive_session"
    print(f"Chatbot ready! (Model: {Config.DEFAULT_MODEL})")
    print("Type 'exit' or 'quit' to end session.")
    print("-" * 50)

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            print("Chatbot: Thinking...", end="\r")
            response, cost = bot.process_query(customer_id, user_input, model_service="claude") # default to claude
            
            print(f"Chatbot: {response}")
            print(f"         [Cost: ${cost:.6f}]")
            print("-" * 50)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    stats = bot.get_session_stats(customer_id)
    if stats:
        print("\nSession Summary:")
        print(f"Total Queries: {stats['query_count']}")
        print(f"Total Tokens: {stats['total_tokens']}")
        print(f"Total Cost: ${stats['total_cost']:.6f}")

def main():
    parser = argparse.ArgumentParser(description="Lira Cosmetics AI Customer Service Chatbot")
    parser.add_argument('mode', choices=['chat', 'simulate'], nargs='?', default='chat', help="Mode to run: 'chat' for interactive mode, 'simulate' for customer simulation")
    
    args = parser.parse_args()

    if args.mode == 'chat':
        interactive_chat()
    elif args.mode == 'simulate':
        if run_simulation:
            print("Starting simulation...")
            run_simulation()
        else:
            print("Simulation module not found or import error.")
            # Fallback inline or just error out. 
            # Ideally simulation.py is implemented next so this will work.

if __name__ == "__main__":
    main()
