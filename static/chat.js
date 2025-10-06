// console.log("🟢 SIA Chat.js Initialized");

// // DOM Elements
// const subtitleDiv = document.getElementById('subtitles');
// const voiceSelect = document.getElementById('voiceSelect');
// const stopBtn = document.getElementById('stopBtn');
// const chatBox = document.getElementById('chatBox');
// const micIndicator = document.getElementById("micIndicator");
// const loadingDiv = document.getElementById("loading");
// const startButton = document.getElementById('startButton');

// // Speech APIs
// const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
// const synth = window.speechSynthesis;

// // State Variables
// let selectedVoice = null;
// let voices = [];
// let isSpeaking = false;
// let isListening = false;

// // UI Helpers
// function showMic() {
//   if (micIndicator) micIndicator.style.display = "block";
// }

// function hideMic() {
//   if (micIndicator) micIndicator.style.display = "none";
// }

// function showLoading() {
//   if (loadingDiv) loadingDiv.style.display = "block";
// }

// function hideLoading() {
//   if (loadingDiv) loadingDiv.style.display = "none";
// }

// function addChatMessage(text, isUser = false) {
//   if (!chatBox) {
//     console.error("The chatBox element was not found in the HTML.");
//     return;
//   }
//   const messageDiv = document.createElement('div');
//   messageDiv.className = isUser ? 'user-message' : 'bot-message';
//   messageDiv.innerText = text;
//   chatBox.appendChild(messageDiv);
//   chatBox.scrollTop = chatBox.scrollHeight;
// }

// // Voice and Speaking Logic
// function loadVoicesAndSelect(defaultVoice = 'Google UK English Female') {
//   return new Promise((resolve) => {
//     function setVoices() {
//       voices = synth.getVoices();
//       voiceSelect.innerHTML = '';
//       let fallbackIndex = 0;

//       voices.forEach((voice, index) => {
//         const option = document.createElement('option');
//         option.value = index;
//         option.textContent = `${voice.name} (${voice.lang})`;
//         voiceSelect.appendChild(option);

//         if (voice.name.includes(defaultVoice)) {
//           option.selected = true;
//           selectedVoice = voice;
//         }
//         if (index === 0 && !selectedVoice) fallbackIndex = index;
//       });

//       if (!selectedVoice && voices.length > 0) {
//         selectedVoice = voices[fallbackIndex];
//         voiceSelect.value = fallbackIndex;
//       }
//       resolve();
//     }
//     if (synth.getVoices().length > 0) setVoices();
//     else synth.onvoiceschanged = setVoices;
//   });
// }

// function speakText(text) {
//   return new Promise((resolve) => {
//     if (isSpeaking) {
//       synth.cancel();
//     }

//     const utterance = new SpeechSynthesisUtterance(text);
//     utterance.voice = selectedVoice;
//     utterance.rate = 1;
//     utterance.pitch = 1;

//     utterance.onstart = () => {
//       isSpeaking = true;
//       stopBtn.disabled = false;
//       isListening = false;
//       hideMic();
//     };

//     utterance.onend = () => {
//       isSpeaking = false;
//       stopBtn.disabled = true;
//       setTimeout(startVoiceRecognition, 500);
//       resolve();
//     };

//     synth.speak(utterance);
//   });
// }

// // Voice Recognition Logic
// function startVoiceRecognition() {
//   if (!SpeechRecognition || !synth) {
//     subtitleDiv.innerText = "❌ Browser not supported. Please use Chrome.";
//     console.error("Browser does not support SpeechRecognition or SpeechSynthesis.");
//     return;
//   }

//   if (isListening || isSpeaking) return;

//   const recognition = new SpeechRecognition();
//   recognition.continuous = false;
//   recognition.lang = 'en-US';
//   recognition.interimResults = false;

//   isListening = true;
//   showMic();
//   subtitleDiv.innerText = "Listening...";
  
//   recognition.onstart = () => console.log("🎤 Voice recognition started.");

//   recognition.onerror = e => {
//     console.error("❌ Voice recognition error:", e.error);
//     if (e.error === 'no-speech' || e.error === 'network') {
//       subtitleDiv.innerText = "Listening timed out. Say something to restart.";
//     } else {
//       subtitleDiv.innerText = "⚠️ Voice error: " + e.error;
//     }
//     isListening = false;
//     hideMic();
//     setTimeout(startVoiceRecognition, 2000);
//   };

