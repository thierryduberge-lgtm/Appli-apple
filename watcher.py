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
    # On utilise l'URL de l'API de store d'Apple
    url = "https://www.apple.com/fr/shop/refurbished/v1/portal/model/mac"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # On cherche partout où Apple peut cacher ses produits
        sections = data.get('added', []) or data.get('products', []) or data.get('tiles', [])
        
        if not sections:
            print("Aucun produit trouvé dans les données Apple.")
            return

        for p in sections:
            name = p.get('name') or p.get('productTitle')
            if not name: continue
            
            price_info = p.get('price', {})
            # Nettoyage du prix (on enlève '€', les espaces, etc.)
            amount = str(price_info.get('amount', '0')).replace(',', '.').replace('\xa0', '')
            price = float(amount)
            
            product_url = "https://www.apple.com" + p.get('productUrl', '')
            product_id = p.get('partNumber', name[:10])

            db.collection('refurb_products').document(product_id).set({
                'name': name,
                'price': price,
                'url': product_url,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            print(f"OK : {name}")
            
    except Exception as e:
        print(f"Erreur de scan : {e}")

if __name__ == "__main__":
    db = initialize_firebase()
    if db:
        check_apple_refurb(db)