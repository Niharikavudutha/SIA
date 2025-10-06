// // // working // //
// // const botAvatar = document.getElementById("bot-avatar");
// // const botStatus = document.getElementById("bot-status");
// // const siaOutput = document.getElementById("sia-output");
// // const video = document.getElementById("video");
// // const canvas = document.getElementById("canvas");


// // // 🎙️ Wake Word Setup
// // const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

// // if (!SpeechRecognition) {
// //   alert("Your browser does not support Speech Recognition. Please use Google Chrome.");
// // } else {
// //   const recognition = new SpeechRecognition();
// //   recognition.continuous = true;
// //   recognition.lang = 'en-US';
// //   recognition.interimResults = false;

// //   recognition.onstart = () => {
// //     console.log("🎤 Voice recognition started");
// //     siaOutput.innerText = "🎤 Listening...";
// //   };

// //   recognition.onresult = async (event) => {
// //     const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
// //     // console.log("🗣️ Heard:", transcript);
// //     siaOutput.innerText = `You said: "${transcript}"`;

// //     const triggers = [
// //       "hi sia", "hello sia", "hey sia", "ok sia", "start sia",
// //       "hi siya", "hello siya", "hey siya", "ok siya", "start siya",
// //       "sia", "siya","hello"
// //     ];

// //     if (triggers.some(trigger => transcript.includes(trigger))) {
// //       botStatus.innerText = "🟢 Wake word detected. Recognizing face...";
// //       await startCameraAndRecognizeFace();
// //     }
// //   };

// //   recognition.onerror = (e) => {
// //     console.error("❌ Recognition error:", e);
// //     siaOutput.innerText = "Error: " + e.error;
// //   };

// //   recognition.onend = () => {
// //     console.warn("🔁 Restarting recognition...");
// //     recognition.start();
// //   };

// //   recognition.start();
// // }

// // // 📷 Face Recognition Logic
// // async function startCameraAndRecognizeFace() {
// //   try {
// //     if (!video) {
// //       console.error("❌ Video element not found.");
// //       botStatus.innerText = "Camera error: element missing.";
// //       return;
// //     }

// //     const stream = await navigator.mediaDevices.getUserMedia({ video: true });
// //     video.srcObject = stream;

// //     await new Promise(resolve => setTimeout(resolve, 2000));

// //     canvas.width = video.videoWidth;
// //     canvas.height = video.videoHeight;
// //     const ctx = canvas.getContext("2d");
// //     ctx.drawImage(video, 0, 0);

// //     stream.getTracks().forEach(track => track.stop());

// //     const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));
// //     const formData = new FormData();
// //     formData.append("file", blob, "snapshot.jpg");

// //     const res = await fetch("/recognize-face", {
// //       method: "POST",
// //       body: formData,
// //     });

// //     const data = await res.json();

// //     if (data.success && data.name) {
// //       botStatus.innerText = `✅ Welcome ${data.name}`;

// //       // 🔊 Audio Greeting
// //       if (data.audio_base64) {
// //         const audio = new Audio("data:audio/mp3;base64," + data.audio_base64);
// //         audio.play();
// //       }

// //       // 🧭 Redirection
// //       if (data.redirect_url) {
// //         // Redirect to template page if card info is present
// //         setTimeout(() => {
// //           window.location.href = data.redirect_url;
// //         }, 4000);
// //       } else {
// //         // Fallback to chat page
// //         setTimeout(() => {
// //           window.location.href = `/chat?name=${encodeURIComponent(data.name)}`;
// //         }, 4000);
// //       }

// //     } else {
// //       botStatus.innerText = "❌ Face not recognized. Say 'Hi SIA' again.";
// //     }

// //   } catch (err) {
// //     console.error("❌ Face recognition failed:", err);
// //     botStatus.innerText = "Face recognition error.";
// //   }
// // }
// // // working // //

// // // working with index.html // //
// const botAvatar = document.getElementById("bot-avatar");
// const botStatus = document.getElementById("bot-status");
// const siaOutput = document.getElementById("sia-output");
// const video = document.getElementById("video");
// const canvas = document.getElementById("canvas");

// // 🎙️ Wake Word Setup
// const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

// if (!SpeechRecognition) {
//   alert("Your browser does not support Speech Recognition. Please use Google Chrome.");
// } else {
//   const recognition = new SpeechRecognition();
//   recognition.continuous = true;
//   recognition.lang = 'en-US';
//   recognition.interimResults = false;

