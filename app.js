const DEFAULT_SCHEME = "briar-forum://share/";

const form = document.getElementById("share-form");
const result = document.getElementById("result");
const shareLinkEl = document.getElementById("share-link");
const markdownEl = document.getElementById("markdown");
const copyLinkBtn = document.getElementById("copy-link");
const copyMarkdownBtn = document.getElementById("copy-markdown");
const downloadJsonBtn = document.getElementById("download-json");

let latestPayload = null;
let latestLink = "";

function toBase64Url(value) {
  const utf8 = new TextEncoder().encode(value);
  let binary = "";
  utf8.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function buildPayload({ forumId, forumName, owner, description, tags }) {
  const payload = {
    forum_id: forumId,
    forum_name: forumName,
    owner,
    created_at: new Date().toISOString(),
    version: 1,
  };

  if (description) payload.description = description;
  if (tags.length > 0) payload.tags = tags;

  return payload;
}

function buildShareLink(payload, scheme) {
  const raw = JSON.stringify(payload);
  return `${scheme}${toBase64Url(raw)}`;
}

function extractFormValues(target) {
  const formData = new FormData(target);
  const forumId = String(formData.get("forumId") || "").trim();
  const forumName = String(formData.get("forumName") || "").trim();
  const owner = String(formData.get("owner") || "").trim();
  const description = String(formData.get("description") || "").trim();
  const scheme = String(formData.get("scheme") || DEFAULT_SCHEME).trim() || DEFAULT_SCHEME;
  const tags = String(formData.get("tags") || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  return { forumId, forumName, owner, description, tags, scheme };
}

async function copyToClipboard(text) {
  if (!text) return;
  await navigator.clipboard.writeText(text);
}

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const values = extractFormValues(event.currentTarget);
  const payload = buildPayload(values);
  const link = buildShareLink(payload, values.scheme);

  latestPayload = payload;
  latestLink = link;

  shareLinkEl.value = link;
  markdownEl.value = `[Join forum: ${payload.forum_name}](${link})`;
  result.classList.remove("hidden");
});

copyLinkBtn.addEventListener("click", async () => {
  await copyToClipboard(latestLink);
});

copyMarkdownBtn.addEventListener("click", async () => {
  await copyToClipboard(markdownEl.value);
});

downloadJsonBtn.addEventListener("click", () => {
  if (!latestPayload || !latestLink) return;

  const blob = new Blob(
    [JSON.stringify({ share_link: latestLink, payload: latestPayload }, null, 2)],
    { type: "application/json" }
  );
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "forum_share.json";
  anchor.click();
  URL.revokeObjectURL(url);
});
