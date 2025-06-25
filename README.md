# Warehouse Automation Bot

This project is a warehouse automation bot designed to manage inventory efficiently. It supports multiple languages, including English, Russian, Georgian, and Azerbaijani, allowing users to interact with the bot in their preferred language.

## Features

- **Inventory Management**: The bot can update the quantity of items in the warehouse. For example, if a user takes an item, the bot will decrease the quantity, and if an item is returned, it will increase the quantity.
- **Multi-language Support**: Users can select their preferred language at startup, and all interactions will be localized accordingly.
- **User-Friendly Interface**: The bot provides a tile-based interface for easy selection of items, minimizing the need for typing.

## Project Structure

```
warehouse-bot
├── src
│   ├── bot.py                  # Main entry point for the bot
│   ├── inventory
│   │   ├── __init__.py
│   │   └── inventory_manager.py # Manages inventory items
│   ├── localization
│   │   ├── __init__.py
│   │   ├── en.json             # English translations
│   │   ├── ru.json             # Russian translations
│   │   ├── ka.json             # Georgian translations
│   │   └── az.json             # Azerbaijani translations
│   ├── ui
│   │   ├── __init__.py
│   │   └── tile_list.py        # UI for item selection
│   └── utils
│       ├── __init__.py
│       └── language_selector.py # Language selection functions
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd warehouse-bot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the bot:
   ```
   python src/bot.py
   ```

## Usage Guidelines

- Upon startup, select your preferred language.
- Use the tile interface to select items and update their quantities.
- Follow the prompts to take or return items from the inventory.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.