//   recognition.onstart = () => {
//     console.log("🎤 Voice recognition started");
//     siaOutput.innerText = "🎤 Listening...";
//   };

//   recognition.onresult = async (event) => {
//     const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
//     siaOutput.innerText = `You said: "${transcript}"`;

//     const triggers = [
//       "hi sia", "hello sia", "hey sia", "ok sia", "start sia",
//       "hi siya", "hello siya", "hey siya", "ok siya", "start siya",
//       "sia", "siya", "hello"
//     ];

//     if (triggers.some(trigger => transcript.includes(trigger))) {
//       botStatus.innerText = "🟢 Wake word detected. Recognizing face...";
//       await startCameraAndRecognizeFace();
//     }
//   };

//   recognition.onerror = (e) => {
//     console.error("❌ Recognition error:", e);
//     siaOutput.innerText = "Error: " + e.error;
//   };

//   recognition.onend = () => {
//     console.warn("🔁 Restarting recognition...");
//     recognition.start();
//   };

//   recognition.start();
// }

// // 📷 Face Recognition Logic
// async function startCameraAndRecognizeFace() {
//   try {
//     if (!video) {
//       console.error("❌ Video element not found.");
//       botStatus.innerText = "Camera error: element missing.";
//       return;
//     }

//     const stream = await navigator.mediaDevices.getUserMedia({ video: true });
//     video.srcObject = stream;

//     await new Promise(resolve => setTimeout(resolve, 2000));

//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;
//     const ctx = canvas.getContext("2d");
//     ctx.drawImage(video, 0, 0);

//     stream.getTracks().forEach(track => track.stop());

//     const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));
//     const formData = new FormData();
//     formData.append("file", blob, "snapshot.jpg");

//     const res = await fetch("/recognize-face", {
//       method: "POST",
//       body: formData,
//     });

//     const data = await res.json();

//     if (data.success && data.name) {
//       // ✅ Known User
//       botStatus.innerText = `✅ Welcome ${data.name}`;

//       // 🔊 Audio Greeting
//       if (data.audio_base64) {
//         const audio = new Audio("data:audio/mp3;base64," + data.audio_base64);
//         audio.play();
//       }

//       // 🧭 Redirect
//       // setTimeout(() => {
//       //   window.location.href = data.redirect_url
//       //     ? data.redirect_url
//       //     : `/chat?name=${encodeURIComponent(data.name)}`;
//       // }, 4000);
//       setTimeout(() => {
//         const name = encodeURIComponent(data.name);
//         window.location.href = `/facerecog?name=${name}`;
//       }, 2000);


//     } else {
//       // ❌ Unknown / Not recognized
//       botStatus.innerText = "👋 Welcome to TechProjects! We couldn't recognize you. Please register using the scanner.";

//       // 🔊 Optional Audio Greeting
//       const welcomeAudio = new SpeechSynthesisUtterance("Welcome to TechProjects! Please register yourself using the scanner so I can remember you. Now, I am redirecting you to SIA for a conversation.");
//       speechSynthesis.speak(welcomeAudio);

//       // 🧭 Redirect to chat with suggestion to register
//       setTimeout(() => {
//         window.location.href = `/chat?name=Guest&register=true`;
//       }, 5000);
//     }

//   } catch (err) {
//     console.error("❌ Face recognition failed:", err);
//     botStatus.innerText = "Face recognition error.";
//   }
// }
// // // // working with index.html // //

// const botStatus = document.getElementById("bot-status");
// const siaOutput = document.getElementById("sia-output");
// const video = document.getElementById("video");
// const canvas = document.getElementById("canvas");

// // Detect current page
// const currentPage = window.location.pathname;

// // =========================
// // 🎙️ Wake Word (Scanpage)
// // =========================
// if (currentPage.includes("/scan")) {
//   const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

//   if (!SpeechRecognition) {
//     alert("Your browser does not support Speech Recognition. Please use Google Chrome.");
//   } else {
//     const recognition = new SpeechRecognition();
//     recognition.continuous = true;
//     recognition.lang = "en-US";
//     recognition.interimResults = false;

//     recognition.onstart = () => {
//       console.log("🎤 Voice recognition started");
//       if (siaOutput) siaOutput.innerText = "🎤 Listening...";
//     };

