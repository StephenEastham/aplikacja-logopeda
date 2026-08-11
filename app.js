const audio = document.querySelector("#exercise-audio");
const homeView = document.querySelector("#home-view");
const exerciseView = document.querySelector("#exercise-view");
const settingsView = document.querySelector("#settings-view");
const soundIndex = document.querySelector("#sound-index");
const exerciseGrid = document.querySelector("#exercise-grid");
const exerciseTitle = document.querySelector("#exercise-title");
const previousSound = document.querySelector("#previous-sound");
const nextSound = document.querySelector("#next-sound");
const orderControls = document.querySelector("#order-controls");
const orderButtons = [...document.querySelectorAll("[data-order]")];
const soundEnabled = document.querySelector("#sound-enabled");
const volume = document.querySelector("#volume");
const installButton = document.querySelector("#install-button");
const parrotImage = "./assets/images/pa_papuga.svg";
const parrotSound = "./assets/sounds/pa_papuga.wav";
let soundGroups = [];
let orderedGroups = [];
let assetsBySyllable = new Map();
let itemOrder = "ascending";
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
  audio.src = button.dataset.audio;

  try {
    await audio.play();
  } catch (error) {
    resetPlayback();
    console.error("Audio playback failed", error);
  }
}

function soundUrl(consonant) {
  return `./#sound=${encodeURIComponent(consonant)}`;
}

function parseExercises(markdown, sourceUrl) {
  const linkDefinitions = new Map(
    markdown
      .split("\n")
      .map((line) => line.match(/^\[([^\]]+)\]:\s*(\S+)/))
      .filter(Boolean)
      .map((match) => [match[1].toLowerCase(), match[2]]),
  );
  const resolveLink = (cell) => {
    const inlinePath = cell.match(/\]\(([^)]+)\)/)?.[1];
    const referenceName = cell.match(/^\[([^\]]+)\]$/)?.[1]?.toLowerCase();
    const path = inlinePath ?? linkDefinitions.get(referenceName);
    return path ? new URL(path, sourceUrl).href : null;
  };
  const groups = new Map();
  const assets = new Map();
  const rows = markdown
    .split("\n")
    .filter((line) => line.startsWith("|") && !line.includes("---"))
    .slice(1)
    .map((line) => line.split("|").slice(1, -1).map((cell) => cell.trim()));

  rows.forEach(([consonant, , syllable, imageCell, soundCell]) => {
    if (!consonant || !syllable) {
      return;
    }

    if (!groups.has(consonant)) {
      groups.set(consonant, []);
    }
    groups.get(consonant).push(syllable);

    const image = resolveLink(imageCell);
    const sound = resolveLink(soundCell);
    if (image && sound) {
      assets.set(syllable, { image, sound });
    }
  });

  return {
    groups: [...groups].map(([consonant, syllables]) => ({ consonant, syllables })),
    assets,
  };
}

function getAssets(syllable) {
  return assetsBySyllable.get(syllable) ?? assetsBySyllable.get("*") ?? {
    image: parrotImage,
    sound: parrotSound,
  };
}

function wordFromSoundUrl(sound, syllable) {
  const filename = decodeURIComponent(new URL(sound, window.location.href).pathname.split("/").pop() ?? "");
  const basename = filename.replace(/\.[^.]+$/, "");
  const prefix = `${syllable}_`;
  return basename.startsWith(prefix) ? basename.slice(prefix.length).replaceAll("_", " ") : syllable;
}

function shuffleItems(items) {
  const shuffledItems = [...items];

  for (let currentIndex = shuffledItems.length - 1; currentIndex > 0; currentIndex -= 1) {
    const randomIndex = Math.floor(Math.random() * (currentIndex + 1));
    [shuffledItems[currentIndex], shuffledItems[randomIndex]] = [
      shuffledItems[randomIndex],
      shuffledItems[currentIndex],
    ];
  }

  return shuffledItems;
}

function orderItems(items, order) {
  if (order === "descending") {
    return [...items].reverse();
  }
  if (order === "random") {
    return shuffleItems(items);
  }
  return [...items];
}

function setItemOrder(order) {
  itemOrder = ["ascending", "descending", "random"].includes(order) ? order : "ascending";
  localStorage.setItem("itemOrder", itemOrder);
  orderButtons.forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.order === itemOrder));
  });

  orderedGroups = orderItems(soundGroups, itemOrder);
  renderSoundIndex();
  renderRoute();
}