//   recognition.onend = () => {
//     isListening = false;
//     if (!isSpeaking) {
//       console.log("🔁 Recognition ended. Restarting...");
//       setTimeout(startVoiceRecognition, 500);
//     }
//   };

//   recognition.onresult = async (event) => {
//     const transcript = event.results[0][0].transcript.trim();
//     console.log("🎧 Heard:", transcript);
//     hideMic();
//     subtitleDiv.innerText = `You: ${transcript}`;
//     addChatMessage(transcript, true);

//     const exitCommands = ["exit", "go back", "quit", "bye", "close", "bye sia"];
//     if (exitCommands.some(cmd => transcript.toLowerCase().includes(cmd))) {
//       subtitleDiv.innerText = "👋 See you again!";
//       await speakText("Ok, see you again! Redirecting you to the main screen.");
//       window.location.href = "/";
//       return;
//     }

//     showLoading();
//     try {
//       const res = await fetch('/ask', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ question: transcript })
//       });
//       const data = await res.json();
//       const reply = data.answer || "Sorry, I don't know how to answer that.";

//       subtitleDiv.innerText = `SIA: ${reply}`;
//       addChatMessage(reply);
//       await speakText(reply);
//       hideLoading();
//     } catch (err) {
//       console.error("❌ Fetch error:", err);
//       subtitleDiv.innerText = "Something went wrong.";
//       hideLoading();
//     }
//   };

//   recognition.start();
// }

// // Event Listeners
// voiceSelect.addEventListener('change', () => {
//   selectedVoice = voices[parseInt(voiceSelect.value)];
// });

// stopBtn.addEventListener('click', () => {
//   synth.cancel();
//   isSpeaking = false;
//   stopBtn.disabled = true;
//   subtitleDiv.innerText = '';
//   startVoiceRecognition();
// });

// // Initialization
// (async function init() {
//   await loadVoicesAndSelect();
//   subtitleDiv.innerText = "Click 'Start Assistant' to begin.";
// })();

// // Start button listener
// startButton.addEventListener('click', async () => {
//   startButton.style.display = 'none';
//   const greeting = "Hi there! How can I help you today?";
//   subtitleDiv.innerText = greeting;
//   await speakText(greeting);
// });

// console.log("🟢 SIA Chat.js Initialized");
 
// // DOM Elements
// const subtitleDiv = document.getElementById('subtitles');
// const voiceSelect = document.getElementById('voiceSelect');
// const stopBtn = document.getElementById('stopBtn');
// const chatBox = document.getElementById('chatBox');
// const micIndicator = document.getElementById("micIndicator");
// const loadingDiv = document.getElementById("loading");
// const startButton = document.getElementById('startButton');
 
// // Speech APIs
// const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
// const synth = window.speechSynthesis;
 
// // State Variables
// let selectedVoice = null;
// let voices = [];
// let isSpeaking = false;
// let isListening = false;
 
// // --- Screen Navigation Keywords ---
// const screenRoutes = {
//   "holiday": "/holidays",
//   "holiday calendar": "/holidays",
//   "holidays": "/holidays",
 
//   "wishes": "/wishes-page",
//   "birthday": "/wishes-page",
//   "birthdays": "/wishes-page",
//   "anniversary": "/wishes-page",
//   "anniversaries": "/wishes-page",
 
//   "hr policies": "/hr",
//   "hr policy": "/hr",
 
//   "insurance": "/insurance",
//   "insurance policy": "/insurance",
 
//   "employee benefits": "/index", // replace if you have a dedicated page
//   "benefits": "/index",
 
//   "event": "../", // replace with dedicated event route if available
//   "upcoming event": "/index",
 
//   "office layout": "/office-layout",
//   "floor plan": "/office-layout",
 
//   "story": "/index", // replace with correct route if available
//   "our story": "/index",
 
//   "assistant": "/chat",
//   "sia": "/chat",
// };
 
// // UI Helpers
// function showMic() {
//   if (micIndicator) micIndicator.style.display = "block";
// }
// function hideMic() {
//   if (micIndicator) micIndicator.style.display = "none";
// }
// function showLoading() {
//   if (loadingDiv) loadingDiv.style.display = "block";
// }
// function hideLoading() {
//   if (loadingDiv) loadingDiv.style.display = "none";
// }
// function addChatMessage(text, isUser = false) {
//   if (!chatBox) {
//     console.error("The chatBox element was not found in the HTML.");
//     return;
//   }
//   const messageDiv = document.createElement('div');
//   messageDiv.className = isUser ? 'user-message' : 'bot-message';
//   messageDiv.innerText = text;
//   chatBox.appendChild(messageDiv);
//   chatBox.scrollTop = chatBox.scrollHeight;
// }
 
