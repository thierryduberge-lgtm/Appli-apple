import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, query, orderBy, onSnapshot } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

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
const list = document.getElementById('product-list');

let filter = 'all';
let data = [];

// Fonction pour afficher les cartes
const show = () => {
    list.innerHTML = "";
    const filtered = data.filter(item => filter === 'all' || item.name.toLowerCase().includes(filter.toLowerCase()));
    
    if (filtered.length === 0) {
        list.innerHTML = `<p class="text-center py-10 text-gray-400">Aucun produit disponible...</p>`;
        return;
    }

    filtered.forEach(item => {
        list.innerHTML += `
            <div class="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 mb-4">
                <h2 class="text-lg font-medium">${item.name}</h2>
                <div class="flex justify-between items-center mt-4">
                    <p class="text-2xl font-bold">${item.price} €</p>
                    <a href="${item.url}" target="_blank" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">Acheter</a>
                </div>
            </div>`;
    });
};

// Gestion des boutons
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('bg-black', 'text-white'));
        btn.classList.add('bg-black', 'text-white');
        filter = btn.getAttribute('data-filter');
        show();
    });
});

// Écoute Firebase
onSnapshot(query(collection(db, "refurb_products"), orderBy("timestamp", "desc")), (snap) => {
    data = snap.docs.map(doc => doc.data());
    show();
});