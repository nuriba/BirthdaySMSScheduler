from flask import Flask, render_template, request, flash, redirect, url_for, session
import os
from datetime import datetime
import json
from twilio.rest import Client
from dotenv import load_dotenv
from qstash import QStash

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Server configuration
PORT = int(os.getenv("PORT", 5001))
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5001")

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# QStash configuration
QSTASH_TOKEN = os.getenv("QSTASH_TOKEN")
YOUR_API_URL = os.getenv("YOUR_API_URL")

# Initialize QStash client
qstash_client = QStash(QSTASH_TOKEN)

# Define the route for the main page
@app.route('/')
# Main page of the application
def index():
    # Get any form data from session to preserve it on errors
    form_data = session.get('form_data', {})
    # Clear the session data after retrieving it
    session.pop('form_data', None)
    # Clear any success message
    session.pop('success_data', None)
    # Render the main page with any previously entered data
    return render_template('index.html', form_data=form_data)

# Define the route for the schedule form
@app.route('/schedule', methods=['POST'])
# Schedule a birthday message
def schedule_message():
    # Store form data in session to preserve it in case of errors
    session['form_data'] = {
        'name': request.form.get('name', ''),
        'phone': request.form.get('phone', ''),
        'birth_date': request.form.get('birth_date', ''),
        'message_time': request.form.get('message_time', ''),
        'message_type': request.form.get('message_type', 'default'),
        'custom_message': request.form.get('custom_message', '')
    }
    
    try:
        # Get form data
        recipient_name = request.form.get('name')
        recipient_phone = request.form.get('phone')
        birth_date = request.form.get('birth_date')  # Format: MM/DD
        message_time = request.form.get('message_time')  # Format: HH:MM
        message_type = request.form.get('message_type') #default or custom
        custom_message = request.form.get('custom_message', '') # Only used if message_type is 'custom'
        
        # Validate inputs
        if not recipient_name or not recipient_phone or not birth_date or not message_time:
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('index'))
        
        # Parse date and time
        month, day = map(int, birth_date.split('/'))  # Changed to MM/DD format
        hour, minute = map(int, message_time.split(':'))
        
        # Create message
        if message_type == 'default':
            message = f"Happy birthday {recipient_name}, Wishing you a wonderful birthday filled with happiness and joy! Have a fantastic day!"
        else:
            message = custom_message
        
        # Determine schedule date (this year or next year)
        current_date = datetime.now()
        current_year = current_date.year
        
        try:
            schedule_date = datetime(current_year, month, day, hour, minute)
            
            # If the date has already passed this year, schedule for next year
            if schedule_date < current_date:
                schedule_date = datetime(current_year + 1, month, day, hour, minute)
        except ValueError as e:
            flash(f'Invalid date: {str(e)}', 'error')
            return redirect(url_for('index'))
            
        # Prepare the payload for the SMS sending endpoint
        sms_payload = {
            "to": recipient_phone,
            "message": message,
            "from": TWILIO_PHONE_NUMBER
        }
        
        # Create a cron expression for the specific date and time
        cron_expression = f"{minute} {hour} {day} {month} *"
        
        try:
            # Use QStash SDK to create a schedule
            schedule_id = qstash_client.schedule.create(
                destination=YOUR_API_URL,
                cron=cron_expression,
                body=json.dumps(sms_payload),
                headers={"Content-Type": "application/json"}
            )
            
            # Store success data to display on confirmation page
            session['success_data'] = {
                'name': recipient_name,
                'phone': recipient_phone,
                'birth_date': birth_date,
                'message_time': message_time,
                'message_type': message_type,
                'custom_message': custom_message,
                'schedule_id': schedule_id,
                'schedule_date': schedule_date.strftime("%B %d, %Y at %I:%M %p")
            }
            
            # Clear form data from session on success
            session.pop('form_data', None)
            
            # Redirect to confirmation page
            return redirect(url_for('confirmation'))
            
        except Exception as qstash_error:
            flash(f'Failed to schedule message: {str(qstash_error)}', 'error')
            return redirect(url_for('index'))
    
    except Exception as e:
        import traceback
        print(f"Exception occurred: {str(e)}")
        print(traceback.format_exc())
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

# New route for confirmation page
@app.route('/confirmation')
def confirmation():
    # Get success data from session
    success_data = session.get('success_data')
    
    # If no success data, redirect to index
    if not success_data:
        return redirect(url_for('index'))
    
    # Render confirmation page
    return render_template('confirmation.html', data=success_data)

# Define the route for the SMS sending endpoint
@app.route('/send-sms', methods=['POST'])
# Endpoint to send SMS
def send_sms():
    try:
        # Get the request data
        if request.is_json:
            data = request.get_json()
        else:
            body_data = request.get_data(as_text=True)
            try:
                data = json.loads(body_data)
            except json.JSONDecodeError:
                print("Failed to parse JSON, trying to parse as string")
                # If QStash sends the JSON as a string, try to parse it again
                try:
                    data = json.loads(body_data.strip('"').replace('\\"', '"'))
                except:
                    print("Could not parse as JSON string, trying to parse with eval")
                    # Last resort - if it's a Python-formatted string
                    import ast
                    data = ast.literal_eval(body_data)
        
        # Get Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send SMS using Twilio
        message = client.messages.create(
            body=data['message'],
            from_=data['from'],
            to=data['to']
        )
        
        return {
            "success": True,
            "message_sid": message.sid
        }, 200
    
    except Exception as e:
        import traceback
        print(f"Exception in send_sms: {str(e)}")
        print(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }, 500


if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=PORT, debug=True)