// // Voice and Speaking Logic
// function loadVoicesAndSelect(defaultVoice = 'Google UK English Female') {
//   return new Promise((resolve) => {
//     function setVoices() {
//       voices = synth.getVoices();
//       voiceSelect.innerHTML = '';
//       let fallbackIndex = 0;
 
//       voices.forEach((voice, index) => {
//         const option = document.createElement('option');
//         option.value = index;
//         option.textContent = `${voice.name} (${voice.lang})`;
//         voiceSelect.appendChild(option);
 
//         if (voice.name.includes(defaultVoice)) {
//           option.selected = true;
//           selectedVoice = voice;
//         }
//         if (index === 0 && !selectedVoice) fallbackIndex = index;
//       });
 
//       if (!selectedVoice && voices.length > 0) {
//         selectedVoice = voices[fallbackIndex];
//         voiceSelect.value = fallbackIndex;
//       }
//       resolve();
//     }
//     if (synth.getVoices().length > 0) setVoices();
//     else synth.onvoiceschanged = setVoices;
//   });
// }
 
// function speakText(text) {
//   return new Promise((resolve) => {
//     if (isSpeaking) {
//       synth.cancel();
//     }
 
//     const utterance = new SpeechSynthesisUtterance(text);
//     utterance.voice = selectedVoice;
//     utterance.rate = 1;
//     utterance.pitch = 1;
 
//     utterance.onstart = () => {
//       isSpeaking = true;
//       stopBtn.disabled = false;
//       isListening = false;
//       hideMic();
//     };
 
//     utterance.onend = () => {
//       isSpeaking = false;
//       stopBtn.disabled = true;
//       setTimeout(startVoiceRecognition, 500);
//       resolve();
//     };
 
//     synth.speak(utterance);
//   });
// }
 
// // Voice Recognition Logic
// function startVoiceRecognition() {
//   if (!SpeechRecognition || !synth) {
//     subtitleDiv.innerText = "❌ Browser not supported. Please use Chrome.";
//     console.error("Browser does not support SpeechRecognition or SpeechSynthesis.");
//     return;
//   }
 
//   if (isListening || isSpeaking) return;
 
//   const recognition = new SpeechRecognition();
//   recognition.continuous = false;
//   recognition.lang = 'en-US';
//   recognition.interimResults = false;
 
//   isListening = true;
//   showMic();
//   subtitleDiv.innerText = "Listening...";
 
//   recognition.onstart = () => console.log("🎤 Voice recognition started.");
 
//   recognition.onerror = e => {
//     console.error("❌ Voice recognition error:", e.error);
//     if (e.error === 'no-speech' || e.error === 'network') {
//       subtitleDiv.innerText = "Listening timed out. Say something to restart.";
//     } else {
//       subtitleDiv.innerText = "⚠️ Voice error: " + e.error;
//     }
//     isListening = false;
//     hideMic();
//     setTimeout(startVoiceRecognition, 2000);
//   };
 
//   recognition.onend = () => {
//     isListening = false;
//     if (!isSpeaking) {
//       console.log("🔁 Recognition ended. Restarting...");
//       setTimeout(startVoiceRecognition, 500);
//     }
//   };
 
//   recognition.onresult = async (event) => {
//     const transcript = event.results[0][0].transcript.trim();
//     console.log("🎧 Heard:", transcript);
//     hideMic();
//     subtitleDiv.innerText = `You: ${transcript}`;
//     addChatMessage(transcript, true);
 
//     const exitCommands = ["exit", "go back", "quit", "bye", "close", "bye sia"];
//     if (exitCommands.some(cmd => transcript.toLowerCase().includes(cmd))) {
//       subtitleDiv.innerText = "👋 See you again!";
//       await speakText("Ok, see you again! Redirecting you to the main screen.");
//       window.location.href = "/";
//       return;
//     }
 
//     // ✅ Check for navigation commands
//     for (let keyword in screenRoutes) {
//       if (transcript.toLowerCase().includes(keyword)) {
//         const route = screenRoutes[keyword];
//         subtitleDiv.innerText = `🔗 Opening ${keyword} page...`;
//         await speakText(`Opening ${keyword} page for you.`);
//         window.location.href = route;
//         return;
//       }
//     }
 
