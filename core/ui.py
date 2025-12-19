from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# --- ASCII & Visual Helpers ---

def generate_ascii_tree(balances):
    """
    Converts a list of dicts [{'username': 'Alice', 'total': 150}]
    into a visual ASCII tree.
    """
    if not balances:
        return "<i>🌑 The treasury is empty.</i>"

    # Sort by total spent (descending)
    sorted_balances = sorted(balances, key=lambda x: x['total'], reverse=True)
    
    tree_lines = ["<b>🏆 Guild Treasury</b>"]
    
    for i, record in enumerate(sorted_balances):
        is_last = (i == len(sorted_balances) - 1)
        prefix = "└── " if is_last else "├── "
        
        # Formatting: Monospace for numbers to align visually
        amount = f"${record['total']:.2f}"
        name = record['username'] or "Unknown"
        
        line = f"{prefix}<b>{name}</b>: <code>{amount}</code>"
        tree_lines.append(line)
        
    return "\n".join(tree_lines)

# --- Message Templates ---

class Views:
    """
    Container for static text templates.
    """
    WELCOME = (
        "<b>🏰 The Guild Hall</b>\n\n"
        "Welcome, Architect. This is your central command for tracking "
        "expenses and managing the treasury.\n\n"
        "<i>Select a module below:</i>"
    )

    AWAITING_INPUT = (
        "<b>✍️ New Expense Entry</b>\n\n"
        "Please type the transaction details in natural language.\n"
        "Examples:\n"
        "• <code>15 lunch with @alice</code>\n"
        "• <code>50 server costs</code>\n\n"
        "<i>Waiting for input...</i>"
    )

    SETTINGS = (
        "<b>⚙️ System Settings</b>\n\n"
        "Configure your Guild preferences here.\n"
        "Current version: v1.0 (Serverless)\n\n"
        "<i>Toggle options below:</i>"
    )

    HELP = (
        "<b>📜 Scribe's Guide</b>\n\n"
        "<b>Adding Expenses:</b>\n"
        "Just click 'Add Expense' and type naturally.\n\n"
        "<b>Commands:</b>\n"
        "/start - Reset the dashboard"
    )

# --- Keyboard Layouts ---

def get_main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("💰 Finances", callback_data='btn_finances'),
            InlineKeyboardButton("👥 Members", callback_data='btn_members')
        ],
        [
            InlineKeyboardButton("➕ Add Expense", callback_data='btn_add_expense')
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data='btn_settings')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_members_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("✋ Join Guild", callback_data='btn_join'),
            InlineKeyboardButton("🚪 Leave", callback_data='btn_leave')
        ],
        [
            InlineKeyboardButton("🔙 Back to Hall", callback_data='btn_back_home')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🇺🇸 Language: EN", callback_data='btn_noop'),
            InlineKeyboardButton("🔔 Alerts: ON", callback_data='btn_noop')
        ],
        [
            InlineKeyboardButton("🔙 Back to Hall", callback_data='btn_back_home')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_finances_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🔄 Refresh", callback_data='btn_refresh_finances'),
            InlineKeyboardButton("📅 History", callback_data='btn_history')
        ],
        [
            InlineKeyboardButton("🔙 Back to Hall", callback_data='btn_back_home')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cancel_keyboard():
    """
    Used when the user is in AWAITING_INPUT state.
    """
    keyboard = [
        [
            InlineKeyboardButton("❌ Cancel", callback_data='btn_back_home')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Toast Messages (Callback Query Answers) ---

TOASTS = {
    'loading': "⏳ Consulting the scrolls...",
    'saved': "✅ Transaction recorded!",
    'cancelled': "🚫 Action cancelled.",
    'error': "⚠️ An error occurred."
}
