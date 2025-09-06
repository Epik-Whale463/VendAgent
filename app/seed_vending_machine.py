"""
Seed data for the vending machine inventory.
This module provides functions to initialize the vending machine with sample data.
"""

from models import VendingMachine, Item, Inventory
from decimal import Decimal


def create_default_inventory():
    """Create and return a default inventory with sample items."""
    inventory = Inventory()
    
    # Basic snacks and drinks
    inventory.add_item(Item("chips", Decimal("1.50"), 10))
    inventory.add_item(Item("soda", Decimal("2.00"), 25))
    inventory.add_item(Item("water", Decimal("1.00"), 8))
    inventory.add_item(Item("candy", Decimal("1.25"), 15))
    inventory.add_item(Item("cookies", Decimal("2.50"), 12))
    inventory.add_item(Item("juice", Decimal("2.75"), 18))
    
    return inventory


def create_expanded_inventory():
    """Create and return an expanded inventory with more variety."""
    inventory = Inventory()
    
    # Snacks
    inventory.add_item(Item("chips", Decimal("1.50"), 20))
    inventory.add_item(Item("pretzels", Decimal("1.75"), 15))
    inventory.add_item(Item("nuts", Decimal("2.25"), 10))
    inventory.add_item(Item("crackers", Decimal("1.25"), 18))
    inventory.add_item(Item("candy", Decimal("1.25"), 25))
    inventory.add_item(Item("cookies", Decimal("2.50"), 12))
    inventory.add_item(Item("granola bar", Decimal("2.00"), 16))
    
    # Drinks
    inventory.add_item(Item("soda", Decimal("2.00"), 30))
    inventory.add_item(Item("water", Decimal("1.00"), 40))
    inventory.add_item(Item("juice", Decimal("2.75"), 20))
    inventory.add_item(Item("energy drink", Decimal("3.50"), 8))
    inventory.add_item(Item("coffee", Decimal("2.25"), 15))
    inventory.add_item(Item("tea", Decimal("1.75"), 12))
    
    # Healthy options
    inventory.add_item(Item("fruit cup", Decimal("3.00"), 6))
    inventory.add_item(Item("yogurt", Decimal("2.50"), 10))
    inventory.add_item(Item("trail mix", Decimal("3.25"), 8))
    
    return inventory


def create_minimal_inventory():
    """Create and return a minimal inventory for testing."""
    inventory = Inventory()
    
    inventory.add_item(Item("chips", Decimal("1.50"), 5))
    inventory.add_item(Item("soda", Decimal("2.00"), 3))
    inventory.add_item(Item("water", Decimal("1.00"), 2))
    
    return inventory


def create_empty_inventory():
    """Create and return an empty inventory."""
    return Inventory()


def seed_vending_machine(inventory_type="expanded"):
    """
    Create and return a seeded vending machine.
    
    Args:
        inventory_type (str): Type of inventory to create
            - "default": Basic selection of items
            - "expanded": Large variety of items
            - "minimal": Just a few items for testing
            - "empty": No items
    
    Returns:
        VendingMachine: A vending machine with the specified inventory
    """
    inventory_creators = {
        "default": create_default_inventory,
        "expanded": create_expanded_inventory,
        "minimal": create_minimal_inventory,
        "empty": create_empty_inventory
    }
    
    if inventory_type not in inventory_creators:
        raise ValueError(f"Unknown inventory type: {inventory_type}. "
                        f"Available types: {list(inventory_creators.keys())}")
    
    inventory = inventory_creators[inventory_type]()
    return VendingMachine(inventory=inventory)


def print_inventory_summary(vending_machine):
    """Print a summary of the vending machine's inventory."""
    items = vending_machine.inventory.list_available_items()
    
    if not items:
        print("Inventory is empty!")
        return
    
    print(f"\nInventory Summary ({len(items)} items):")
    print("-" * 50)
    print(f"{'Item':<15} {'Price':<8} {'Stock':<8} {'Value':<8}")
    print("-" * 50)
    
    total_value = Decimal("0.00")
    total_items = 0
    
    for item in sorted(items, key=lambda x: x.name):
        item_value = item.price * item.quantity
        total_value += item_value
        total_items += item.quantity
        
        print(f"{item.name.title():<15} ${item.price:<7.2f} {item.quantity:<8} ${item_value:<7.2f}")
    
    print("-" * 50)
    print(f"{'Total:':<15} {'':<8} {total_items:<8} ${total_value:<7.2f}")
    print(f"Average price: ${total_value / total_items:.2f}" if total_items > 0 else "")


if __name__ == "__main__":
    # Demonstrate different inventory types
    print("Vending Machine Inventory Seeder")
    print("=" * 40)
    
    inventory_types = ["default", "expanded", "minimal", "empty"]
    
    for inv_type in inventory_types:
        print(f"\n{inv_type.upper()} INVENTORY:")
        vm = seed_vending_machine(inv_type)
        print_inventory_summary(vm)
        print()
