# Setup Guide - WhatsApp Sales Bot

Complete step-by-step guide to get the bot running.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Windows/Linux/macOS computer
- [ ] Python 3.8 or higher installed
- [ ] Google Chrome browser installed
- [ ] SQL Server database access
- [ ] Gmail or SMTP account for notifications
- [ ] WhatsApp account for each bot

## 🔧 Step-by-Step Setup

### 1. Install Python Dependencies

```bash
# Navigate to project directory
cd whatsapp-sales-bot

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Install ChromeDriver

**Option A: Automatic (Recommended)**
```bash
pip install webdriver-manager
```
Then the bot will download ChromeDriver automatically.

**Option B: Manual**
1. Check your Chrome version: `chrome://version`
2. Download matching ChromeDriver from: https://chromedriver.chromium.org/
3. Extract to a folder (e.g., `C:/chromedriver/`)
4. Note the full path to `chromedriver.exe`

### 3. Create Chrome Profiles

Each bot needs its own Chrome profile to maintain separate WhatsApp sessions.

```bash
# Create directories for Chrome profiles
mkdir Chrome-Profiles
mkdir Chrome-Profiles/Bot1-Georgetown
mkdir Chrome-Profiles/Bot2-Zambia
mkdir Chrome-Profiles/Bot3-Other
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` with your details:

```env
# ChromeDriver path (use forward slashes even on Windows)
CHROMEDRIVER_PATH=C:/chromedriver/chromedriver.exe

# Database (SQL Server)
DB_DRIVER=SQL Server
DB_SERVER=your-server.database.windows.net
DB_NAME=YourDatabaseName
DB_TRUSTED=yes

# Gmail SMTP (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # See below for setup
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Email recipients
REPORT_ERROR_TO=admin@example.com
REPORT_DAILY_TO=manager@example.com

# Daily report time (24-hour format)
DAILY_REPORT_TIME=13:04
```

### 5. Setup Gmail App Password (for Notifications)

1. Go to Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable if not already)
3. Scroll to **App passwords**
4. Create a new app password for "Mail"
5. Copy the 16-character password
6. Paste it into `.env` as `MAIL_PASSWORD`

### 6. Configure Bot Settings

Edit `config.json`:

```json
{
  "bots": {
    "Bot1-GY": {
      "campuses": ["Georgetown"],
      "profile": "C:/path/to/Chrome-Profiles/Bot1-Georgetown"
    },
    "Bot2-ZA": {
      "campuses": ["Zambia"],
      "profile": "C:/path/to/Chrome-Profiles/Bot2-Zambia"
    },
    "Bot3-NIL": {
      "campuses": ["NULL", "NIL"],
      "profile": "C:/path/to/Chrome-Profiles/Bot3-Other"
    }
  },
  "settings": {
    "poll_interval": 30,        // Check database every 30 seconds
    "batch_size": 5,            // Process 5 leads at a time
    "message_delay_min": 3,     // Wait 3-6 seconds between messages
    "message_delay_max": 6,
    "anti_lock_interval": 240   // Prevent sleep every 4 minutes
  }
}
```

### 7. Setup Message Templates

Edit `messages.json` with your custom messages:

```json
{
  "Doctor of Medicine": "Hi {name}! Welcome to our MD program...",
  "Master of Public Health": "Hello {name}! Thanks for your interest in MPH...",
  "Default": "Hi {name}! Welcome to {program}..."
}
```

**Available placeholders:**
- `{name}` - Student's first name
- `{program}` - Program name
- `{phone}` - Phone number (without +)

### 8. Setup Database Tables

Run this SQL script on your SQL Server:

```sql
-- Create Lead_status table for tracking
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

-- Create index for better performance
CREATE INDEX idx_datetime ON Lead_status(Date_time);
CREATE INDEX idx_campus ON Lead_status(mx_Program_Campus);
```

### 9. First Run - Login to WhatsApp

```bash
python main.py
```

When prompted, press ENTER. Three Chrome windows will open:

1. **For each window:**
   - WhatsApp Web will load
   - Scan the QR code with your WhatsApp account
   - Wait for chats to load
   - Keep the window open

2. **Important:** Use a different WhatsApp number for each bot!

### 10. Verify Setup

Check that:
- [ ] All 3 Chrome windows show WhatsApp chats
- [ ] Console shows "All 3 bots launched successfully!"
- [ ] `logs/` directory is created with log files
- [ ] No error messages in console

## 🎯 Usage

### Normal Operation

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the bot
python main.py
```

### Monitoring

Watch the console output for:
- `Processing X leads` - Bot is working
- `Message sent to [Name]` - Success
- `NotFound` - Contact not on WhatsApp
- `Failed-Send` - Sending error

Check logs:
```bash
# View today's log
tail -f logs/bot_YYYYMMDD.log

# View recent errors
ls -lt errors/
```

### Daily Reports

Reports are automatically emailed at the configured time with:
- Total messages sent/failed
- Success rate percentage
- Breakdown by campus
- Color-coded status

## 🔍 Troubleshooting

### Bot won't start
```
Error: ChromeDriver version mismatch
Solution: Update ChromeDriver to match Chrome version
```

### WhatsApp won't load
```
Error: QR code timeout
Solution: 
1. Check internet connection
2. Clear Chrome profile: delete profile folder and restart
3. Try using Chrome incognito mode profile
```

### Messages not sending
```
Error: Element not found
Solution:
1. WhatsApp UI may have changed
2. Check XPath selectors in whatsapp_helper.py
3. Increase wait times in configuration
```

### Database connection failed
```
Error: Login failed for user
Solution:
1. Verify DB_SERVER, DB_NAME in .env
2. Check SQL Server firewall rules
3. Ensure database user has INSERT/SELECT permissions
```

### Email notifications not working
```
Error: Authentication failed
Solution:
1. Use Gmail App Password, not regular password
2. Enable "Less secure app access" if needed
3. Check SMTP settings (port 587 for TLS)
```

## 📊 Performance Tuning

### For High Volume (1000+ leads/day)
```json
{
  "settings": {
    "poll_interval": 15,     // Check more frequently
    "batch_size": 10,        // Process more at once
    "message_delay_min": 2,  // Faster sending
    "message_delay_max": 4
  }
}
```

### For Stability (Avoiding Blocks)
```json
{
  "settings": {
    "poll_interval": 60,     // Check less frequently
    "batch_size": 3,         // Process fewer at once
    "message_delay_min": 5,  // Longer delays
    "message_delay_max": 10
  }
}
```

## 🛡️ Security Best Practices

1. **Never commit `.env` file** - Contains passwords
2. **Use app-specific passwords** - Not your main Gmail password
3. **Restrict database permissions** - Only SELECT/INSERT needed
4. **Regular backups** - Backup Chrome profiles weekly
5. **Monitor error emails** - Review all error notifications

## 📞 Support

If you encounter issues:

1. Check logs in `logs/` directory
2. Review error screenshots in `errors/` directory
3. Search existing GitHub issues
4. Create a new issue with:
   - Error message
   - Log excerpt
   - Configuration (without passwords!)

## 🎉 Success!

Once everything is working, you should see:
- Bots processing leads every 30 seconds
- Success messages in console
- Daily email reports
- Lead_status table populating

**Happy automating! 🚀**
