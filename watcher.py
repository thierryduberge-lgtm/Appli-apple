import requests
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

def initialize_firebase():
    service_account_env = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
    if service_account_env:
        info = json.loads(service_account_env)
        cred = credentials.Certificate(info)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        return firestore.client()
    return None

def check_apple_refurb(db):
    url = "https://www.apple.com/fr/shop/refurbished/mac"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        products = data.get('added', []) or data.get('products', [])
        
        if not products:
            print("Aucun produit chez Apple.")
            return

        for p in products:
            name = p.get('name')
            price = float(p.get('price', {}).get('amount', '0').replace(',', '.'))
            product_url = "https://www.apple.com" + p.get('productUrl', '')
            product_id = p.get('partNumber')

            # Enregistre dans Firebase
            db.collection('refurb_products').document(product_id).set({
                'name': name,
                'price': price,
                'url': product_url,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            print(f"Ajouté : {name}")
            
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    db = initialize_firebase()
    if db:
        check_apple_refurb(db)