//     recognition.onresult = (event) => {
//       const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
//       if (siaOutput) siaOutput.innerText = `You said: "${transcript}"`;

//       const triggers = [
//         "hi sia", "hello sia", "hey sia", "ok sia", "start sia",
//         "hi siya", "hello siya", "hey siya", "ok siya", "start siya",
//         "sia", "siya", "hello"
//       ];

//       if (triggers.some(trigger => transcript.includes(trigger))) {
//         if (botStatus) botStatus.innerText = "🟢 Wake word detected. Redirecting to face recognition...";
//         console.log("Wake word detected → redirecting to /facerecog");

//         setTimeout(() => {
//           window.location.href = "/facerecog";
//         }, 1500);
//       }
//     };

//     recognition.onerror = (e) => {
//       console.error("❌ Recognition error:", e);
//       if (siaOutput) siaOutput.innerText = "Error: " + e.error;
//     };

//     recognition.onend = () => {
//       console.warn("🔁 Restarting recognition...");
//       recognition.start();
//     };

//     recognition.start();
//   }
// }

// // ==============================
// // 📷 Face Recognition (Facerecog)
// // ==============================
// if (currentPage.includes("/facerecog")) {
//   window.addEventListener("load", () => {
//     setTimeout(() => {
//       startCameraAndRecognizeFace();
//     }, 1000); // slight delay after page load
//   });
// }

// async function startCameraAndRecognizeFace() {
//   try {
//     if (!video || !canvas) {
//       console.error("❌ Video/Canvas elements missing.");
//       if (botStatus) botStatus.innerText = "Camera error: element missing.";
//       return;
//     }

//     const stream = await navigator.mediaDevices.getUserMedia({ video: true });
//     video.srcObject = stream;

//     // wait for camera to settle
//     await new Promise(resolve => setTimeout(resolve, 2000));

//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;
//     const ctx = canvas.getContext("2d");
//     ctx.drawImage(video, 0, 0);

//     stream.getTracks().forEach(track => track.stop());

//     const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));
//     const formData = new FormData();
//     formData.append("file", blob, "snapshot.jpg");

//     if (botStatus) botStatus.innerText = "🔍 Recognizing face...";

//     const res = await fetch("/recognize-face", {
//       method: "POST",
//       body: formData,
//     });

//     const data = await res.json();

//     if (data.success && data.name) {
//       // ✅ Known User
//       if (botStatus) botStatus.innerText = `✅ Welcome ${data.name}`;

//       // 🔊 Audio Greeting
//       if (data.audio_base64) {
//         const audio = new Audio("data:audio/mp3;base64," + data.audio_base64);
//         audio.play();
//       }

//       // 🧭 Redirect
//       setTimeout(() => {
//         const name = encodeURIComponent(data.name);
//         window.location.href = `/chat?name=${name}`;
//       }, 4000);

//     } else {
//       // ❌ Unknown User
//       if (botStatus) botStatus.innerText = "👋 Couldn't recognize you. Please register with the scanner.";

//       const welcomeAudio = new SpeechSynthesisUtterance(
//         "Welcome to TechProjects! Please register yourself using the scanner so I can remember you. Now, I am redirecting you to SIA for a conversation."
//       );
//       speechSynthesis.speak(welcomeAudio);

//       // 🧭 Redirect to chat with Guest
//       setTimeout(() => {
//         window.location.href = `/chat?name=Guest&register=true`;
//       }, 5000);
//     }

//   } catch (err) {
//     console.error("❌ Face recognition failed:", err);
//     if (botStatus) botStatus.innerText = "Face recognition error.";
//   }
// }
const botStatus = document.getElementById("bot-status");
const siaOutput = document.getElementById("sia-output");
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");

// Detect current page
const currentPage = window.location.pathname;

