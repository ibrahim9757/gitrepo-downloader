// mail.js

// Session Management: Generate a unique ID for this user's browser session
let sessionID = localStorage.getItem('userSessionID');
if (!sessionID) {
    sessionID = Date.now().toString(36) + Math.random().toString(36).substring(2);
    localStorage.setItem('userSessionID', sessionID);
}

// FIX: Wrap all logic in DOMContentLoaded to ensure elements exist and fix the Scope Error
document.addEventListener('DOMContentLoaded', () => {

    // --- Access Firestore ---
    // Access the 'db' variable set globally in the HTML script block
    const db = window.db; 

    // --- DOM ELEMENTS (Declared safely inside this scope) ---
    const welcomeModal = document.getElementById('welcomeModal');
    const mainContent = document.getElementById('mainContent');
    const emailInput = document.getElementById('emailInput');
    const continueBtn = document.getElementById('continueBtn');
    const emailError = document.getElementById('emailError');
    const repoUrlInput = document.getElementById('repoUrl');
    const loadRepoBtn = document.getElementById('loadRepoBtn');
    const downloadAllBtn = document.getElementById('downloadAllBtn');

    // --- DATABASE FUNCTION ---
    async function updateSessionData(data) {
        if (!sessionID || !db) return;
        
        try {
            await db.collection("userSessions").doc(sessionID).set({
                ...data,
                lastUpdated: firebase.firestore.FieldValue.serverTimestamp()
            }, { merge: true });
            console.log("Data saved successfully for Session ID:", sessionID);
        } catch (error) {
            console.error("Error saving data to Firestore:", error);
        }
    }

    // --- UI UPDATE FUNCTION ---
    function updateUI() {
        const emailSaved = localStorage.getItem('sessionEmail');
        if (emailSaved) {
            welcomeModal.classList.add('hidden');
            mainContent.classList.remove('hidden');
        } else {
            welcomeModal.classList.remove('hidden');
            mainContent.classList.add('hidden');
        }
    }

    // --- EVENT LISTENERS ---

    // A. Handle Modal Submission (Capture Email)
    continueBtn.addEventListener('click', async () => {
        const email = emailInput.value.trim();
        const isValidEmail = email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

        if (!isValidEmail) {
            emailError.classList.remove('hidden');
            return;
        }
        
        emailError.classList.add('hidden');
        continueBtn.disabled = true;
        continueBtn.textContent = 'Saving...';

        await updateSessionData({ 
            email: email, 
            initialEntry: firebase.firestore.FieldValue.serverTimestamp()
        });

        localStorage.setItem('sessionEmail', email);
        updateUI(); 

        continueBtn.disabled = false;
        continueBtn.textContent = 'Continue';
    });


    // B. Handle Repo URL Submission (Capture GitHub Link)
    loadRepoBtn.addEventListener('click', async () => {
        const url = repoUrlInput.value.trim();
        
        if (!url || !url.includes("github.com")) {
            alert("Please enter a valid GitHub repository URL.");
            return;
        }
        
        loadRepoBtn.disabled = true;
        loadRepoBtn.textContent = 'Loading...';

        await updateSessionData({ 
            repoUrl: url,
            repoLoadedAt: firebase.firestore.FieldValue.serverTimestamp()
        });
        
        // Your GitHub API logic will go here
        
        downloadAllBtn.disabled = false;
        
        loadRepoBtn.disabled = false;
        loadRepoBtn.textContent = 'Load Repository';
    });

    // C. Placeholder for Download Button
    downloadAllBtn.addEventListener('click', () => {
        alert("Download functionality is not yet implemented!");
    });

    // --- INITIAL CALL ---
    updateUI();

});