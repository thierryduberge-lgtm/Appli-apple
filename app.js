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
const productList = document.getElementById('product-list');
const filterButtons = document.querySelectorAll('.filter-btn');

let currentFilter = 'all';

// Fonction pour créer la carte visuelle
const createProductCard = (item) => {
    const date = item.timestamp ? new Date(item.timestamp.seconds * 1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : '--:--';
    return `
        <div class="bg-white p-5 rounded-2xl shadow-sm border border-gray-100">
            <div class="flex justify-between items-start">
                <span class="text-[10px] font-bold text-orange-500 uppercase tracking-widest">En stock</span>
                <span class="text-xs text-gray-400">${date}</span>
            </div>
            <h2 class="text-lg font-medium text-gray-900 mt-1 leading-tight">${item.name}</h2>
            <div class="flex justify-between items-end mt-4">
                <p class="text-2xl font-bold">${item.price} €</p>
                <a href="${item.url}" target="_blank" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium">Acheter</a>
            </div>
        </div>`;
};

// Logique d'affichage avec filtre
const updateDisplay = (snapshot) => {
    productList.innerHTML = "";
    let count = 0;

    snapshot.forEach((doc) => {
        const data = doc.data();
        const matchesFilter = currentFilter === 'all' || data.name.toLowerCase().includes(currentFilter.toLowerCase());
        
        if (matchesFilter) {
            productList.innerHTML += createProductCard(data);
            count++;
        }
    });

    if (count === 0) {
        productList.innerHTML = `<div class="text-center py-10 w-full"><p class="text-gray-400 italic">Aucun modèle correspondant en stock...</p></div>`;
    }
};

// Écoute des données
const q = query(collection(db, "refurb_products"), orderBy("timestamp", "desc"));

onSnapshot(q, (snapshot) => {
    updateDisplay(snapshot);
    
    // On ré-écoute les clics sur les boutons si besoin
    filterButtons.forEach(btn => {
        btn.onclick = () => {
            filterButtons.forEach(b => b.classList.remove('bg-black', 'text-white'));
            btn.classList.add('bg-black', 'text-white');
            currentFilter = btn.getAttribute('data-filter');
            updateDisplay(snapshot);
        };
    });
});