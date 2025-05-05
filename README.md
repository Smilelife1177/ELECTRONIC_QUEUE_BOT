# Telegram Queue Bot

This project is a Telegram bot written in Python that implements an electronic queue system. Users can join the queue, leave it, view the list of participants, and call the next person in line. The bot is ideal for organizing queues in chats, such as for event registrations or customer service.

## Features

- **Join Queue**: Adds a user to the end of the queue.
- **Leave Queue**: Removes a user from the queue.
- **View Queue**: Displays the current list of participants with their names.
- **Next in Line**: Removes the first user from the queue (e.g., after being served).
- Interactive interface with buttons.

## Requirements

- Python 3.7++

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Smilelife1177/Pet2025.git
   cd Pet2025
   ```
2. **Set up a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
4. **Create a `.env` file** in the project root and add your Telegram bot token:

   ```plaintext
   TELEGRAM_TOKEN=your_bot_token_here
   ```
5. **Run the bot**:

   ```bash
   python bot.py
   ```

## Additional Notes

- Ensure you have a Telegram bot token from [BotFather](https://t.me/BotFather).The `requirements.txt` file should include:
- ```plaintext
  aiogram==3.13.1
  python-dotenv==1.1.0
  mysql-connector-python==8.0.33
  ```
- For development, you may want to add `black` or `flake8` to `requirements.txt` for code formatting and linting:
  ```plaintext
  black==23.3.0
  flake8==6.0.0
  ```
- To update dependencies, use:
  ```bash
  pip install --upgrade -r requirements.txt
  ```

## Contributing

Feel free to submit issues or pull requests to improve the bot. Please follow the code style and run `black` and `flake8` before submitting changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
