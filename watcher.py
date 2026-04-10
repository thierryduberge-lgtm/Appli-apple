
import requests
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

def initialize_firebase():
    """Initialise la connexion à Firebase de manière sécurisée."""
    # Priorité 1 : On cherche le secret GitHub (pour la production)
    service_account_env = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
    
    if service_account_env:
        try:
            # On charge le JSON depuis la variable d'environnement
            info = json.loads(service_account_env)
            cred = credentials.Certificate(info)
            firebase_admin.initialize_app(cred)
            return firestore.client()
        except Exception as e:
            print(f"Erreur lors du chargement du secret : {e}")
            return None
    else:
        # Priorité 2 : On cherche un fichier local (pour tes tests sur ton iMac)
        # Assure-toi que le fichier s'appelle 'serviceAccountKey.json' localement
        try:
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
            return firestore.client()
        except:
            print("Erreur : Aucune méthode d'authentification trouvée.")
            return None

def check_apple_refurb(db):
    """Analyse le site d'Apple et met à jour Firestore."""
    # URL de l'API Refurb Apple France
    url = "https://www.apple.com/fr/shop/refurbished/v1/portal/model/mac"
    
    # Critères de recherche - À MODIFIER SELON TES ENVIES
    target_model = "MacBook Pro"
    max_price = 2200.0

    print(f"[{datetime.now()}] Scan en cours...")

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        response = requests.get(url, headers=headers)
        data = response.json()
        
        products = data.get('added', [])
        found = 0

        for p in products:
            name = p.get('name', '')
            # Nettoyage du prix (Apple renvoie parfois des strings avec des virgules)
            raw_price = p.get('price', {}).get('amount', '0').replace(',', '.')
            price = float(raw_price)
            product_url = "https://www.apple.com" + p.get('productUrl', '')
            product_id = p.get('partNumber', '')

            # Logique de filtrage
            if target_model.lower() in name.lower() and price <= max_price:
                print(f"Match trouvé : {name} à {price}€")
                
                # Mise à jour Firestore (idempotente)
                db.collection('refurb_products').document(product_id).set({
                    'name': name,
                    'price': price,
                    'url': product_url,
                    'timestamp': firestore.SERVER_TIMESTAMP
                })
                found += 1
        
        print(f"Scan terminé. {found} produits ajoutés/mis à jour.")

    except Exception as e:
        print(f"Erreur durant l'exécution : {e}")

if __name__ == "__main__":
    firestore_db = initialize_firebase()
    if firestore_db:
        check_apple_refurb(firestore_db)