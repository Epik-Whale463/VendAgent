from decimal import Decimal, ROUND_HALF_UP

class Item:
    def __init__(self, name: str, price: Decimal, quantity: int):
        self.name = name
        self.price = Decimal(price)
        self.quantity = quantity

    def is_available(self) -> bool:
        return self.quantity > 0

    def purchase(self) -> bool:
        if self.is_available():
            self.quantity -= 1
            return True
        return False

class Inventory:
    def __init__(self):
        self.items = {}

    def add_item(self, item: Item):
        self.items[item.name.strip().lower()] = item

    def get_item(self, name: str):
        return self.items.get(name.strip().lower())

    def list_available_items(self):
        return [item for item in self.items.values() if item.is_available()]

class VendingMachine:
    def __init__(self, inventory: Inventory):
        self.inventory = inventory
        self.balance = Decimal("0.00")

    def insert_money(self, amount: Decimal):
        amt = Decimal(amount)
        if amt > 0:
            self.balance += amt

    def purchase_quantity(self, item_name: str, qty: int) -> dict:
        """Attempt to purchase up to qty items atomically.

        Returns a dict with keys: success, requested, bought, total_cost, remaining_balance, reason
        """
        try:
            qty = int(qty)
        except Exception:
            qty = 1

        if qty <= 0:
            return {"success": False, "reason": "invalid_quantity", "requested": qty}

        clean_name = item_name.strip().lower()
        item = self.inventory.get_item(clean_name)
        if not item:
            # try partial match
            for name, itm in self.inventory.items.items():
                if clean_name in name.lower():
                    item = itm
                    break
        if not item:
            return {"success": False, "reason": "not_found", "requested": qty}

        available = item.quantity
        to_buy = min(qty, available)
        if to_buy == 0:
            return {"success": False, "reason": "out_of_stock", "requested": qty}

        total_cost = round(item.price * to_buy, 2)
        if self.balance < total_cost:
            return {
                "success": False,
                "reason": "insufficient_funds",
                "required": total_cost,
                "balance": round(self.balance, 2),
                "requested": qty,
                "available": available,
            }

        # commit purchase
        bought = 0
        for _ in range(to_buy):
            if item.purchase():
                bought += 1
        # deduct total cost
        self.balance = round(self.balance - round(item.price * bought, 2), 2)

        return {
            "success": True,
            "requested": qty,
            "bought": bought,
            "total_cost": round(item.price * bought, 2),
            "remaining_balance": round(self.balance, 2),
        }

    def refund(self) -> float:
        refund_amount = float(self.balance)
        self.balance = Decimal("0.00")
        return refund_amount