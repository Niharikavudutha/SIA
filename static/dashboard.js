// // static/dashboard.js
// document.addEventListener("DOMContentLoaded", () => {
//   // Map tile classes -> page routes
//   const routes = {
//     "holiday": "/holidays",
//     "policies": "/hr",
//     "policies-orange": "/insurance",
//     "benefits": "/insurance",
//     "event": "/index",     // or another page if you want
//     "our-story": "/index", // example: redirect to SIA
//     "about": "/index",
//     // "health": "/insurance",
//     "wishes": "/wishes-page",
//     "sia": "/scan"
//   };

//   // Attach click listeners
//   Object.keys(routes).forEach(cls => {
//     const el = document.querySelector(`.${cls}`);
//     if (el) {
//       el.style.cursor = "pointer";
//       el.addEventListener("click", () => {
//         window.location.href = routes[cls];
//       });
//     }
//   });
// });
// static/dashboard.js
document.addEventListener("DOMContentLoaded", () => {
  // Map tile classes -> page routes
  const routes = {
    "holiday": "/holidays",
    "policies": "/hr",
    "policies-orange": "/insurance",
    "benefits": "/other_emp_benefits",
    "event": "../static/event.pdf",        // you can replace with another page if needed
    "our-story": "https://www.cswg.com/about/",    // example: redirect to SIA or story page
    // "about": "/index",
    "office-layout": "../static/Office_layout.pdf",
    "wishes": "/wishes-page", // full wishes page
    "sia": "/scan"            // SIA intro flow
  };

  // Attach click listeners for dashboard tiles
  Object.keys(routes).forEach(cls => {
    const el = document.querySelector(`.${cls}`);
    if (el) {
      el.style.cursor = "pointer";
      el.addEventListener("click", () => {
        window.location.href = routes[cls];
      });
    }
  });

  // === Wishes Auto-Update ===
  async function loadWishes() {
    try {
      const res = await fetch("/wishes");
      const data = await res.json();

      const bdayMsg = document.getElementById("birthday-msg");
      const annMsg = document.getElementById("anniversary-msg");

      if (bdayMsg) {
        if (data.birthdays && data.birthdays.length > 0) {
          bdayMsg.innerHTML = `🎂 Happy Birthday: <b>${data.birthdays.join(", ")}</b>`;
        } else {
          bdayMsg.innerHTML = "🎂 No birthdays today";
        }
      }

      if (annMsg) {
        if (data.anniversaries && data.anniversaries.length > 0) {
          annMsg.innerHTML = `🎉 Work Anniversary: <b>${data.anniversaries.join(", ")}</b>`;
        } else {
          annMsg.innerHTML = "🎉 No anniversaries today";
        }
      }
    } catch (err) {
      console.error("❌ Failed to load wishes:", err);
    }
  }

  // Load immediately and refresh every 60s
  loadWishes();
  setInterval(loadWishes, 60000);
});
