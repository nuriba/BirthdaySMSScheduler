# Birthday SMS Scheduler

A simple Flask application that schedules birthday SMS messages using QStash for scheduling and Twilio for sending SMS.

## Features

- Schedule birthday SMS messages for specific dates and times
- Option to send default or custom birthday messages
- Client-side form validation
- Confirmation page showing scheduled message details
- Automatic scheduling for this year or next year based on current date
- Reliable message delivery with QStash scheduling

## Setup
### Prerequisites

- Python 3.7+
- Twilio account with phone number
- Upstash account with QStash access

### Installation

1. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your credentials
```
# Flask configuration
SECRET_KEY=your-secret-key

# Server configuration
PORT=5001
SERVER_URL=http://localhost:5001

# Twilio configuration
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone

# QStash configuration
QSTASH_TOKEN=your-qstash-token

# Your API endpoint (use ngrok for development)
YOUR_API_URL=https://your-ngrok-url.ngrok-free.app/send-sms
```

4. For local development, use ngrok to expose your endpoint
```bash
ngrok http 5001
```

5. Update the `YOUR_API_URL` in your `.env` file with the ngrok URL. Otherwise, you can't send your message after schedule it.

### Important Note: 
- Keep your ngrok tunnel running for QStash callbacks to work in development.
