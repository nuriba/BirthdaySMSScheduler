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

### Deployment
To deploy the application on Vercel:

1. Create a `vercel.json` file in the project root with the following configuration:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/app.py"
    }
  ]
}
```

2. Configure the following environment variables in your Vercel deployment:
- SECRET_KEY
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_PHONE_NUMBER
- QSTASH_TOKEN
- YOUR_API_URL (set to your Vercel deployment URL + '/send-sms')

### Usage

1. Start the application
```bash
python app.py
```

2. Visit `http://localhost:5001` in your browser

3. Fill out the form with:
   - Recipient's name and phone number
   - Birth date (MM/DD format)
   - Message time
   - Choose default or custom message

4. Click "Schedule Birthday Message" to create the schedule

5. View the confirmation page with details of your scheduled message