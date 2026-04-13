import requests
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore, messaging
from datetime import datetime, timezone

# ── Initialisation Firebase ──────────────────────────────────────────────────
def initialize_firebase():
    service_account_env = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
    if not service_account_env:
        print("❌ Variable d'environnement FIREBASE_SERVICE_ACCOUNT manquante.")
        return None
    try:
        info = json.loads(service_account_env)
        cred = credentials.Certificate(info)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"❌ Erreur d'initialisation Firebase : {e}")
        return None

# ── Envoi d'une notification push via Firebase Cloud Messaging ───────────────
def send_push_notification(product_name: str, price: float):
    """
    Envoie une notification push à tous les abonnés du topic 'refurb_alerts'.
    Les appareils doivent s'abonner à ce topic côté frontend (voir app.js).
    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title="🍎 Nouveau produit reconditionné !",
                body=f"{product_name} — {price:.2f} €",
            ),
            topic="refurb_alerts",   # Tous les appareils abonnés reçoivent l'alerte
        )
        response = messaging.send(message)
        print(f"🔔 Notification envoyée : {response}")
    except Exception as e:
        print(f"⚠️  Erreur notification push : {e}")

# ── Scan de l'Apple Store Reconditionné ─────────────────────────────────────
def check_apple_refurb(db):
    url = "https://www.apple.com/fr/shop/refurbished/v1/portal/model/mac"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'fr-FR,fr;q=0.9',
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        print("❌ Timeout : Apple n'a pas répondu dans les délais.")
        return
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur HTTP {response.status_code} : {e}")
        return
    except json.JSONDecodeError:
        print("❌ La réponse d'Apple n'est pas du JSON valide.")
        return
    except Exception as e:
        print(f"❌ Erreur réseau inattendue : {e}")
        return

    # Recherche des produits dans la réponse
    sections = (
        data.get('added') or
        data.get('products') or
        data.get('tiles') or
        data.get('results') or
        []
    )

    if not sections:
        print(f"⚠️  Aucun produit trouvé. Clés disponibles : {list(data.keys())}")
        return

    print(f"✅ {len(sections)} produit(s) trouvé(s). Synchronisation en cours...")

    # ── Récupération des produits déjà connus en base ────────────────────────
    existing_ids = set()
    try:
        existing_docs = db.collection('refurb_products').stream()
        existing_ids = {doc.id for doc in existing_docs}
    except Exception as e:
        print(f"⚠️  Impossible de lire les produits existants : {e}")

    batch = db.batch()
    count = 0
    new_products = []   # Produits apparus pour la première fois → notification push

    for p in sections:
        try:
            name = p.get('name') or p.get('productTitle') or p.get('title')
            if not name:
                continue

            # Nettoyage robuste du prix
            price_info = p.get('price', {})
            amount_raw = str(price_info.get('amount', '0'))
            amount_clean = (
                amount_raw
                .replace(',', '.')
                .replace('\xa0', '')
                .replace(' ', '')
                .replace('€', '')
            )
            try:
                price = float(amount_clean)
            except ValueError:
                print(f"⚠️  Prix invalide pour '{name}' : {amount_raw!r} — ignoré.")
                continue

            product_url = p.get('productUrl', '')
            if product_url and not product_url.startswith('http'):
                product_url = "https://www.apple.com" + product_url

            product_id = (
                p.get('partNumber') or
                p.get('id') or
                name[:20].replace(' ', '_')
            )

            # Détection des nouveaux produits
            if product_id not in existing_ids:
                new_products.append({'name': name, 'price': price})
                print(f"🆕 Nouveau : {name} — {price:.2f} €")

            ref = db.collection('refurb_products').document(product_id)
            batch.set(ref, {
                'name': name,
                'price': price,
                'url': product_url,
                'last_seen': datetime.now(timezone.utc).isoformat(),
            })
            count += 1

        except Exception as e:
            print(f"⚠️  Erreur sur un produit : {e}")
            continue

    # ── Écriture atomique dans Firestore ─────────────────────────────────────
    if count > 0:
        try:
            batch.commit()
            print(f"✅ {count} produit(s) synchronisé(s) dans Firestore.")
        except Exception as e:
            print(f"❌ Erreur lors de l'écriture Firestore : {e}")
            return
    else:
        print("⚠️  Aucun produit valide à synchroniser.")
        return

    # ── Notifications push pour les nouveaux produits ────────────────────────
    for product in new_products:
        send_push_notification(product['name'], product['price'])

# ── Point d'entrée ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"🔍 Scan démarré à {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    db = initialize_firebase()
    if db:
        check_apple_refurb(db)
