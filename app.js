import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore, collection, onSnapshot } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

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

// On écoute la collection sans aucun filtre compliqué pour l'instant
onSnapshot(collection(db, "refurb_products"), (snap) => {
    list.innerHTML = "";
    if (snap.empty) {
        list.innerHTML = "<p class='text-center py-10'>La base de données est vide...</p>";
        return;
    }
    
    snap.forEach(doc => {
        const item = doc.data();
        list.innerHTML += `
            <div style="background:white; padding:20px; border-radius:15px; margin-bottom:10px; border:1px solid #eee">
                <h2 style="font-size:18px; margin:0">${item.name}</h2>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:15px">
                    <b style="font-size:20px">${item.price} €</b>
                    <a href="${item.url}" target="_blank" style="background:#0071e3; color:white; padding:8px 15px; border-radius:8px; text-decoration:none">Acheter</a>
                </div>
            </div>`;
    });
});