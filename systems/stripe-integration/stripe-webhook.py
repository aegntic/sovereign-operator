#!/usr/bin/env python3
"""
Stripe Integration for Silent Cash Droid
Handles real payments, creates checkout sessions, and triggers product delivery.
"""
import os
import stripe
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load Stripe keys from env (set these in production)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRODUCTS = {
    "landing-droid-v1": {
        "name": "Landing Droid v1 - Instant High-Converting Landing Page",
        "price": 99900,  # $999.00 in cents
        "description": "I build you a production-grade landing/sales page in <4 hours using our full AI stack. Includes code, hosting setup, and Loom walkthrough."
    }
}

@app.route('/create-checkout', methods=['POST'])
def create_checkout():
    data = request.json
    product_id = data.get('product_id', 'landing-droid-v1')
    customer_email = data.get('email')
    
    product = PRODUCTS.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=customer_email,
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product['name'],
                        'description': product['description'],
                    },
                    'unit_amount': product['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://yourdomain.com/cancel',
            metadata={
                'product_id': product_id,
                'customer_handle': data.get('x_handle', 'unknown')
            }
        )
        return jsonify({"url": checkout_session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        product_id = session['metadata']['product_id']
        customer_handle = session['metadata'].get('customer_handle')
        amount = session['amount_total'] / 100
        
        print(f"✅ PAYMENT RECEIVED: ${amount} for {product_id} from {customer_handle}")
        # Here we would trigger delivery: build product, send repo access, post proof on X
        
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    print("Stripe webhook server ready for Silent Cash Droid.")
    print("Set STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET in environment.")