function renderSoundIndex() {
  const fragment = document.createDocumentFragment();

  orderedGroups.forEach(({ consonant }) => {
    const link = document.createElement("a");
    link.className = "index-tile";
    link.href = soundUrl(consonant);
    link.dataset.route = "";
    link.textContent = consonant;
    link.setAttribute("aria-label", `Ćwicz dźwięk ${consonant}`);
    fragment.append(link);
  });

  soundIndex.replaceChildren(fragment);
}

function renderExercise(groupIndex) {
  const group = soundGroups[groupIndex];
  const previousIndex = (groupIndex - 1 + soundGroups.length) % soundGroups.length;
  const nextIndex = (groupIndex + 1) % soundGroups.length;
  const fragment = document.createDocumentFragment();

  orderItems(group.syllables, itemOrder).forEach((syllable) => {
    const button = document.createElement("button");
    const image = document.createElement("img");
    const label = document.createElement("span");
    const assets = getAssets(syllable);
    const word = wordFromSoundUrl(assets.sound, syllable);

    button.className = "sound-tile";
    button.type = "button";
    button.dataset.sound = syllable;
    button.dataset.audio = assets.sound;
    button.setAttribute("aria-label", `Odtwórz słowo „${word}”, sylaba „${syllable}”`);
    button.setAttribute("aria-pressed", "false");
    image.alt = "";
    image.addEventListener("error", () => {
      if (!image.src.endsWith("/assets/images/pa_papuga.svg")) {
        image.src = parrotImage;
      }
    });
    image.src = assets.image;
    label.textContent = syllable;
    button.append(image, label);
    fragment.append(button);
  });

  resetPlayback();
  exerciseTitle.textContent = group.consonant;
  previousSound.href = soundUrl(soundGroups[previousIndex].consonant);
  previousSound.setAttribute("aria-label", `Poprzedni dźwięk: ${soundGroups[previousIndex].consonant}`);
  nextSound.href = soundUrl(soundGroups[nextIndex].consonant);
  nextSound.setAttribute("aria-label", `Następny dźwięk: ${soundGroups[nextIndex].consonant}`);
  exerciseGrid.setAttribute("aria-label", `Sylaby dla dźwięku ${group.consonant}`);
  exerciseGrid.replaceChildren(fragment);
}

function renderRoute() {
  const route = window.location.hash;
  const requestedSound = route.startsWith("#sound=")
    ? decodeURIComponent(route.slice("#sound=".length))
    : null;
  const groupIndex = soundGroups.findIndex(({ consonant }) => consonant === requestedSound);
  const showSettings = route === "#settings";
  const showExercise = groupIndex >= 0;

  homeView.hidden = showSettings || showExercise;
  exerciseView.hidden = !showExercise;
  settingsView.hidden = !showSettings;
  orderControls.hidden = showSettings;

  if (showSettings) {
    document.title = "Ustawienia | Logopeda";
    document.querySelector("#settings-title").focus({ preventScroll: true });
  } else if (showExercise) {
    renderExercise(groupIndex);
    document.title = `${soundGroups[groupIndex].consonant} | Logopeda`;
    exerciseTitle.focus({ preventScroll: true });
  } else {
    document.title = "Logopeda";
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

document.addEventListener("click", (event) => {
  const soundButton = event.target.closest("[data-sound]");
  if (soundButton) {
    toggleSound(soundButton);
  }
});

orderButtons.forEach((button) => {
  button.addEventListener("click", () => setItemOrder(button.dataset.order));
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

async function initializeApp() {
  loadPreferences();

  try {
    const response = await fetch("./assets/assets.md");
    if (!response.ok) {
      throw new Error(`Unable to load exercises: ${response.status}`);
    }

    const exercises = parseExercises(await response.text(), response.url);
    soundGroups = exercises.groups;
    assetsBySyllable = exercises.assets;
    setItemOrder(localStorage.getItem("itemOrder") ?? "ascending");
  } catch (error) {
    soundIndex.textContent = "Nie udało się wczytać ćwiczeń.";
    console.error(error);
  }
}

initializeApp();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("./service-worker.js"));
}