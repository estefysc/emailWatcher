# App Architecture

This application is a WhatsApp-based email management system that uses Ngrok, Flask, Twilio, and Gmail APIs. 

At startup, the application will obtain a summary of the user's unread emails and send it to the user via WhatsApp (using a Twilio sandbox number), along with a prompt asking how they would like to proceed: keep all emails, delete all emails, or keep emails from a specific sender.

## Startup Sequence
### Tunnel Creation
1. An ngrok tunnel is established to make the local Flask server publicly accessible for Twilio webhooks.

### Thread Creation
The application runs on three main threads:
1. `appThread`: Flask web server (Port 8000)
2. `initProcessThread`: Initial setup and user communication
3. `monitorThread`: Shutdown signal monitoring

## Message Flow
#### Outbound Messages (App → User)
The app directly calls Twilio's API using Twilio's client libraries/SDK. These requests go straight to Twilio's servers using Twilio's public API endpoints. Twilio then handles delivering the message to WhatsApp. These outbound requests don't need the tunnel as  they're standard HTTP requests to Twilio's public API endpoints.

#### Inbound Messages (User → App)
When a user sends a WhatsApp message responding to the application, the message goes to 
Twilio, which needs to forward this message to the app via a webhook. The ngrok tunnel creates a secure encrypted tunnel between the local development machine and the ngrok service, which then provides a public URL that can be used to receive Twilio's webhooks. 

## Configuration
### Environment Variables
The application uses a `config.cfg` file to manage environment variables and sensitive credentials. This file should be kept secure and never committed to version control.

### Required Configuration
Create a `config.cfg` file in the root directory with the following structure:

```ini
[NGROK]
DOMAIN = your-ngrok-domain.ngrok-free.app

[WHATSAPP]
ACCOUNT_SID = your-twilio-account-sid
AUTH_TOKEN = your-twilio-auth-token

[MESSAGES]
FROM_NUMBER = whatsapp:+1234567890
TO_NUMBER = whatsapp:+1234567890

[OpenAI]
OPENAI_API_KEY = your-openai-api-key
```

### Variable Descriptions
#### NGROK Configuration
- `DOMAIN`: Your ngrok domain for webhook endpoints. Obtained from the ngrok dashboard.

#### WhatsApp Configuration (via Twilio)
- `ACCOUNT_SID`: Your Twilio Account SID found in Twilio Console
- `AUTH_TOKEN`: Your Twilio Auth Token found in Twilio Console

#### Message Settings
- `FROM_NUMBER`: Your Twilio WhatsApp sandbox number (format: whatsapp:+1234567890)
- `TO_NUMBER`: Your personal WhatsApp number that will receive the messages (format: whatsapp:+1234567890)

#### OpenAI Configuration
- `OPENAI_API_KEY`: Your OpenAI API key for AI functionality. 

### Authentication
#### token.json
The `token.json` file is used to store OAuth 2.0 credentials for Gmail API authentication:

- This file contains the user's access and refresh tokens
- It is automatically created during the first authorization flow
- If you encounter an `invalid_grant: Token has been expired or revoked` error:
  1. Delete the existing `token.json` file
  2. Restart the application
  3. A new authorization flow will begin and create a fresh `token.json`