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

let currentFilter = 'all';
let lastSnapshot = null;

const render = (snapshot) => {
    if (!snapshot) return;
    productList.innerHTML = "";
    let count = 0;

    snapshot.forEach((doc) => {
        const item = doc.data();
        const matches = currentFilter === 'all' || item.name.toLowerCase().includes(currentFilter.toLowerCase());
        
        if (matches) {
            const date = item.timestamp ? new Date(item.timestamp.seconds * 1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : '--:--';
            productList.innerHTML += `
                <div class="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 mb-4">
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
            count++;
        }
    });

    if (count === 0) productList.innerHTML = `<p class="text-center text-gray-400 italic py-10">Aucun produit trouvé...</p>`;
};

// Écoute des clics sur les boutons
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.filter-btn');
    if (!btn) return;

    document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.remove('bg-black', 'text-white');
        b.classList.add('bg-gray-100', 'text-gray-600');
    });
    btn.classList.add('bg-black', 'text-white');
    btn.classList.remove('bg-gray-100', 'text-gray-600');

    currentFilter = btn.getAttribute('data-filter');
    render(lastSnapshot);
});

// Connexion Firebase
const q = query(collection(db, "refurb_products"), orderBy("timestamp", "desc"));
onSnapshot(q, (snapshot) => {
    lastSnapshot = snapshot;
    render(snapshot);
});