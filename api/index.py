import os
import asyncio
import logging
from http.server import BaseHTTPRequestHandler
import json

from telegram import Update, Bot
from telegram.ext import Application

# Import our Logic
from core.router import route_update

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Environment Variables
TOKEN = os.getenv("TELEGRAM_TOKEN")

class handler(BaseHTTPRequestHandler):
    """
    Vercel Serverless Function Handler
    """
    def do_POST(self):
        try:
            # 1. Read the request body (The JSON from Telegram)
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            json_string = post_data.decode('utf-8')
            
            # 2. Convert JSON to Telegram Update Object
            update_data = json.loads(json_string)
            # We construct the Update object manually or via de_json
            # However, PTB (Python Telegram Bot) Application handles this better.
            # For serverless, we often just use the Bot and manual routing 
            # to avoid the overhead of the full 'Application' polling loop,
            # but using Application is cleaner for context.
            
            asyncio.run(self.process_update(update_data))

            # 3. Respond 200 OK to Telegram (Crucial!)
            # If we don't, Telegram will keep retrying and spamming us.
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            
        except Exception as e:
            logger.error(f"Critical Error: {e}")
            self.send_response(200) 
            self.end_headers()
            self.wfile.write(b"OK")

    def do_GET(self):
        """Sanity check to see if the server is running"""
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Guild System Bot is Active.")

    async def process_update(self, update_json):
        """
        Async wrapper to initialize the bot and route the update.
        """
        # Initialize Bot/App
        # Note: In a high-traffic production app, we might cache this 
        # application instance globally to reuse warm containers.
        application = Application.builder().token(TOKEN).build()
        
        # Deserialize
        update = Update.de_json(update_json, application.bot)
        
        # Initialize the Context (Manually for serverless dispatch)
        # We cheat slightly here by using the application context manager
        async with application:
             # Manually trigger our router
             # We create a pseudo-context or just pass the bot if needed. 
             # For this architecture, we pass the application's context.
             # Note: route_update expects (Update, Context).
             # We can construct a context or simplify route_update to just take 'bot'.
             # To stick to the plan, we let Application handle the update via process_update
             # OR we call our router directly if we didn't add it as a handler.
             
             # Simpler approach for Serverless:
             # Just call our logic function directly.
             await route_update(update, application)
