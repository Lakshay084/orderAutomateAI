import re

class EmailParser:
    @staticmethod
    def parse_email(content):
        # Example parsing logic
        supplier_name = re.search(r"Dear\s+(.*?)\,", content)
        agreed_price = re.search(r"price\s+to\s+\$(\d+(\.\d+)?)", content)  # Match $198.0
        quantity = re.search(r"order\s+volume\s+of\s+(\d+)", content)  # Match 500
        status = "Agreed" if "agree" in content.lower() else "Pending"

        return {
            "supplier_name": supplier_name.group(1) if supplier_name else None,
            "agreed_price": float(agreed_price.group(1)) if agreed_price else None,
            "quantity": int(quantity.group(1)) if quantity else None,
            "status": status,
        }

