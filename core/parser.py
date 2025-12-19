import re

def parse_expense_text(text):
    """
    Parses natural language string into structured expense data.
    
    Input: "20.50 lunch with @bob"
    Output: {
        'amount': 20.50,
        'description': "lunch with",
        'involved_users': ['bob']
    }
    """
    if not text:
        return None

    # 1. Extract Amount (Int or Float with up to 2 decimal places)
    # Regex explanation: Look for digits, optionally followed by a dot and 1-2 digits
    amount_match = re.search(r'(\d+(?:\.\d{1,2})?)', text)
    
    if not amount_match:
        return None # No amount found, invalid expense
        
    amount_str = amount_match.group(1)
    amount = float(amount_str)

    # 2. Extract Involved Users (@username)
    # Regex explanation: Look for @ followed by word characters
    mentions = re.findall(r'@(\w+)', text)

    # 3. Clean Description
    # Remove the amount from text
    text_no_amount = text.replace(amount_str, "", 1)
    
    # Remove mentions
    for user in mentions:
        text_no_amount = text_no_amount.replace(f"@{user}", "")
        
    # Clean up whitespace and special chars
    description = text_no_amount.strip()
    
    # Fallback if description is empty
    if not description:
        description = "General Expense"

    return {
        'amount': amount,
        'description': description,
        'involved_users': mentions
    }

# --- Unit Test Block (For local verification) ---
if __name__ == "__main__":
    # Test cases
    tests = [
        "20 lunch",
        "Taxi 15.50",
        "Dinner 100 @alice @bob",
        "5 coffee"
    ]
    for t in tests:
        print(f"Input: '{t}' -> {parse_expense_text(t)}")
