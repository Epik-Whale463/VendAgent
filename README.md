# VendAgent

![VendAgent Screenshot](image.png)

VendAgent is a simple tool designed to automate and manage vending machine operations. It helps track inventory, sales, and restocking schedules to streamline vending business processes.

## Features

- Inventory management
- Sales tracking
- Restocking reminders

## Getting Started

Clone the repository and follow the setup instructions in the documentation to begin using VendAgent.

## Vending Machine Project

## Class Structure

``` text
Item
 └─ name: str
 └─ price: Decimal
 └─ quantity: int
 └─ is_available() -> bool
 └─ purchase() -> bool

Inventory
 └─ items: dict[str, Item]
 └─ add_item(item: Item)
 └─ get_item(name: str) -> Item | None
 └─ list_available_items() -> list[Item]

VendingMachine
 └─ inventory: Inventory
 └─ balance: Decimal
 └─ insert_money(amount: Decimal)
 └─ purchase_quantity(item_name: str, qty: int) -> dict
 └─ refund() -> float
```

## Agent Orchestration

- Uses LangChain and LangGraph to create a ReAct agent.
- Tools exposed to the agent:
  - `get_inventory()`: Returns current inventory.
  - `buy_item(item_name, quantity)`: Attempts to purchase an item.
  - `insert_money(amount)`: Insert money into the machine.
  - `get_balance()`: Returns current balance.
  - `refund()`: Refunds the current balance.
- The agent is initialized with a system prompt to enforce plain text, friendly responses.
- User input is parsed and routed to the correct tool or handled by the agent for natural language queries.
- Inventory and balance are persisted between sessions using a local file.
- The CLI supports multi-item purchases, edge case handling, and a styled ASCII-art interface.

---

Run the CLI:

``` code
python agent.py
```

Type `help` in the CLI for available commands.