//     // Otherwise → go to backend /ask
//     showLoading();
//     try {
//       const res = await fetch('/ask', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ question: transcript })
//       });
//       const data = await res.json();
//       const reply = data.answer || "Sorry, I don't know how to answer that.";
 
//       subtitleDiv.innerText = `SIA: ${reply}`;
//       addChatMessage(reply);
//       await speakText(reply);
//       hideLoading();
//     } catch (err) {
//       console.error("❌ Fetch error:", err);
//       subtitleDiv.innerText = "Something went wrong.";
//       hideLoading();
//     }
//   };
 
//   recognition.start();
// }
 
// // Event Listeners
// voiceSelect.addEventListener('change', () => {
//   selectedVoice = voices[parseInt(voiceSelect.value)];
// });
// stopBtn.addEventListener('click', () => {
//   synth.cancel();
//   isSpeaking = false;
//   stopBtn.disabled = true;
//   subtitleDiv.innerText = '';
//   startVoiceRecognition();
// });
 
// // Initialization
// (async function init() {
//   await loadVoicesAndSelect();
//   subtitleDiv.innerText = "Click 'Start Assistant' to begin.";
// })();
 
// // Start button listener
// startButton.addEventListener('click', async () => {
//   startButton.style.display = 'none';
//   const greeting = "Hi there! How can I help you today?";
//   subtitleDiv.innerText = greeting;
//   await speakText(greeting);
// });
 
 console.log("🟢 SIA Chat.js Initialized");
 
// DOM Elements
const subtitleDiv = document.getElementById('subtitles');
const voiceSelect = document.getElementById('voiceSelect');
const stopBtn = document.getElementById('stopBtn');
const chatBox = document.getElementById('chatBox');
const micIndicator = document.getElementById("micIndicator");
const loadingDiv = document.getElementById("loading");
const startButton = document.getElementById('startButton');
 
// Speech APIs
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const synth = window.speechSynthesis;
 
// State Variables
let selectedVoice = null;
let voices = [];
let isSpeaking = false;
let isListening = false;
 
// --- Screen Navigation Keywords ---
const screenRoutes = {
  "holiday": "/holidays",
  "holiday calendar": "/holidays",
  "holidays": "/holidays",
 
  "wishes": "/wishes-page",
  "birthday": "/wishes-page",
  "birthdays": "/wishes-page",
  "anniversary": "/wishes-page",
  "anniversaries": "/wishes-page",
 
  "hr policies": "/hr",
  "hr policy": "/hr",
 
  "insurance": "/insurance",
  "insurance policy": "/insurance",
 
  "employee benefits": "/other_emp_benefits", // replace if you have a dedicated page
  "benefits": "/other_emp_benefits",
 
  "event": "../static/event.pdf", // replace with dedicated event route if available
  "upcoming event": "../static/event.pdf",
 
  "office layout": "/office-layout",
  "floor plan": "/office-layout",
 
  "story": "https://www.cswg.com/about/", // replace with correct route if available
  "our story": "https://www.cswg.com/about/",
 
  "assistant": "/chat",
  "sia": "/chat",
};
 
// UI Helpers
function showMic() {
  if (micIndicator) micIndicator.style.display = "block";
}
function hideMic() {
  if (micIndicator) micIndicator.style.display = "none";
}
function showLoading() {
  if (loadingDiv) loadingDiv.style.display = "block";
}
function hideLoading() {
  if (loadingDiv) loadingDiv.style.display = "none";
}
function addChatMessage(text, isUser = false) {
  if (!chatBox) {
    console.error("The chatBox element was not found in the HTML.");
    return;
  }
  const messageDiv = document.createElement('div');
  messageDiv.className = isUser ? 'user-message' : 'bot-message';
  messageDiv.innerText = text;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}
 
