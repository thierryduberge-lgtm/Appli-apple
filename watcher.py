
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
    """Analyse complète du Refurb Apple."""
    # Cette URL est plus globale pour éviter les erreurs de catégorie
    url = "https://www.apple.com/fr/shop/refurbished/v1/portal/model/mac"
    
    print(f"[{datetime.now()}] Scan global en cours...")

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # Apple utilise souvent 'added' ou 'products'
        products = data.get('added', []) or data.get('products', [])
        
        if not products:
            print("Apple ne renvoie aucun produit en ce moment.")
            return

        found = 0
        for p in products:
            name = p.get('name', 'Produit sans nom')
            # Gestion plus robuste du prix
            price_data = p.get('price', {})
            raw_price = price_data.get('amount', '0').replace(',', '.')
            price = float(raw_price)
            
            product_url = "https://www.apple.com" + p.get('productUrl', '')
            product_id = p.get('partNumber', 'id_' + str(found))

            # On enregistre TOUT sans filtre pour vérifier que ça marche
            db.collection('refurb_products').document(product_id).set({
                'name': name,
                'price': price,
                'url': product_url,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            found += 1
            print(f"Enregistré : {name}")
        
        print(f"Succès ! {found} produits envoyés à Firebase.")

    except Exception as e:
        print(f"Erreur durant le scan : {e}")