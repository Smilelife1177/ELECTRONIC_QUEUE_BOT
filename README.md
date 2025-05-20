# Telegram Queue Bot

This project is a Telegram bot written in Python that implements an electronic queue system. Users can join, leave, view, and manage a queue directly in Telegram chats, making it perfect for event registrations, customer service, or any queue-based workflow.

## Features

* **Join Queue** : Adds a user to the end of the queue.
* **Leave Queue** : Removes a user from the queue.
* **View Queue** : Displays the current list of participants with their names and positions.
* **Next in Line** : Removes the first user from the queue (e.g., after being served).
* **Interactive Interface** : Provides user-friendly buttons for seamless interaction.

## Requirements

* Python 3.8 +++++++++++++++++++++
* MySQL database (for persistent queue storage)
* Telegram bot token from [BotFather](https://t.me/BotFather)

## Installation

1. **Clone the repository** :

```bash
   git clone https://github.com/Smilelife1177/Pet2025.git
   cd Pet2025
```

1. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. **Install dependencies** :

```bash
   pip install -r requirements.txt
```

1. **Set up environment variables** :
   Create a `.env` file in the project root with the following content:

```plaintext
   TELEGRAM_TOKEN=your_bot_token_here
```

1. **Configure the MySQL database** :

* Ensure a MySQL server is running.
* Create a database and necessary tables (see `schema.sql` in the repository for table structure).
* Update the `.env` file with your MySQL credentials.

1. **Run the bot** :

```bash
   python bot.py
```

## Requirements File

The `requirements.txt` file should include:

```plaintext
aiogram==3.13.1
python-dotenv==1.1.0
mysql-connector-python==8.4.0
```

To update dependencies to the latest compatible versions:

```bash
pip install --upgrade -r requirements.txt
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Run `black` and `flake8` to ensure code style compliance.
5. Push to the branch (`git push origin feature/your-feature`).
6. Open a pull request.

Please include a detailed description of your changes and ensure tests pass.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Support

For issues or questions, open an issue on the [GitHub repository](https://github.com/Smilelife1177/Pet2025) or contact the maintainers.
