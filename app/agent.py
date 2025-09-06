from langchain.tools import tool
from models import VendingMachine, Item, Inventory
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Literal, Annotated
import json
import re, os
from decimal import Decimal
from dotenv import load_dotenv
from seed_vending_machine import seed_vending_machine
import sys
import pickle
import os

load_dotenv()

def _serialize_for_json(obj):
    """Recursively convert Decimal objects to float so json.dumps won't fail.

    Leaves other types unchanged. Handles dicts, lists, tuples and primitive types.
    """
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize_for_json(v) for v in obj]
    return obj


# Initialize vending machine with seeded inventory
vending_machine = seed_vending_machine("expanded")

llm = ChatGroq(model="openai/gpt-oss-20b",api_key=os.getenv("GROQ_API_KEY"))


@tool
def get_inventory() -> str:
    """Returns the current inventory of the vending machine."""
    items = vending_machine.inventory.list_available_items()
    payload = [{"name": item.name, "price": item.price, "quantity": item.quantity} for item in items]
    return json.dumps(_serialize_for_json(payload))

@tool
def buy_item(item_name: str, quantity: str = "1") -> str:
    """Attempts to purchase an item from the vending machine. Specify quantity (default 1)."""
    # parse quantity defensively
    try:
        q = int(float(quantity))
    except:
        q = 1
    res = vending_machine.purchase_quantity(item_name, q)
    return json.dumps(_serialize_for_json(res))

@tool
def refund() -> str:
    """Refunds the current balance."""
    amount = vending_machine.refund()
    return f"Refunded: ${amount:.2f}"

@tool
def get_balance() -> str:
    """Returns the current balance."""
    return f"Current balance: ${vending_machine.balance:.2f}"

@tool
def insert_money(amount: str) -> str:
    """Insert money into the vending machine. Amount should be a string representing a float."""
    # defensive parsing
    def extract_number_from_string(s: str):
        m = re.search(r"[-+]?\d*\.?\d+", s or "")
        return m.group() if m else None

    m = extract_number_from_string(amount)
    if m is None:
        return json.dumps(_serialize_for_json({"success": False, "reason": "invalid_amount", "input": amount}))
    vending_machine.insert_money(Decimal(str(m)))
    return json.dumps(_serialize_for_json({"success": True, "inserted": float(m), "balance": vending_machine.balance}))


# Define the tools list
tools = [get_inventory, buy_item, refund, get_balance, insert_money]

# Create the ReAct agent using LangGraph with system message
system_message = """You are a helpful vending machine assistant. When responding to users:
- Do NOT use markdown formatting (no **, ##, ###, |, etc.)
- Use plain text only
- Keep responses clear and simple
- Avoid tables, bold text, headers, or any special formatting
- Use simple lists with dashes (-) if needed, but no complex formatting"""

agent = create_react_agent(llm, tools)

# Test the agent
def run_vending_agent(query: str, show_reasoning: bool = True):
    """Run the vending machine agent with a user query."""
    try:
        if show_reasoning:
            print(f"\nUser Query: {query}")
            print("=" * 60)
            print("AGENT REASONING PROCESS:")
            print("-" * 60)
        
        # Include system message in the conversation
        messages = [
            ("system", system_message),
            ("user", query)
        ]
        
        result = agent.invoke({"messages": messages})
        
        if show_reasoning:
            for message in result["messages"]:
                if hasattr(message, 'content') and message.content:
                    content = message.content
                    # Print the agent's internal reasoning chain
                    print(content)
                    print("-" * 40)
        
        # Extract the final message from the agent
        final_message = result["messages"][-1].content

        # If the LLM returned JSON (tool output), parse it; otherwise return the final message string.
        try:
            out = json.loads(final_message)
            if isinstance(out, dict) and out.get("success") is not None:
                if out.get("success"):
                    final = f"Dispensed {out.get('bought')} item(s). Cost ${out.get('total_cost')}. Remaining balance ${out.get('remaining_balance')}."
                else:
                    if out.get('reason') == 'insufficient_funds':
                        final = f"Failed: insufficient funds. Required ${out.get('required')}, balance ${out.get('balance')}.'"
                    else:
                        final = f"Failed: {out.get('reason')}"
                return final
        except Exception:
            pass

        # fallback: return raw final message
        return final_message
    except Exception as e:
        return f"Error: {str(e)}"

def run_simple_agent(query: str):
    """Run the agent without reasoning output."""
    return run_vending_agent(query, show_reasoning=False)

# --- Persistence helpers ---
STATE_FILE = "vending_state.pkl"

def save_state():
    with open(STATE_FILE, "wb") as f:
        pickle.dump(vending_machine, f)

