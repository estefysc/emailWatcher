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