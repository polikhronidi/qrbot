# QR Creator

My repository contains the source code for a chatbot developed using Python. QR Creator is designed to perform various tasks and interact with users on the Telegram platform, it is your ultimate QR code generator chat-bot! This repository contains all the necessary code and resources to deploy QRBOT and start generating QR codes effortlessly.

## Features
1. **Start Message Handler:** Upon receiving the "/start" command, the bot sends a greeting message to the user and updates their notification status in the database.
2. **User Interaction:** The bot allows users to interact with it through messages, commands, and inline keyboards.
3. **Database Integration:** It utilizes an SQLite database to store user information, including their IDs, names, notification statuses, etc.
4. **Admin Notification:** When a new user joins the bot, an admin is notified with relevant user details, such as username and registration count.
5. **Language Support:** The bot supports multiple languages and adjusts its responses based on the user's preferred language.

## Dependencies
- Python 3.х
- aiogram
- SQLAlchemy

## Installation
1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/polikhronidi/qrbot.git
   ```
2. Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```
Set up your Telegram bot token in the config.py file.
Run the bot using the following command:
```bash 
python main.py
```
## Usage
Start a chat with the bot on Telegram. Use commands such as "/start" to interact with the bot and explore its functionality. Customize the bot's behavior and responses by modifying the code according to your requirements.
##Structure
**main.py**: Main script containing the bot's logic and message handlers.
**config.py**: Configuration file for storing the bot token and other settings.
**database.py**: Module for managing the SQLite database used by the bot.
**utils.py**: Utility functions used throughout the bot's code.
##Contributing
Contributions are welcome! If you'd like to contribute to the development of this bot, please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
Special thanks to the developers of aiogram and SQLAlchemy for creating such powerful libraries for building Telegram bots and working with databases in Python.

For any questions or support, feel free to mail me at ahntr@vk.com.
