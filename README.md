# WhatsApp Sales Bot - Multi-Campus Lead Management System

A powerful, multi-threaded WhatsApp automation system designed for educational institutions to manage and send personalized messages to leads across multiple campuses.

## 🌟 Features

- **Multi-Bot Architecture**: Run 3 independent bots simultaneously, each handling different campuses
- **Dynamic Message Templates**: Customizable message templates based on program types
- **Smart Program Matching**: Fuzzy matching algorithm to find the best message template
- **Database Integration**: SQL Server integration for lead management and status tracking
- **Daily Reports**: Automated daily email reports with delivery statistics
- **Error Notifications**: Instant email alerts with screenshots when errors occur
- **Anti-Lock System**: Prevents system sleep/lock during long operations
- **Retry Mechanism**: Automatic retry logic for failed operations
- **Clean Logging**: Structured logging with rotation and retention policies

## 📋 Prerequisites

- Python 3.8+
- Google Chrome browser
- ChromeDriver (matching your Chrome version)
- SQL Server database
- SMTP email account (for reports)
- WhatsApp Web access for each bot profile

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/whatsapp-sales-bot.git
   cd whatsapp-sales-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your configuration details

4. **Set up message templates**
   - Edit `messages.json` with your program-specific templates

5. **Configure bot campuses**
   - Edit `config.json` to set up campus assignments for each bot

## ⚙️ Configuration

### `.env` File

```env
# ChromeDriver
CHROMEDRIVER_PATH=C:/chromedriver/chromedriver.exe

# Database Configuration
DB_DRIVER=SQL Server
DB_SERVER=your-server
DB_NAME=your-database
DB_TRUSTED=yes

# File Paths
MESSAGES_FILE=messages.json
CONFIG_FILE=config.json

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Recipients
REPORT_ERROR_TO=admin@example.com
REPORT_DAILY_TO=manager@example.com

# Daily Report Time (24-hour format)
DAILY_REPORT_TIME=13:04
```

### `config.json` Structure

```json
{
  "bots": {
    "Bot1-GY": {
      "campuses": ["Georgetown"],
      "profile": "C:/Chrome-Profiles/Bot1"
    },
    "Bot2-ZA": {
      "campuses": ["Zambia"],
      "profile": "C:/Chrome-Profiles/Bot2"
    },
    "Bot3-NIL": {
      "campuses": ["NULL", "NIL"],
      "profile": "C:/Chrome-Profiles/Bot3"
    }
  },
  "settings": {
    "poll_interval": 30,
    "batch_size": 5,
    "message_delay_min": 3,
    "message_delay_max": 6,
    "anti_lock_interval": 240
  }
}
```

### `messages.json` Structure

```json
{
  "Doctor of Medicine": "Hi {name}! 🩺 Congratulations on your interest in our MD program...",
  "Master of Public Health": "Hello {name}! 🏥 Thank you for choosing our MPH program...",
  "PhD": "Dear {name}, Greetings from Texila! 🎓 Your PhD journey starts here...",
  "Default": "Hi {name}! Thank you for your interest in {program}. We'll contact you soon!"
}
```

## 📁 Project Structure

```
whatsapp-sales-bot/
│
├── main.py                 # Main application entry point
├── helpers/
│   ├── __init__.py
│   ├── db_helper.py       # Database operations
│   ├── whatsapp_helper.py # WhatsApp automation functions
│   ├── message_helper.py  # Message template handling
│   └── email_helper.py    # Email notification functions
│
├── config.json            # Bot and settings configuration
├── messages.json          # Message templates
├── .env                   # Environment variables (not in git)
├── .env.example          # Example environment file
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── logs/                  # Application logs (auto-created)
└── errors/               # Error screenshots (auto-created)
```

## 🎯 Usage

1. **Initial Setup**
   ```bash
   python main.py
   ```
   - Press ENTER when prompted
   - Scan QR codes for each bot (first time only)

2. **The system will automatically**:
   - Poll the database every 30 seconds (configurable)
   - Send personalized messages to new leads
   - Track message status in `Lead_status` table
   - Send daily reports at configured time
   - Alert on errors with screenshots

## 📊 Database Schema

### Required Tables

**DUMY_LIVEDB** (Source table)
- Phone (varchar)
- FirstName (varchar)
- OwnerIdName (varchar)
- mx_Program_Name (varchar)
- mx_Program_Campus (varchar)

**Lead_status** (Tracking table)
```sql
CREATE TABLE Lead_status (
    id INT IDENTITY(1,1) PRIMARY KEY,
    lead_name VARCHAR(255),
    Phone VARCHAR(50),
    Program VARCHAR(255),
    Degree_Awarding_Body VARCHAR(255),
    mx_Program_Campus VARCHAR(100),
    Status_lead VARCHAR(50),
    Date_time DATETIME
);
```

## 📈 Status Types

- **Sent**: Message successfully delivered
- **Failed-Send**: Message sending failed
- **NotFound**: Contact not found on WhatsApp
- **Failed-NewChat**: Couldn't open new chat
- **Error**: Unexpected error occurred

## 🔧 Troubleshooting

### Bot won't start
- Verify ChromeDriver version matches Chrome browser
- Check Chrome profile paths exist
- Ensure WhatsApp Web is accessible

### Messages not sending
- Verify WhatsApp Web is logged in for all profiles
- Check phone number format (must include country code)
- Review error logs in `logs/` directory

### Database connection fails
- Verify SQL Server credentials in `.env`
- Check network connectivity to database
- Ensure database user has required permissions

### Email reports not working
- Use app-specific password for Gmail
- Check SMTP settings in `.env`
- Verify recipient email addresses

## 🛡️ Security Considerations

- Never commit `.env` file to version control
- Use app-specific passwords for email accounts
- Restrict database user permissions to minimum required
- Keep ChromeDriver updated to latest version
- Regularly rotate SMTP credentials

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Support

For issues and questions, please open an issue on GitHub or contact the maintainer.

## ⚠️ Disclaimer

This tool is for legitimate business use only. Ensure compliance with WhatsApp's Terms of Service and applicable laws regarding automated messaging. The authors are not responsible for misuse of this software.

## 🎉 Acknowledgments

- Built for educational institutions managing multi-campus operations
- Uses Selenium WebDriver for WhatsApp Web automation
- Logging powered by Loguru

---

**Made with ❤️ for educational institutions worldwide**
