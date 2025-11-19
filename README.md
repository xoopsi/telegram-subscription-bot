# Telegram Subscription Bot for Portfolio Management

This project is a fully functional Telegram bot built to manage client subscriptions, payments, receipt verification, portfolio registration, weekly settlement, and more. Designed with `python-telegram-bot`, it can be adapted to various business use cases.

## 🎥 Demo Video

Watch this demo video to learn how the bot works and what it does:

➡️ YouTube Link: [*Place your video link here*](https://youtu.be/2r5f5M7otNA)

---

## 📁 Project Structure

```bash
telegram-subscription-bot/
├── app.py # Main bot engine
├── db.py # SQLite database handler
├── handlers/ # Handlers for multiple bot menus and commands
│ ├── common.py
│ ├── registration.py
│ ├── payments.py
│ ├── admin.py
│ ├── portfolio.py
│ └── report.py
├── scheduler/ # Scheduler tasks
├── config.py # BOT_TOKEN and configurations
└── README.md # This file
```


---

## 🛠️ Setup Guide

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a config.py and include:
   ```bash
   BOT_TOKEN = "Your Telegram Bot Token"
   ADMIN_IDS = [12345678]
   SCHEDULER_INTERVAL = 3600
   ```


3. Run the bot:
```bash
python main.py
or
python -m folder.main.py

```

📬 Contact & Purchase

If you're interested in getting the full source code with setup instructions, please contact me via:

Telegram: @mhshirin
Gmail : hadi.shirin@gmail.com


---

ا
