const chat = document.getElementById("chat");
const promptBox = document.getElementById("prompt");
const sendBtn = document.getElementById("send-btn");
const csrf = document.querySelector('meta[name="csrf-token"]').content;

const WELCOME = chat.innerHTML; 

const banner = document.getElementById("offline-banner");

function updateOnlineStatus() {
  const online = navigator.onLine;
  banner.classList.toggle("d-none", online);
  sendBtn.disabled = !online;
  document.querySelectorAll(".chip").forEach((c) => (c.disabled = !online));
  promptBox.placeholder = online
    ? "Ask a question for class..."
    : "You're offline. Reconnect to ask a question.";
}

window.addEventListener("online", updateOnlineStatus);
window.addEventListener("offline", updateOnlineStatus);
updateOnlineStatus(); // run once on page load

function addMessage(text, who, isError = false) {
  const label = document.createElement("div");
  label.className = "label" + (who === "user" ? " user" : "");
  const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  label.textContent = who === "user" ? `YOU (STUDENT) · ${time}` : `CLASS ASSISTANT · ${time}`;

  const bubble = document.createElement("div");
  bubble.className = `bubble ${who}` + (isError ? " error" : "");
  if (who === "bot" && !isError) {
    bubble.innerHTML = DOMPurify.sanitize(marked.parse(text));
  } else {
    bubble.textContent = text;
  }

  chat.append(label, bubble);
  chat.scrollTop = chat.scrollHeight;
  return bubble;
}

async function sendPrompt() {
  if (!navigator.onLine) { updateOnlineStatus(); return; }
  const prompt = promptBox.value.trim();
  if (!prompt) return;

  addMessage(prompt, "user");
  promptBox.value = "";
  sendBtn.disabled = true;
  const thinking = addMessage("Thinking…", "bot", true);
  thinking.classList.remove("error");

  try {
    const res = await fetch("/api/chat/", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
      body: JSON.stringify({ prompt }),
    });
    const data = await res.json();
    thinking.previousSibling.remove();
    thinking.remove();
    if (res.ok) addMessage(data.reply, "bot");
    else addMessage(data.error || "Something went wrong.", "bot", true);
  } catch (err) {
    thinking.previousSibling.remove();
    thinking.remove();
    addMessage("Couldn't reach the server. Check your connection.", "bot", true);
  } finally {
    updateOnlineStatus();
    promptBox.focus();
  }
}

function clearChat() { chat.innerHTML = WELCOME; }

sendBtn.addEventListener("click", sendPrompt);
promptBox.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendPrompt(); }
});
document.getElementById("clear-btn").addEventListener("click", clearChat);
document.getElementById("clear-top").addEventListener("click", clearChat);
document.querySelectorAll(".chip").forEach((chip) =>
  chip.addEventListener("click", () => { promptBox.value = chip.textContent; sendPrompt(); })
);

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/serviceworker.js", { scope: "/" })
      .then(() => console.log("Service worker registered"))
      .catch((err) => console.error("SW registration failed:", err));
  });
}