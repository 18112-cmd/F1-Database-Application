'use strict';

// 06) Import Firebase libraries
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";

// ✅ Your Firebase config from the console
const firebaseConfig = {
  apiKey: "AIzaSyDBLWm1sEPaQdtkfT8aZYQ-dwcQSxMCoEM",
  authDomain: "babi-454114.firebaseapp.com",
  projectId: "babi-454114",
  storageBucket: "babi-454114.firebasestorage.app",
  messagingSenderId: "638364778061",
  appId: "1:638364778061:web:e3da39b603e1b503dbe604"
};

// 07) Initialize Firebase and handle events
window.addEventListener("load", function () {
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  updateUI(document.cookie);
  console.log("hello world load");

  // Sign up new user
  document.getElementById("sign-up").addEventListener("click", function () {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    createUserWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        const user = userCredential.user;
        user.getIdToken().then((token) => {
          document.cookie = "token=" + token + ";path=/;SameSite=Strict";
          window.location = "/";
        });
      })
      .catch((error) => {
        console.log(error.code + " " + error.message);
      });
  });

  // 08) Login user
  document.getElementById("login").addEventListener("click", function () {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        const user = userCredential.user;
        console.log("logged in");
        user.getIdToken().then((token) => {
          document.cookie = "token=" + token + ";path=/;SameSite=Strict";
          window.location = "/";
        });
      })
      .catch((error) => {
        console.log(error.code + " " + error.message);
      });
  });

  // 09) Sign out user
  document.getElementById("sign-out").addEventListener("click", function () {
    signOut(auth)
      .then(() => {
        document.cookie = "token=;path=/;SameSite=Strict";
        window.location = "/";
      });
  });
});

// 10) Update UI based on login status
function updateUI(cookie) {
  var token = parseCookieToken(cookie);

  if (token.length > 0) {
    document.getElementById("login-box").hidden = true;
    document.getElementById("sign-out").hidden = false;
  } else {
    document.getElementById("login-box").hidden = false;
    document.getElementById("sign-out").hidden = true;
  }
}

// 11) Parse cookie for token
function parseCookieToken(cookie) {
  var strings = cookie.split(';');
  for (let i = 0; i < strings.length; i++) {
    var temp = strings[i].split('=');
    if (temp[0].trim() == "token")
      return temp[1];
  }
  return "";
}
