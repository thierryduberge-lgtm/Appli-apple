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
    # Nouvelle URL plus fiable
    url = "https://www.apple.com/fr/shop/refurbished/v1/portal/model/mac"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        # On essaie de récupérer les produits peu importe où ils sont cachés dans le JSON
        products = data.get('added', []) or data.get('products', []) or data.get('tiles', [])
        
        if not products:
            print("Aucun produit trouvé chez Apple actuellement.")
            return

        for p in products:
            name = p.get('name') or p.get('productTitle')
            if not name: continue

            # Extraction propre du prix
            price_data = p.get('price', {})
            amount = str(price_data.get('amount', '0')).replace(',', '.')
            price = float(amount)
            
            product_url = "https://www.apple.com" + p.get('productUrl', '')
            product_id = p.get('partNumber', 'id_' + name[:5])

            # On envoie à Firebase
            db.collection('refurb_products').document(product_id).set({
                'name': name,
                'price': price,
                'url': product_url,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            print(f"Trouvé : {name}")
            
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    db = initialize_firebase()
    if db:
        check_apple_refurb(db)