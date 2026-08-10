const audio = document.querySelector("#exercise-audio");
const soundButtons = [...document.querySelectorAll("[data-sound]")];
const homeView = document.querySelector("#home-view");
const settingsView = document.querySelector("#settings-view");
const soundEnabled = document.querySelector("#sound-enabled");
const volume = document.querySelector("#volume");
const installButton = document.querySelector("#install-button");
let activeButton = null;
let installPrompt = null;

function loadPreferences() {
  soundEnabled.checked = localStorage.getItem("soundEnabled") !== "false";
  volume.value = localStorage.getItem("volume") ?? "1";
  audio.volume = Number(volume.value);
}

function resetPlayback() {
  if (activeButton) {
    activeButton.setAttribute("aria-pressed", "false");
  }
  activeButton = null;
}

async function toggleSound(button) {
  if (!soundEnabled.checked) {
    return;
  }

  if (activeButton === button && !audio.paused) {
    audio.pause();
    resetPlayback();
    return;
  }

  audio.pause();
  audio.currentTime = 0;
  resetPlayback();
  activeButton = button;
  button.setAttribute("aria-pressed", "true");

  try {
    await audio.play();
  } catch (error) {
    resetPlayback();
    console.error("Audio playback failed", error);
  }
}

function renderRoute() {
  const showSettings = window.location.pathname === "/settings";
  homeView.hidden = showSettings;
  settingsView.hidden = !showSettings;
  document.title = showSettings ? "Ustawienia | Logopeda" : "Logopeda";
  if (showSettings) {
    document.querySelector("#settings-title").focus({ preventScroll: true });
  }
}

document.addEventListener("click", (event) => {
  const routeLink = event.target.closest("[data-route]");
  if (!routeLink) {
    return;
  }
  event.preventDefault();
  history.pushState({}, "", routeLink.href);
  renderRoute();
});

soundButtons.forEach((button) => {
  button.setAttribute("aria-pressed", "false");
  button.addEventListener("click", () => toggleSound(button));
});

audio.addEventListener("ended", resetPlayback);
audio.addEventListener("error", resetPlayback);
window.addEventListener("popstate", renderRoute);

soundEnabled.addEventListener("change", () => {
  localStorage.setItem("soundEnabled", String(soundEnabled.checked));
  if (!soundEnabled.checked) {
    audio.pause();
    resetPlayback();
  }
});

volume.addEventListener("input", () => {
  audio.volume = Number(volume.value);
  localStorage.setItem("volume", volume.value);
});

window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  installPrompt = event;
  installButton.hidden = false;
});

installButton.addEventListener("click", async () => {
  if (!installPrompt) {
    return;
  }
  await installPrompt.prompt();
  installPrompt = null;
  installButton.hidden = true;
});

window.addEventListener("appinstalled", () => {
  installPrompt = null;
  installButton.hidden = true;
});

loadPreferences();
renderRoute();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("/service-worker.js"));
}