// =========================
// 🎙️ Wake Word (Scanpage)
// =========================
if (currentPage.includes("/scan")) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    alert("Your browser does not support Speech Recognition. Please use Google Chrome.");
  } else {
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.lang = "en-US";
    recognition.interimResults = false;

    recognition.onstart = () => {
      console.log("🎤 Voice recognition started");
      if (siaOutput) siaOutput.innerText = "🎤 Listening...";
    };

    recognition.onresult = (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
      if (siaOutput) siaOutput.innerText = `You said: "${transcript}"`;

      const triggers = [
        "hi sia", "hello sia", "hey sia", "ok sia", "start sia",
        "hi siya", "hello siya", "hey siya", "ok siya", "start siya",
        "sia", "siya", "hello"
      ];

      if (triggers.some(trigger => transcript.includes(trigger))) {
        if (botStatus) botStatus.innerText = "🟢 Wake word detected. Redirecting to face recognition...";
        console.log("Wake word detected → redirecting to /facerecog");

        setTimeout(() => {
          window.location.href = "/facerecog";
        }, 1500);
      }
    };

    recognition.onerror = (e) => {
      console.error("❌ Recognition error:", e);
      if (siaOutput) siaOutput.innerText = "Error: " + e.error;
    };

    recognition.onend = () => {
      console.warn("🔁 Restarting recognition...");
      recognition.start();
    };

    recognition.start();
  }
}

// ==============================
// 📷 Face Recognition (Facerecog)
// ==============================
if (currentPage.includes("/facerecog")) {
  window.addEventListener("load", () => {
    setTimeout(() => {
      startCameraAndRecognizeFace();
    }, 1000); // slight delay after page load
  });
}

async function startCameraAndRecognizeFace() {
  try {
    if (!video || !canvas) {
      console.error("❌ Video/Canvas elements missing.");
      if (botStatus) botStatus.innerText = "Camera error: element missing.";
      return;
    }

    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;

    // wait for camera to settle
    await new Promise(resolve => setTimeout(resolve, 2000));

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    stream.getTracks().forEach(track => track.stop());

    const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));
    const formData = new FormData();
    formData.append("file", blob, "snapshot.jpg");

    if (botStatus) botStatus.innerText = "🔍 Recognizing face...";

    const res = await fetch("/recognize-face", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (data.success && data.name) {
      // ✅ Known User
      if (botStatus) botStatus.innerText = `✅ Welcome ${data.name}`;

      // 🔊 Audio Greeting
      if (data.audio_base64) {
        const audio = new Audio("data:audio/mp3;base64," + data.audio_base64);
        audio.play();
      }

      // 🧭 Redirect
      setTimeout(() => {
        const name = encodeURIComponent(data.name);
        window.location.href = `/chat?name=${name}`;
      }, 4000);

    } 
    // else {
    //   // ❌ Unknown User
    //   if (botStatus) botStatus.innerText = "New Human Detected.     You look awesome but I dont";

    //   const welcomeAudio = new SpeechSynthesisUtterance(
    //     "Welcome to TechProjects! Please register yourself using the scanner so I can remember you. Now, I am redirecting you to SIA for a conversation."
    //   );
    //   speechSynthesis.speak(welcomeAudio);

    //   // 🧭 Redirect to chat with Guest
    //   setTimeout(() => {
    //     window.location.href = `/chat?name=Guest&register=true`;
    //   }, 5000);
    // }
    else {
      // ❌ Unknown User

      // Define random messages
      const unknownMessages = [
        {
          header: "🤔 Oops… My memory must be on a coffee break!",
          body: "I don’t recognize you yet. Want to register so I can greet you properly next time?"
        },
        {
          header: "😅 Are you undercover?",
          body: "I can’t seem to recognize you. Don’t worry, it happens! Just register your face now, and next time I’ll roll out the red carpet."
        },
        {
          header: "👋 Hey Stranger!",
          body: "You’re not in my system yet, but I’d love to know you! Let’s register your face — future me will remember you instantly."
        }
      ];

      // Pick random message
      const randomMsg = unknownMessages[Math.floor(Math.random() * unknownMessages.length)];

      // Show on screen
      if (botStatus) botStatus.innerText = `${randomMsg.header}\n${randomMsg.body}`;

      // Speak the body text
      const welcomeAudio = new SpeechSynthesisUtterance(
        randomMsg.body + " Now, I am redirecting you to SIA for a conversation."
      );
      speechSynthesis.speak(welcomeAudio);

      // 🧭 Redirect to chat with Guest
      setTimeout(() => {
        window.location.href = `/chat?name=Guest&register=true`;
      }, 5000);
    }


  } catch (err) {
    console.error("❌ Face recognition failed:", err);
    if (botStatus) botStatus.innerText = "Face recognition error.";
  }
}