// Voice and Speaking Logic
function loadVoicesAndSelect(defaultVoice = 'Google UK English Female') {
  return new Promise((resolve) => {
    function setVoices() {
      voices = synth.getVoices();
      voiceSelect.innerHTML = '';
      let fallbackIndex = 0;
 
      voices.forEach((voice, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${voice.name} (${voice.lang})`;
        voiceSelect.appendChild(option);
 
        if (voice.name.includes(defaultVoice)) {
          option.selected = true;
          selectedVoice = voice;
        }
        if (index === 0 && !selectedVoice) fallbackIndex = index;
      });
 
      if (!selectedVoice && voices.length > 0) {
        selectedVoice = voices[fallbackIndex];
        voiceSelect.value = fallbackIndex;
      }
      resolve();
    }
    if (synth.getVoices().length > 0) setVoices();
    else synth.onvoiceschanged = setVoices;
  });
}
 
function speakText(text) {
  return new Promise((resolve) => {
    if (isSpeaking) {
      synth.cancel();
    }
 
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = selectedVoice;
    utterance.rate = 1;
    utterance.pitch = 1;
 
    utterance.onstart = () => {
      isSpeaking = true;
      stopBtn.disabled = false;
      isListening = false;
      hideMic();
    };
 
    utterance.onend = () => {
      isSpeaking = false;
      stopBtn.disabled = true;
      setTimeout(startVoiceRecognition, 500);
      resolve();
    };
 
    synth.speak(utterance);
  });
}
 
// Voice Recognition Logic
function startVoiceRecognition() {
  if (!SpeechRecognition || !synth) {
    subtitleDiv.innerText = "❌ Browser not supported. Please use Chrome.";
    console.error("Browser does not support SpeechRecognition or SpeechSynthesis.");
    return;
  }
 
  if (isListening || isSpeaking) return;
 
  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.lang = 'en-US';
  recognition.interimResults = false;
 
  isListening = true;
  showMic();
  subtitleDiv.innerText = "Listening...";
 
  recognition.onstart = () => console.log("🎤 Voice recognition started.");
 
  recognition.onerror = e => {
    console.error("❌ Voice recognition error:", e.error);
    if (e.error === 'no-speech' || e.error === 'network') {
      subtitleDiv.innerText = "Listening timed out. Say something to restart.";
    } else {
      subtitleDiv.innerText = "⚠️ Voice error: " + e.error;
    }
    isListening = false;
    hideMic();
    setTimeout(startVoiceRecognition, 2000);
  };
 
  recognition.onend = () => {
    isListening = false;
    if (!isSpeaking) {
      console.log("🔁 Recognition ended. Restarting...");
      setTimeout(startVoiceRecognition, 500);
    }
  };
 
  recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript.trim();
    console.log("🎧 Heard:", transcript);
    hideMic();
    subtitleDiv.innerText = `You: ${transcript}`;
    addChatMessage(transcript, true);
 
    const exitCommands = ["exit", "go back", "quit", "bye", "close", "bye sia"];
    if (exitCommands.some(cmd => transcript.toLowerCase().includes(cmd))) {
      subtitleDiv.innerText = "👋 See you again!";
      await speakText("Ok, see you again! Redirecting you to the main screen.");
      window.location.href = "/";
      return;
    }
 
    // ✅ Check for navigation commands
    for (let keyword in screenRoutes) {
      if (transcript.toLowerCase().includes(keyword)) {
        const route = screenRoutes[keyword];
        subtitleDiv.innerText = `🔗 Opening ${keyword} page...`;
        await speakText(`Opening ${keyword} page for you.`);
        window.location.href = route;
        return;
      }
    }
 
    // Otherwise → go to backend /ask
    showLoading();
    try {
      const res = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: transcript })
      });
      const data = await res.json();
      const reply = data.answer || "Sorry, I don't know how to answer that.";
 
      subtitleDiv.innerText = `SIA: ${reply}`;
      addChatMessage(reply);
      await speakText(reply);
      hideLoading();
    } catch (err) {
      console.error("❌ Fetch error:", err);
      subtitleDiv.innerText = "Something went wrong.";
      hideLoading();
    }
  };
 
  recognition.start();
}
 
// Event Listeners
voiceSelect.addEventListener('change', () => {
  selectedVoice = voices[parseInt(voiceSelect.value)];
});
stopBtn.addEventListener('click', () => {
  synth.cancel();
  isSpeaking = false;
  stopBtn.disabled = true;
  subtitleDiv.innerText = '';
  startVoiceRecognition();
});
 
// Initialization
(async function init() {
  await loadVoicesAndSelect();
  subtitleDiv.innerText = "Click 'Start Assistant' to begin.";
})();
 
// Start button listener
startButton.addEventListener('click', async () => {
  startButton.style.display = 'none';
  const greeting = "Hi there! How can I help you today?";
  subtitleDiv.innerText = greeting;
  await speakText(greeting);
});
