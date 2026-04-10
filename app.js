
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, onSnapshot, query, orderBy } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

// Ma configuration Firebase
const firebaseConfig = {
    apiKey: "TON_API_KEY",
    authDomain: "TON_PROJET.firebaseapp.com",
    projectId: "TON_PROJET",
    storageBucket: "TON_PROJET.appspot.com",
    messagingSenderId: "...",
    appId: "..."
};

// Initialisation
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const productList = document.getElementById('product-list');

// Fonction pour créer le HTML d'une carte produit
const createProductCard = (item) => {
    const date = item.timestamp ? new Date(item.timestamp.seconds * 1000).toLocaleTimeString([], {hour: '2bit', minute:'2bit'}) : '--:--';
    
    return `
        <div class="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 animate-in fade-in duration-500">
            <div class="flex justify-between items-start">
                <span class="text-[10px] font-bold text-orange-500 uppercase tracking-widest">En stock</span>
                <span class="text-xs text-gray-400">${date}</span>
            </div>
            <h2 class="text-lg font-medium text-gray-900 mt-1 leading-tight">${item.name}</h2>
            <div class="flex justify-between items-end mt-4">
                <p class="text-2xl font-bold">${item.price} €</p>
                <a href="${item.url}" target="_blank" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium">
                    Acheter
                </a>
            </div>
        </div>
    `;
};

// Écoute des données
const q = query(collection(db, "refurb_products"), orderBy("timestamp", "desc"));

onSnapshot(q, (snapshot) => {
    productList.innerHTML = "";
    
    if (snapshot.empty) {
        productList.innerHTML = `
            <div class="text-center py-10">
                <p class="text-gray-400 italic">Aucun Mac disponible...</p>
            </div>
        `;
        return;
    }

    snapshot.forEach((doc) => {
        productList.innerHTML += createProductCard(doc.data());
    });
}, (error) => {
    console.error("Erreur Firestore:", error);
    document.getElementById('connection-status').classList.replace('bg-green-500', 'bg-red-500');
});