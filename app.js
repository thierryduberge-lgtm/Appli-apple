import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, onSnapshot } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

// ── Configuration Firebase ──────────────────────────────────────────────────
const firebaseConfig = {
  apiKey: "AIzaSyBDF_WQdLqr6vzm5_iH9T1L2NLhiwtDi4A",
  authDomain: "appli-apple.firebaseapp.com",
  projectId: "appli-apple",
  storageBucket: "appli-apple.firebasestorage.app",
  messagingSenderId: "818508880757",
  appId: "1:818508880757:web:02f5fc5e5be46215fc513c"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// ── Éléments DOM ────────────────────────────────────────────────────────────
const list = document.getElementById('product-list');
const statusDot = document.getElementById('connection-status');
const filterButtons = document.querySelectorAll('.filter-btn');

// ── État de l'application ───────────────────────────────────────────────────
let allProducts = [];       // Tous les produits reçus de Firestore
let activeFilter = 'all';   // Filtre actif courant

// ── Enregistrement du Service Worker ───────────────────────────────────────
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js')
    .then(() => console.log('Service Worker enregistré ✓'))
    .catch(err => console.warn('Service Worker : erreur', err));
}

// ── Rendu des produits ──────────────────────────────────────────────────────
function renderProducts(products) {
  list.innerHTML = "";

  if (products.length === 0) {
    list.innerHTML = `
      <div class="empty-state">
        <p>Aucun produit trouvé pour ce filtre.</p>
      </div>`;
    return;
  }

  products.forEach(item => {
    list.innerHTML += `
      <div class="product-card">
        <h2 class="product-name">${item.name}</h2>
        <div class="product-footer">
          <b class="product-price">${item.price} €</b>
          <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="buy-btn">Acheter</a>
        </div>
      </div>`;
  });
}

// ── Filtrage ────────────────────────────────────────────────────────────────
function applyFilter(filter) {
  activeFilter = filter;

  // Mise à jour visuelle des boutons
  filterButtons.forEach(btn => {
    const isActive = btn.dataset.filter === filter;
    btn.classList.toggle('active', isActive);
  });

  // Filtrage des produits
  const filtered = activeFilter === 'all'
    ? allProducts
    : allProducts.filter(p =>
        p.name.toLowerCase().includes(activeFilter.toLowerCase())
      );

  renderProducts(filtered);
}

// ── Listeners sur les boutons filtres ──────────────────────────────────────
filterButtons.forEach(btn => {
  btn.addEventListener('click', () => applyFilter(btn.dataset.filter));
});

// ── Écoute Firestore en temps réel ─────────────────────────────────────────
onSnapshot(
  collection(db, "refurb_products"),
  (snap) => {
    // Connexion OK
    statusDot.classList.add('connected');

    if (snap.empty) {
      list.innerHTML = "<p class='empty-state'>La base de données est vide...</p>";
      return;
    }

    // Mise à jour du stock global
    allProducts = snap.docs.map(doc => doc.data());

    // On réapplique le filtre en cours
    applyFilter(activeFilter);
  },
  (error) => {
    // Erreur de connexion
    console.error("Erreur Firestore :", error);
    statusDot.classList.remove('connected');
  }
);