def load_state():
    global vending_machine
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "rb") as f:
            vending = pickle.load(f)
            if vending:
                vending_machine.inventory = vending.inventory
                vending_machine.balance = vending.balance

# --- Improved multi-item parsing ---
def parse_multi_item_request(text):
    # Example: "Buy 2 chips and 3 candy bars"
    pattern = r"(\d+)\s+([\w ]+)"
    items = re.findall(pattern, text, re.IGNORECASE)
    if not items:
        # fallback: try to find single item
        return [(text.strip(), 1)]
    return [(name.strip(), int(qty)) for qty, name in items]

# --- ASCII Art and Styled CLI ---
def print_ascii_header():
    header = r'''
 __      __            _           _           _     _             
 \ \    / /           | |         | |         | |   | |            
  \ \  / /__ _ __   __| | ___ _ __| |__   ___ | |__ | | ___  ___   
   \ \/ / _ \ '_ \ / _` |/ _ \ '__| '_ \ / _ \| '_ \| |/ _ \/ __|  
    \  /  __/ | | | (_| |  __/ |  | |_) | (_) | |_) | |  __/\__ \  
     \/ \___|_| |_|\__,_|\___|_|  |_.__/ \___/|_.__/|_|\___||___/  
                                                                   
'''
    print("\033[38;5;208m" + header + "\033[0m")  # Orange color if supported
    print("\033[1mWelcome to VENDING MACHINE CLI\033[0m\nType 'help' for commands. Type 'exit' to quit.\n")

def print_boxed(text):
    lines = text.split("\n")
    width = max(len(line) for line in lines)
    print("┌" + "─" * (width + 2) + "┐")
    for line in lines:
        print(f"│ {line.ljust(width)} │")
    print("└" + "─" * (width + 2) + "┘")

def interactive_cli():
    print_ascii_header()
    load_state()
    while True:
        try:
            user_input = input("\033[1;36mYou > \033[0m").strip()
            if user_input.lower() in ["exit", "quit"]:
                save_state()
                print("Session saved. Goodbye!")
                break
            elif user_input.lower() == "help":
                print_boxed("Commands:\n- inventory\n- buy <item> [qty]\n- insert <amount>\n- balance\n- refund\n- exit")
                continue
            elif user_input.lower() == "inventory":
                items = vending_machine.inventory.list_available_items()
                if not items:
                    print_boxed("No items available!")
                else:
                    inv_lines = [f"{item.name.title():<12} | ${item.price:<5.2f} | {item.quantity} in stock" for item in items]
                    print_boxed("INVENTORY:\n" + "\n".join(inv_lines))
                continue
            elif user_input.lower().startswith("insert"):
                amt = re.findall(r"[-+]?[0-9]*\.?[0-9]+", user_input)
                if amt:
                    amount = Decimal(amt[0])
                    if amount <= 0:
                        print_boxed("Amount must be positive.")
                        continue
                    vending_machine.insert_money(amount)
                    print_boxed(f"Inserted: ${amount:.2f}\nBalance: ${vending_machine.balance:.2f}")
                    save_state()
                else:
                    print_boxed("Invalid amount.")
                continue
            elif user_input.lower() == "balance":
                print_boxed(f"Current balance: ${vending_machine.balance:.2f}")
                continue
            elif user_input.lower() == "refund":
                if vending_machine.balance > 0:
                    refunded = vending_machine.refund()
                    print_boxed(f"Refunded: ${refunded:.2f}")
                    save_state()
                else:
                    print_boxed("No balance to refund.")
                continue
            elif user_input.lower().startswith("buy"):
                # Multi-item parsing
                req = user_input[3:].strip()
                items = parse_multi_item_request(req)
                total_cost = 0
                bought = []
                for name, qty in items:
                    res = vending_machine.purchase_quantity(name, qty)
                    if res["success"]:
                        bought.append(f"{res['bought']} {name.strip()}(s)")
                        total_cost += res["total_cost"]
                    else:
                        print_boxed(f"Could not buy {qty} {name}: {res.get('reason')}")
                if bought:
                    print_boxed(f"Purchased: {', '.join(bought)}\nTotal cost: ${total_cost:.2f}\nRemaining balance: ${vending_machine.balance:.2f}")
                    save_state()
                continue
            else:
                # Fallback to agent for natural language
                response = run_vending_agent(user_input, show_reasoning=False)
                print_boxed(response)
                save_state()
        except KeyboardInterrupt:
            save_state()
            print("\nSession saved. Goodbye!")
            break
        except Exception as e:
            print_boxed(f"Error: {e}")

if __name__ == "__main__":
    interactive_cli()