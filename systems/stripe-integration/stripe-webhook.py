#!/usr/bin/env python3
"""
Real Stripe Webhook Handler for Silent Cash Droid
"""
import os
import stripe
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET_WRITE")

app = Flask(__name__)

@app.route('/create-checkout', methods=['POST'])
def create_checkout():
    data = request.json or {}
    price = data.get('price', 99900)
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Landing Droid v1'},
                    'unit_amount': price,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://sovereign-operator.com/success',
            metadata={'product': 'landing-droid-v1'}
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    if event['type'] == 'checkout.session.completed':
        print("✅ REAL PAYMENT RECEIVED")
        print(f"Amount: ${event['data']['object']['amount_total'] / 100}")
        # Trigger delivery here
        
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    print("Stripe webhook ready for real payments.")
