const audio = document.querySelector("#exercise-audio");
const homeView = document.querySelector("#home-view");
const exerciseView = document.querySelector("#exercise-view");
const settingsView = document.querySelector("#settings-view");
const soundIndex = document.querySelector("#sound-index");
const exerciseGrid = document.querySelector("#exercise-grid");
const exerciseTitle = document.querySelector("#exercise-title");
const playAllSounds = document.querySelector("#play-all-sounds");
const previousSound = document.querySelector("#previous-sound");
const nextSound = document.querySelector("#next-sound");
const orderControls = document.querySelector("#order-controls");
const orderButtons = [...document.querySelectorAll("[data-order]")];
const soundEnabled = document.querySelector("#sound-enabled");
const volume = document.querySelector("#volume");
const playbackPause = document.querySelector("#playback-pause");
const playbackPauseValue = document.querySelector("#playback-pause-value");
const installButton = document.querySelector("#install-button");
const helpContent = document.querySelector("#help-content");
const developerHelpContent = document.querySelector("#developer-help-content");
const parrotImage = "./assets/images/pa_papuga.svg";
const parrotSound = "./assets/sounds/pa_papuga.wav";
let soundGroups = [];
let orderedGroups = [];
let assetsBySyllable = new Map();
let itemOrder = "ascending";
let activeButton = null;
let playbackQueue = [];
let playbackQueueIndex = -1;
let playbackTimer = null;
let installPrompt = null;

function loadPreferences() {
  soundEnabled.checked = localStorage.getItem("soundEnabled") !== "false";
  volume.value = localStorage.getItem("volume") ?? "1";
  const savedPause = Number(localStorage.getItem("playbackPause"));
  playbackPause.value = savedPause >= 400 && savedPause <= 700 ? String(savedPause) : "500";
  playbackPauseValue.value = `${playbackPause.value} ms`;
  audio.volume = Number(volume.value);
}

function resetPlayback() {
  if (activeButton) {
    activeButton.setAttribute("aria-pressed", "false");
  }
  activeButton = null;
}

function setPlayAllState(isPlaying) {
  const consonant = playAllSounds.textContent;
  playAllSounds.setAttribute("aria-pressed", String(isPlaying));
  if (consonant) {
    playAllSounds.setAttribute(
      "aria-label",
      `${isPlaying ? "Zatrzymaj" : "Odtwórz"} wszystkie dźwięki dla litery ${consonant}`,
    );
  }
}

function cancelPlayback() {
  window.clearTimeout(playbackTimer);
  playbackTimer = null;
  playbackQueue = [];
  playbackQueueIndex = -1;
  setPlayAllState(false);
  audio.pause();
  audio.currentTime = 0;
  resetPlayback();
}

async function playSound(button) {
  resetPlayback();
  activeButton = button;
  button.setAttribute("aria-pressed", "true");
  audio.src = button.dataset.audio;

  try {
    await audio.play();
  } catch (error) {
    cancelPlayback();
    console.error("Audio playback failed", error);
  }
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

  cancelPlayback();
  await playSound(button);
}

async function toggleAllSounds() {
  if (!soundEnabled.checked) {
    return;
  }

  if (!audio.paused || playbackQueue.length > 0) {
    cancelPlayback();
    return;
  }

  playbackQueue = [...exerciseGrid.querySelectorAll("[data-word-sound]")];
  playbackQueueIndex = 0;
  if (playbackQueue.length === 0) {
    return;
  }

  setPlayAllState(true);
  await playSound(playbackQueue[playbackQueueIndex]);
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

  rows.forEach(([consonant, , syllable, syllableSoundCell, wordSoundCell, imageCell]) => {
    if (!consonant || !syllable) {
      return;
    }

    if (!groups.has(consonant)) {
      groups.set(consonant, []);
    }
    groups.get(consonant).push(syllable);

    const image = resolveLink(imageCell);
    const syllableSound = resolveLink(syllableSoundCell);
    const wordSound = resolveLink(wordSoundCell);
    if (image && syllableSound && wordSound) {
      assets.set(syllable, { image, syllableSound, sound: wordSound });
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
    syllableSound: parrotSound,
    sound: parrotSound,
  };
}

function wordFromSoundUrl(sound, syllable) {
  const filename = decodeURIComponent(new URL(sound, window.location.href).pathname.split("/").pop() ?? "");
  const basename = filename.replace(/\.[^.]+$/, "");
  const prefix = `${syllable}_`;
  return basename.startsWith(prefix) ? basename.slice(prefix.length).replaceAll("_", " ") : syllable;
}

function renderMarkdown(markdown, target) {
  const fragment = document.createDocumentFragment();
  let list = null;
  let code = null;

  markdown.split("\n").forEach((line) => {
    const text = line.trim();

    if (text.startsWith("```")) {
      if (code) {
        code = null;
      } else {
        const pre = document.createElement("pre");
        code = document.createElement("code");
        pre.append(code);
        fragment.append(pre);
      }
      list = null;
      return;
    }

    if (code) {
      code.textContent += `${line}\n`;
      return;
    }

    if (!text) {
      list = null;
      return;
    }

    const heading = text.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      const element = document.createElement(`h${heading[1].length + 1}`);
      element.textContent = heading[2];
      fragment.append(element);
      list = null;
      return;
    }

    if (text.startsWith("- ")) {
      if (!list || list.tagName !== "UL") {
        list = document.createElement("ul");
        fragment.append(list);
      }
      const item = document.createElement("li");
      item.textContent = text.slice(2);
      list.append(item);
      return;
    }

    const orderedItem = text.match(/^\d+\.\s+(.+)$/);
    if (orderedItem) {
      if (!list || list.tagName !== "OL") {
        list = document.createElement("ol");
        fragment.append(list);
      }
      const item = document.createElement("li");
      item.textContent = orderedItem[1];
      list.append(item);
      return;
    }

    const paragraph = document.createElement("p");
    paragraph.textContent = text;
    fragment.append(paragraph);
    list = null;
  });

  target.replaceChildren(fragment);
}

async function loadMarkdown(url, target, errorMessage) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Unable to load ${url}: ${response.status}`);
    }
    renderMarkdown(await response.text(), target);
  } catch (error) {
    target.textContent = errorMessage;
    console.error(error);
  }
}

async function loadHelp() {
  await Promise.all([
    loadMarkdown("./assets/pomoc/pomoc.md", helpContent, "Nie udało się wczytać pomocy."),
    loadMarkdown(
      "./assets/pomoc/dla-developera.md",
      developerHelpContent,
      "Nie udało się wczytać informacji dla developera.",
    ),
  ]);
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
    const tile = document.createElement("article");
    const wordButton = document.createElement("button");
    const image = document.createElement("img");
    const syllableButton = document.createElement("button");
    const assets = getAssets(syllable);
    const word = wordFromSoundUrl(assets.sound, syllable);

    tile.className = "sound-tile";
    wordButton.className = "word-sound-button";
    wordButton.type = "button";
    wordButton.dataset.sound = syllable;
    wordButton.dataset.wordSound = "";
    wordButton.dataset.audio = assets.sound;
    wordButton.setAttribute("aria-label", `Odtwórz słowo „${word}”`);
    wordButton.setAttribute("aria-pressed", "false");
    image.alt = "";
    image.addEventListener("error", () => {
      if (!image.src.endsWith("/assets/images/pa_papuga.svg")) {
        image.src = parrotImage;
      }
    });
    image.src = assets.image;
    syllableButton.className = "syllable-sound-button";
    syllableButton.type = "button";
    syllableButton.dataset.sound = syllable;
    syllableButton.dataset.audio = assets.syllableSound;
    syllableButton.setAttribute("aria-label", `Odtwórz sylabę „${syllable}”`);
    syllableButton.setAttribute("aria-pressed", "false");
    syllableButton.textContent = syllable;
    wordButton.append(image);
    tile.append(wordButton, syllableButton);
    fragment.append(tile);
  });

  cancelPlayback();
  playAllSounds.textContent = group.consonant;
  setPlayAllState(false);
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
    playAllSounds.focus({ preventScroll: true });
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

playAllSounds.addEventListener("click", toggleAllSounds);
audio.addEventListener("ended", () => {
  resetPlayback();
  playbackQueueIndex += 1;

  if (playbackQueueIndex < playbackQueue.length) {
    playbackTimer = window.setTimeout(() => {
      playbackTimer = null;
      playSound(playbackQueue[playbackQueueIndex]);
    }, Number(playbackPause.value));
  } else {
    playbackQueue = [];
    playbackQueueIndex = -1;
    setPlayAllState(false);
  }
});
audio.addEventListener("error", cancelPlayback);
window.addEventListener("popstate", renderRoute);

soundEnabled.addEventListener("change", () => {
  localStorage.setItem("soundEnabled", String(soundEnabled.checked));
  if (!soundEnabled.checked) {
    cancelPlayback();
  }
});

volume.addEventListener("input", () => {
  audio.volume = Number(volume.value);
  localStorage.setItem("volume", volume.value);
});

playbackPause.addEventListener("input", () => {
  playbackPauseValue.value = `${playbackPause.value} ms`;
  localStorage.setItem("playbackPause", playbackPause.value);
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
  loadHelp();

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