const TOKEN_KEY = "northstar_access_token";
const CHAT_KEY = "northstar_conversation_id";
const state = { token: localStorage.getItem(TOKEN_KEY), user: null, page: "dashboard", groups: [], documents: [], conversations: [], users: [], messages: [], conversationId: localStorage.getItem(CHAT_KEY), busy: false };
const app = document.querySelector("#app");
const icon = (name) => `<svg class="icon"><use href="#i-${name}"></use></svg>`;
const esc = (value = "") => String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
const initials = (name = "") => name.split(/\s+/).filter(Boolean).slice(0, 2).map(part => part[0]).join("").toUpperCase() || "U";
function inlineMarkdown(text) {
  return text.replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/__(.+?)__/g, "<strong>$1</strong>")
    .replace(/\*(?!\s)(.+?)(?<!\s)\*/g, "<em>$1</em>")
    .replace(/_(?!\s)(.+?)(?<!\s)_/g, "<em>$1</em>");
}
function renderMarkdown(value = "") {
  const lines = esc(value).replace(/\r\n?/g, "\n").split("\n");
  const output = []; let paragraph = []; let listType = null; let code = []; let inCode = false;
  const flushParagraph = () => { if (paragraph.length) { output.push(`<p>${paragraph.map(inlineMarkdown).join("<br>")}</p>`); paragraph = []; } };
  const closeList = () => { if (listType) { output.push(`</${listType}>`); listType = null; } };
  for (const line of lines) {
    if (/^\s*```/.test(line)) { flushParagraph(); closeList(); if (inCode) { output.push(`<pre><code>${code.join("\n")}</code></pre>`); code = []; } inCode = !inCode; continue; }
    if (inCode) { code.push(line); continue; }
    if (!line.trim()) { flushParagraph(); closeList(); continue; }
    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    const unordered = line.match(/^\s*[-*+]\s+(.+)$/);
    const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    const quote = line.match(/^\s*&gt;\s?(.+)$/);
    if (heading) { flushParagraph(); closeList(); const level = heading[1].length; output.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`); }
    else if (unordered || ordered) { flushParagraph(); const nextType = unordered ? "ul" : "ol"; if (listType !== nextType) { closeList(); listType = nextType; output.push(`<${listType}>`); } output.push(`<li>${inlineMarkdown((unordered || ordered)[1])}</li>`); }
    else if (quote) { flushParagraph(); closeList(); output.push(`<blockquote>${inlineMarkdown(quote[1])}</blockquote>`); }
    else { closeList(); paragraph.push(line); }
  }
  flushParagraph(); closeList();
  if (inCode) output.push(`<pre><code>${code.join("\n")}</code></pre>`);
  return output.join("");
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (state.token) headers.set("Authorization", `Bearer ${state.token}`);
  if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const response = await fetch(path, { ...options, headers });
  if (response.status === 401 && state.token) { clearSession(); renderAuth(); const error = new Error("Your session expired. Please sign in again."); error.status = 401; throw error; }
  const body = await response.json().catch(() => ({}));
  if (!response.ok) { const error = new Error(body.detail || `Request failed (${response.status})`); error.status = response.status; throw error; }
  return body;
}

function clearSession() { state.token = null; state.user = null; state.conversationId = null; state.messages = []; localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(CHAT_KEY); }
function toast(message, error = false) {
  const region = document.querySelector("#toast-region");
  if (!region) return;
  const item = document.createElement("div"); item.className = `toast${error ? " toast-error" : ""}`; item.textContent = message; region.append(item);
  setTimeout(() => item.remove(), 3800);
}

function renderAuth(mode = "login") {
  const signup = mode === "signup";
  app.innerHTML = `<main class="auth-layout"><section class="auth-story"><a class="brand" href="#"><span class="brand-mark">N</span><span>northstar<span class="brand-light">.work</span></span></a><div class="story-content"><span class="eyebrow"><span class="status-dot"></span> KNOWLEDGE, IN CONTEXT</span><h1>Every answer<br>has a <em>source.</em></h1><p>A secure workspace for the knowledge your teams rely on. Ask better questions and get grounded answers from the documents you can access.</p><div class="story-points"><span>${icon("shield")} Group-level access</span><span>${icon("spark")} Source-linked answers</span></div></div><div class="story-foot">PRIVATE KNOWLEDGE · SHARED WITH PURPOSE</div></section><section class="auth-panel"><div class="auth-card"><div class="mobile-brand brand"><span class="brand-mark">N</span><span>northstar<span class="brand-light">.work</span></span></div><span class="eyebrow muted">${signup ? "GET STARTED" : "WELCOME BACK"}</span><h2>${signup ? "Create your account" : "Sign in to your workspace"}</h2><p class="auth-subtitle">${signup ? "Your administrator can add you to the right groups." : "Your team’s knowledge is ready when you are."}</p><form id="auth-form" class="form-stack">${signup ? `<label>Full name<input name="full_name" autocomplete="name" placeholder="Jordan Lee" required minlength="2"></label><label>Department <span class="optional">OPTIONAL</span><input name="department" placeholder="e.g. Engineering"></label>` : ""}<label>Work email<input name="email" type="email" autocomplete="email" placeholder="you@company.com" required></label><label>Password<input name="password" type="password" autocomplete="${signup ? "new-password" : "current-password"}" placeholder="${signup ? "At least 8 characters" : "Enter your password"}" required minlength="${signup ? "8" : "1"}"></label><button class="button button-primary button-wide" type="submit">${signup ? "Create account" : "Sign in"}<span>→</span></button><div class="form-error" id="auth-error"></div></form><div class="auth-switch">${signup ? "Already have an account?" : "New to this workspace?"} <button class="text-button" id="auth-switch">${signup ? "Sign in" : "Create an account"}</button></div><div class="auth-note">${icon("shield")} Your workspace access is protected by your team’s permissions.</div></div><div class="auth-copyright">NORTHSTAR WORKSPACE <span>·</span> SECURE KNOWLEDGE</div></section></main>`;
  document.querySelector("#auth-switch").onclick = () => renderAuth(signup ? "login" : "signup");
  document.querySelector("#auth-form").onsubmit = async (event) => {
    event.preventDefault(); const form = new FormData(event.currentTarget); const payload = Object.fromEntries(form.entries());
    const error = document.querySelector("#auth-error"); error.textContent = "";
    try {
      const result = await request(signup ? "/auth/signup" : "/auth/login", { method: "POST", body: JSON.stringify(payload) });
      state.token = result.access_token; localStorage.setItem(TOKEN_KEY, state.token); state.user = result.user; state.page = "dashboard"; await loadWorkspace(); render(); toast("Welcome to your workspace.");
    } catch (problem) { error.textContent = problem.message; }
  };
}

async function loadWorkspace() {
  state.user = await request("/me");
  const results = await Promise.allSettled([request("/groups"), request("/documents"), request("/conversations")]);
  if (!state.token) throw new Error("Your session has ended. Please sign in again.");
  const [groups, documents, conversations] = results.map(result => result.status === "fulfilled" ? result.value : []);
  state.groups = groups; state.documents = documents; state.conversations = conversations;
  if (state.user.role === "admin") {
    try { state.users = await request("/admin/users"); }
    catch (error) { if (error.status === 401 || !state.token) throw error; state.users = []; toast(`People list could not load: ${error.message}`, true); }
  }
  const failed = results.find(result => result.status === "rejected");
  if (failed && state.token) toast(`Some workspace data could not load: ${failed.reason.message}`, true);
  if (state.conversationId && !conversations.some(row => row.id === state.conversationId)) { state.conversationId = null; localStorage.removeItem(CHAT_KEY); }
}

function shell() {
  const nav = [["dashboard", "grid", "Overview"], ["chat", "chat", "AI assistant"], ["documents", "files", "Knowledge base"]];
  if (state.user.role === "admin") nav.push(["admin", "users", "Administration"]);
  return `<div class="workspace"><aside class="sidebar"><a class="brand" href="#" data-page="dashboard"><span class="brand-mark">N</span><span>northstar<span class="brand-light">.work</span></span></a><div class="workspace-label">WORKSPACE</div><div class="workspace-picker"><span class="workspace-avatar">${initials(state.user.department || "NW")}</span><span><strong>${esc(state.user.department || "Northstar")}</strong><small>Knowledge workspace</small></span><span class="picker-chevron">⌄</span></div><div class="nav-label">MENU</div><nav class="main-nav">${nav.map(([page, ico, label]) => `<button class="nav-item ${state.page === page ? "active" : ""}" data-page="${page}">${icon(ico)}<span>${label}</span>${page === "chat" ? `<span class="nav-indicator"></span>` : ""}</button>`).join("")}</nav><div class="sidebar-bottom"><div class="sidebar-help"><span class="help-orbit">${icon("spark")}</span><strong>Knowledge, made useful.</strong><p>Answers grounded in the documents your team trusts.</p></div><div class="user-card"><span class="user-avatar">${initials(state.user.full_name)}</span><span class="user-meta"><strong>${esc(state.user.full_name)}</strong><small>${esc(state.user.role === "admin" ? "Workspace admin" : state.user.department || "Team member")}</small></span><button class="logout-button" title="Sign out" data-action="logout">${icon("logout")}</button></div></div></aside><main class="main-area"><header class="topbar"><div class="breadcrumb"><span>Workspace</span>${icon("chevron")}<strong>${({ dashboard: "Overview", chat: "AI assistant", documents: "Knowledge base", admin: "Administration" })[state.page]}</strong></div><div class="topbar-right"><span class="secure-label">${icon("shield")} SECURE WORKSPACE</span><span class="top-avatar">${initials(state.user.full_name)}</span></div></header><section class="page-content" id="page-content"></section></main></div>`;
}

function render() {
  if (!state.token || !state.user) return renderAuth();
  app.innerHTML = shell();
  document.querySelectorAll("[data-page]").forEach(button => button.onclick = () => { state.page = button.dataset.page; if (state.page !== "chat") render(); else openChat(); });
  document.querySelector('[data-action="logout"]').onclick = logout;
  ({ dashboard: renderDashboard, chat: renderChat, documents: renderDocuments, admin: renderAdmin }[state.page] || renderDashboard)();
}

function renderDashboard() {
  const content = document.querySelector("#page-content");
  const recent = state.documents.slice(0, 5);
  content.innerHTML = `<div class="page-heading"><div><span class="eyebrow muted">YOUR WORKSPACE</span><h1>Good ${new Date().getHours() < 12 ? "morning" : new Date().getHours() < 18 ? "afternoon" : "evening"}, ${esc(state.user.full_name.split(" ")[0])}</h1><p>Everything your team knows, in one place.</p></div><button class="button button-primary" data-page="chat">${icon("spark")} Ask the assistant</button></div><div class="welcome-banner"><div class="welcome-copy"><span class="eyebrow">NORTHSTAR ASSISTANT</span><h2>Find clarity in your company knowledge.</h2><p>Ask a question and get a grounded answer with sources you can trust.</p><button class="button button-white" data-page="chat">Start a conversation <span>→</span></button></div><div class="banner-art"><div class="art-ring ring-one"></div><div class="art-ring ring-two"></div><div class="art-core">${icon("spark")}</div><span class="art-chip chip-one">Verified sources</span><span class="art-chip chip-two">Group-aware</span></div></div><div class="metric-grid"><article class="metric-card"><div class="metric-top"><span>AVAILABLE DOCUMENTS</span><span class="metric-icon blue">${icon("files")}</span></div><strong>${state.documents.length}</strong><small>Shared with your groups</small></article><article class="metric-card"><div class="metric-top"><span>YOUR GROUPS</span><span class="metric-icon purple">${icon("users")}</span></div><strong>${state.groups.length}</strong><small>Knowledge spaces you can access</small></article><article class="metric-card"><div class="metric-top"><span>CONVERSATIONS</span><span class="metric-icon green">${icon("chat")}</span></div><strong>${state.conversations.length}</strong><small>Your saved assistant chats</small></article></div><div class="section-heading"><div><h2>Recently added</h2><p>Documents available in your workspace</p></div><button class="button button-quiet" data-page="documents">View knowledge base <span>→</span></button></div><div class="data-card">${recent.length ? `<div class="table-wrap"><table><thead><tr><th>DOCUMENT</th><th>SHARED WITH</th><th>ADDED BY</th><th>ADDED</th></tr></thead><tbody>${recent.map(documentRow).join("")}</tbody></table></div>` : emptyState("files", "No documents yet", "Documents shared with your groups will appear here.")}</div><div class="group-strip"><div><h3>Your access</h3><p>Knowledge spaces you’re a member of</p></div><div class="group-pills">${state.groups.length ? state.groups.map(group => `<span class="group-pill"><i></i>${esc(group.name)}</span>`).join("") : `<span class="muted-text">No groups assigned yet</span>`}</div></div>`;
  bindPageButtons();
}

function documentRow(doc) { return `<tr><td><div class="file-cell"><span class="file-icon">${icon("files")}</span><span><strong>${esc(doc.filename)}</strong><small>${formatBytes(doc.size_bytes)}</small></span></div></td><td>${(doc.shared_groups || "").split(",").filter(Boolean).map(name => `<span class="table-tag">${esc(name.trim())}</span>`).join(" ") || "—"}</td><td>${esc(doc.uploader || "Workspace admin")}</td><td>${formatDate(doc.created_at)}</td></tr>`; }
function formatBytes(size = 0) { if (size < 1024) return `${size} B`; if (size < 1048576) return `${(size / 1024).toFixed(0)} KB`; return `${(size / 1048576).toFixed(1)} MB`; }
function formatDate(value) { return value ? new Date(value.endsWith("Z") ? value : `${value}Z`).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" }) : "—"; }
function emptyState(symbol, title, description) { return `<div class="empty-state"><span class="empty-icon">${icon(symbol)}</span><h3>${title}</h3><p>${description}</p></div>`; }
function bindPageButtons() { document.querySelectorAll("[data-page]").forEach(button => button.onclick = () => { state.page = button.dataset.page; render(); }); }

function renderDocuments() {
  const content = document.querySelector("#page-content");
  content.innerHTML = `<div class="page-heading"><div><span class="eyebrow muted">SHARED KNOWLEDGE</span><h1>Knowledge base</h1><p>Documents your groups can use to get reliable answers.</p></div><button class="button button-primary" id="upload-open">${icon("upload")} Upload documents</button></div><div class="document-toolbar"><div class="search-field">${icon("search")}<input id="document-search" placeholder="Search documents..."></div><span class="result-count">${state.documents.length} ${state.documents.length === 1 ? "document" : "documents"}</span></div><div id="document-list" class="data-card">${state.documents.length ? `<div class="table-wrap"><table><thead><tr><th>DOCUMENT</th><th>SHARED WITH</th><th>ADDED BY</th><th>ADDED</th><th></th></tr></thead><tbody>${state.documents.map(doc => `<tr data-filename="${esc(doc.filename.toLowerCase())}"><td>${documentRow(doc).match(/<td>(.*?)<\/td>/)?.[1] || ""}</td><td>${(doc.shared_groups || "").split(",").filter(Boolean).map(name => `<span class="table-tag">${esc(name.trim())}</span>`).join(" ")}</td><td>${esc(doc.uploader || "Workspace admin")}</td><td>${formatDate(doc.created_at)}</td><td>${doc.can_delete ? `<button class="icon-button danger" data-delete="${esc(doc.id)}" title="Delete document">${icon("trash")}</button>` : ""}</td></tr>`).join("")}</tbody></table></div>` : emptyState("files", "Your knowledge base is ready", "Upload a document and share it with the right groups.")}</div><div class="upload-modal hidden" id="upload-modal"><div class="modal-backdrop" data-close-modal></div><div class="modal-card"><div class="modal-heading"><div><span class="eyebrow muted">ADD TO KNOWLEDGE</span><h2>Upload documents</h2><p>Choose files and the groups allowed to use them.</p></div><button class="icon-button" data-close-modal aria-label="Close">×</button></div><form id="upload-form"><label class="drop-zone" for="upload-files">${icon("upload")}<strong>Choose documents to upload</strong><span>PDF, DOCX, XLSX, CSV, TXT, and Markdown · Up to 25 MB each</span><input id="upload-files" name="files" type="file" multiple accept=".pdf,.docx,.xlsx,.xlsm,.csv,.txt,.md" required></label><div class="selected-files" id="selected-files"></div><fieldset class="group-select"><legend>Share with groups</legend><p>Only members of selected groups can search these documents.</p><div class="checkbox-list">${state.groups.length ? state.groups.map(group => `<label class="check-row"><input type="checkbox" name="group_ids" value="${group.id}"><span class="checkmark"></span><span><strong>${esc(group.name)}</strong><small>${esc(group.description || "Workspace group")}</small></span></label>`).join("") : `<p class="muted-text">You are not a member of any groups. Ask an administrator to add you first.</p>`}</div></fieldset><div class="modal-actions"><button class="button button-quiet" type="button" data-close-modal>Cancel</button><button class="button button-primary" type="submit">Upload and index</button></div><div class="form-error" id="upload-error"></div></form></div></div>`;
  document.querySelector("#upload-open").onclick = () => document.querySelector("#upload-modal").classList.remove("hidden");
  document.querySelectorAll("[data-close-modal]").forEach(button => button.onclick = () => document.querySelector("#upload-modal").classList.add("hidden"));
  document.querySelector("#document-search").oninput = event => document.querySelectorAll("#document-list tbody tr").forEach(row => row.hidden = !row.dataset.filename.includes(event.target.value.toLowerCase()));
  document.querySelectorAll("[data-delete]").forEach(button => button.onclick = () => deleteDocument(button.dataset.delete));
  document.querySelector("#upload-files").onchange = event => { document.querySelector("#selected-files").textContent = [...event.target.files].map(file => `${file.name} · ${formatBytes(file.size)}`).join("  |  "); };
  document.querySelector("#upload-form").onsubmit = uploadDocuments;
}

async function uploadDocuments(event) {
  event.preventDefault(); const form = event.currentTarget; const data = new FormData();
  [...form.querySelector("#upload-files").files].forEach(file => data.append("files", file));
  [...form.querySelectorAll('[name="group_ids"]:checked')].forEach(input => data.append("group_ids", input.value));
  const button = form.querySelector('[type="submit"]'); button.disabled = true; button.textContent = "Uploading and indexing…";
  try { const result = await request("/documents", { method: "POST", body: data }); toast(`${result.documents.length} document(s) added to the knowledge base.`); state.page = "documents"; await loadWorkspace(); render(); }
  catch (error) { form.querySelector("#upload-error").textContent = error.message; button.disabled = false; button.textContent = "Upload and index"; }
}
async function deleteDocument(id) { if (!confirm("Delete this document and remove it from search?")) return; try { await request(`/documents/${encodeURIComponent(id)}`, { method: "DELETE" }); await loadWorkspace(); renderDocuments(); toast("Document deleted."); } catch (error) { toast(error.message, true); } }

function renderChat() {
  const content = document.querySelector("#page-content");
  content.innerHTML = `<div class="chat-layout"><aside class="chat-history"><div class="history-heading"><div><span class="eyebrow muted">YOUR WORKSPACE</span><h2>Conversations</h2></div><button id="new-chat" class="icon-button add-chat" title="New conversation">${icon("plus")}</button></div><button class="new-chat-button" id="new-chat-secondary">${icon("plus")} New conversation</button><div class="conversation-list">${state.conversations.length ? state.conversations.map(convo => `<button class="conversation-item ${state.conversationId === convo.id ? "selected" : ""}" data-conversation="${esc(convo.id)}"><span class="conversation-glyph">${icon("chat")}</span><span class="conversation-text"><strong>${esc(convo.title || "New conversation")}</strong><small>${formatDate(convo.updated_at)}</small></span></button>`).join("") : `<p class="history-empty">Your conversations will appear here.</p>`}</div><div class="history-foot">${icon("shield")} Conversations are private to your account</div></aside><section class="chat-panel"><div class="chat-top"><div><span class="assistant-orb">${icon("spark")}</span><span><strong>Northstar assistant</strong><small>${state.groups.length ? `Searching ${state.groups.length} accessible group${state.groups.length === 1 ? "" : "s"}` : "No group access yet"}</small></span></div><span class="grounded-label">${icon("shield")} GROUNDED IN YOUR KNOWLEDGE</span></div><div class="message-list" id="message-list"></div><div class="prompt-area"><div class="suggestion-row"><button class="suggestion" data-prompt="What information is available in my team documents?">What can I find?</button><button class="suggestion" data-prompt="Summarize the key points from the available policies.">Summarize a policy</button><button class="suggestion" data-prompt="What are the key procedures I should know?">Key procedures</button></div><form class="prompt-box" id="chat-form"><textarea id="chat-input" rows="1" maxlength="4000" placeholder="Ask a question about your team's knowledge..." required></textarea><button class="send-button" type="submit" aria-label="Send message">${icon("send")}</button></form><div class="prompt-disclaimer">Answers are generated from documents you can access. Always verify critical details in the cited source.</div></div></section></div>`;
  document.querySelectorAll("[data-conversation]").forEach(button => button.onclick = () => selectConversation(button.dataset.conversation));
  document.querySelectorAll("#new-chat,#new-chat-secondary").forEach(button => button.onclick = newConversation);
  document.querySelectorAll("[data-prompt]").forEach(button => button.onclick = () => { const input = document.querySelector("#chat-input"); input.value = button.dataset.prompt; input.focus(); });
  document.querySelector("#chat-form").onsubmit = sendChat;
  if (state.conversationId) loadMessages(); else renderMessages();
}
async function openChat() { state.page = "chat"; render(); }
function newConversation() { state.conversationId = null; state.messages = []; localStorage.removeItem(CHAT_KEY); renderChat(); }
async function selectConversation(id) { state.conversationId = id; localStorage.setItem(CHAT_KEY, id); state.messages = []; renderChat(); }
async function loadMessages() { try { state.messages = await request(`/conversations/${encodeURIComponent(state.conversationId)}`); renderMessages(); } catch (error) { toast(error.message, true); } }
function renderMessagesLegacy() {
  const list = document.querySelector("#message-list"); if (!list) return;
  if (!state.messages.length) { list.innerHTML = `<div class="chat-welcome"><div class="welcome-orb">${icon("spark")}</div><span class="eyebrow muted">YOUR KNOWLEDGE ASSISTANT</span><h2>What would you like to know?</h2><p>Ask a question about documents shared with your groups. I’ll include sources so you can verify the answer.</p></div>`; return; }
  list.innerHTML = state.messages.map(message => `<article class="message ${message.role === "user" ? "message-user" : "message-assistant"}"><span class="message-avatar">${message.role === "user" ? initials(state.user.full_name) : icon("spark")}</span><div class="message-body"><span class="message-author">${message.role === "user" ? "You" : "Northstar assistant"}</span><div class="message-text">${esc(message.content).replace(/\n/g, "<br>")}</div>${message.sources?.length ? `<div class="source-list"><span class="source-label">SOURCES</span>${message.sources.map(source => `<div class="source-item"><span class="source-number">${esc(source.number || "↗")}</span><span><strong>${esc(source.filename || source.title || "Document")}</strong><small>${source.page ? `Page ${esc(source.page)}` : "Retrieved passage"}</small></span></div>`).join("")}</div>` : ""}</div></article>`).join("");
  list.scrollTop = list.scrollHeight;
}
async function sendChat(event) {
  event.preventDefault(); if (state.busy) return; const input = document.querySelector("#chat-input"); const question = input.value.trim(); if (!question) return;
  state.busy = true; state.messages.push({ role: "user", content: question, sources: [] }); input.value = ""; renderMessages();
  const list = document.querySelector("#message-list"); list.insertAdjacentHTML("beforeend", `<div class="thinking" id="thinking"><span></span><span></span><span></span> Searching your knowledge</div>`); list.scrollTop = list.scrollHeight;
  try { const result = await request("/chat", { method: "POST", body: JSON.stringify({ question, conversation_id: state.conversationId }) }); state.conversationId = result.conversation_id; localStorage.setItem(CHAT_KEY, state.conversationId); state.messages.push({ role: "assistant", content: result.answer, sources: result.sources }); state.conversations = await request("/conversations"); renderChat(); }
  catch (error) { state.messages.push({ role: "assistant", content: `I couldn't complete that request: ${error.message}`, sources: [] }); renderMessages(); }
  finally { state.busy = false; }
}

function renderAdmin() {
  const content = document.querySelector("#page-content");
  content.innerHTML = `<div class="page-heading"><div><span class="eyebrow muted">WORKSPACE CONTROLS</span><h1>Administration</h1><p>Manage groups, membership, and workspace activity.</p></div><span class="admin-badge">${icon("shield")} ADMINISTRATOR</span></div><div class="admin-tabs"><button class="admin-tab active" data-admin-tab="groups">Groups & access</button><button class="admin-tab" data-admin-tab="users">People <span>${state.users.length}</span></button><button class="admin-tab" data-admin-tab="audit">Activity log</button></div><div id="admin-content"></div>`;
  document.querySelectorAll("[data-admin-tab]").forEach(button => button.onclick = () => { document.querySelectorAll("[data-admin-tab]").forEach(item => item.classList.toggle("active", item === button)); ({ groups: renderAdminGroups, users: renderAdminUsers, audit: renderAudit }[button.dataset.adminTab])(); }); renderAdminGroups();
}
function renderAdminGroups() {
  const target = document.querySelector("#admin-content"); if (!target) return;
  target.innerHTML = `<div class="admin-intro"><div><h2>Groups</h2><p>Groups control which documents employees can discover and ask about.</p></div><button class="button button-primary" id="create-group">${icon("plus")} Create group</button></div><div class="group-admin-grid">${state.groups.length ? state.groups.map(group => `<article class="group-admin-card"><div class="group-card-head"><span class="group-icon">${icon("users")}</span><span class="member-count">${group.member_count ?? state.users.filter(user => user.groups.some(item => item.id === group.id)).length} MEMBERS</span></div><h3>${esc(group.name)}</h3><p>${esc(group.description || "No description provided")}</p><div class="group-members">${state.users.filter(user => user.groups.some(item => item.id === group.id)).slice(0, 4).map(user => `<span class="mini-avatar" title="${esc(user.full_name)}">${initials(user.full_name)}</span>`).join("")}<button class="add-member" data-manage-group="${group.id}" title="Manage members">${icon("plus")}</button><button class="member-action-label" data-manage-group="${group.id}">Manage members</button></div></article>`).join("") : `<div class="data-card">${emptyState("users", "No groups created", "Create a group to start managing document access.")}</div>`}</div><div class="data-card access-note">${icon("shield")}<div><strong>Access is enforced at retrieval</strong><p>Assistant searches include only documents shared with a user’s current groups.</p></div></div>`;
  document.querySelector("#create-group")?.addEventListener("click", createGroup);
  document.querySelectorAll("[data-manage-group]").forEach(button => button.onclick = () => manageMembers(Number(button.dataset.manageGroup)));
}
async function createGroup() {
  const name = prompt("Group name"); if (!name) return; const description = prompt("Short description (optional)") || "";
  try { await request("/groups", { method: "POST", body: JSON.stringify({ name, description }) }); await loadWorkspace(); renderAdminGroups(); toast("Group created."); } catch (error) { toast(error.message, true); }
}
async function manageMembers(groupId) {
  const group = state.groups.find(item => item.id === groupId); if (!group) return;
  const current = new Set(state.users.filter(user => user.groups.some(item => item.id === groupId)).map(user => user.id));
  const modal = document.createElement("div"); modal.className = "upload-modal"; modal.innerHTML = `<div class="modal-backdrop"></div><section class="modal-card member-modal"><div class="modal-heading"><div><span class="eyebrow muted">GROUP ACCESS</span><h2>Manage ${esc(group.name)}</h2><p>Select the people who should belong to this group.</p></div><button class="icon-button" data-close aria-label="Close">×</button></div><form><div class="member-picker">${state.users.map(user => `<label class="check-row"><input type="checkbox" value="${user.id}" ${current.has(user.id) ? "checked" : ""}><span class="checkmark"></span><span><strong>${esc(user.full_name)} ${user.role === "admin" ? `<em>Admin</em>` : ""}</strong><small>${esc(user.email)}${user.department ? ` · ${esc(user.department)}` : ""}</small></span></label>`).join("") || `<p class="muted-text">No accounts yet.</p>`}</div><div class="modal-actions"><button class="button button-quiet" type="button" data-close>Cancel</button><button class="button button-primary" type="submit">Save membership</button></div><div class="form-error"></div></form></section>`;
  document.body.append(modal); modal.querySelectorAll("[data-close],.modal-backdrop").forEach(button => button.onclick = () => modal.remove());
  modal.querySelector("form").onsubmit = async event => {
    event.preventDefault(); const save = event.currentTarget.querySelector('[type="submit"]'); save.disabled = true; save.textContent = "Saving…"; const selected = new Set([...modal.querySelectorAll('input[type="checkbox"]:checked')].map(input => Number(input.value)));
    try { await Promise.all([...selected].filter(id => !current.has(id)).map(id => request(`/groups/${groupId}/members`, { method: "POST", body: JSON.stringify({ user_id: id }) }))); await Promise.all([...current].filter(id => !selected.has(id)).map(id => request(`/groups/${groupId}/members/${id}`, { method: "DELETE" }))); modal.remove(); await loadWorkspace(); renderAdminGroups(); toast("Group membership updated."); }
    catch (error) { modal.querySelector(".form-error").textContent = error.message; save.disabled = false; save.textContent = "Save membership"; }
  };
}
function renderAdminUsers() {
  const target = document.querySelector("#admin-content"); if (!target) return;
  target.innerHTML = `<div class="admin-intro"><div><h2>People</h2><p>Review accounts and their current access groups.</p></div><span class="result-count">${state.users.length} accounts</span></div><div class="data-card"><div class="table-wrap"><table><thead><tr><th>PERSON</th><th>DEPARTMENT</th><th>ROLE</th><th>GROUPS</th><th>JOINED</th></tr></thead><tbody>${state.users.map(user => `<tr><td><div class="person-cell"><span class="user-avatar small">${initials(user.full_name)}</span><span><strong>${esc(user.full_name)}</strong><small>${esc(user.email)}</small></span></div></td><td>${esc(user.department || "—")}</td><td><span class="role-tag ${user.role}">${esc(user.role)}</span></td><td>${user.groups.map(group => `<span class="table-tag">${esc(group.name)}</span>`).join(" ") || "—"}</td><td>${formatDate(user.created_at)}</td></tr>`).join("")}</tbody></table></div></div>`;
}
async function renderAudit() {
  const target = document.querySelector("#admin-content"); if (!target) return; target.innerHTML = `<div class="admin-intro"><div><h2>Activity log</h2><p>Recent account, group, document, and assistant activity.</p></div></div><div class="data-card" id="audit-table">Loading activity…</div>`;
  try { const events = await request("/admin/audit"); const table = document.querySelector("#audit-table"); if (!table) return; table.innerHTML = events.length ? `<div class="table-wrap"><table><thead><tr><th>EVENT</th><th>ACTOR</th><th>DETAILS</th><th>TIME</th></tr></thead><tbody>${events.map(event => `<tr><td><span class="event-tag">${esc(event.action.replaceAll("_", " "))}</span></td><td>${esc(event.actor || "System")}</td><td>${esc(event.details || event.target || "—")}</td><td>${formatDate(event.created_at)}</td></tr>`).join("")}</tbody></table></div>` : emptyState("clock", "No activity yet", "Workspace activity will appear here."); } catch (error) { toast(error.message, true); }
}
async function logout() { try { await request("/auth/logout", { method: "POST" }); } catch { } clearSession(); state.page = "dashboard"; renderAuth(); }

function renderMessages() {
  const list = document.querySelector("#message-list");
  if (!list) return;
  if (!state.messages.length) {
    list.innerHTML = `<div class="chat-welcome"><div class="welcome-orb">${icon("spark")}</div><h2>Ask a question</h2><p>Ask about documents shared with your groups.</p></div>`;
    return;
  }
  list.innerHTML = state.messages.map(message => `<article class="message ${message.role === "user" ? "message-user" : "message-assistant"}"><span class="message-avatar">${message.role === "user" ? initials(state.user.full_name) : icon("spark")}</span><div class="message-body"><span class="message-author">${message.role === "user" ? "You" : "Assistant"}</span><div class="message-text">${renderMarkdown(message.content)}</div>${message.sources?.length ? `<div class="source-list"><span class="source-label">Sources</span>${message.sources.map((source,index) => `<div class="source-item"><span class="source-number">${index + 1}</span><span><strong>${esc(source.filename || source.title || "Document")}</strong><small>${source.page ? `Page ${esc(source.page)}` : source.sheet ? `Sheet ${esc(source.sheet)}` : "Retrieved passage"}</small></span></div>`).join("")}</div>` : ""}</div></article>`).join("");
  list.scrollTop = list.scrollHeight;
}

function removePromotionalCopy() {
  document.querySelectorAll(".brand-mark").forEach(node => {
    node.classList.add("logo-mark");
    node.innerHTML = '<img src="/assets/northstar%20logo%202%20no%20bg.png" alt="Northstar">';
  });
  document.querySelectorAll(".secure-label,.grounded-label,.prompt-disclaimer,.sidebar-help,.story-foot,.story-points,.auth-note,.auth-copyright").forEach(node => node.remove());
  document.querySelectorAll(".brand-light").forEach(node => node.remove());
  document.querySelectorAll(".brand > span:last-child,.brand-lockup > span:last-child").forEach(node => { node.textContent = "Northstar"; });
  document.querySelector(".story-content > .eyebrow")?.remove();
  const loginHeading = document.querySelector(".story-content h1");
  if (loginHeading) loginHeading.textContent = "Company knowledge, in one place.";
  const loginDescription = document.querySelector(".story-content > p");
  if (loginDescription) loginDescription.textContent = "Sign in to access documents shared with your groups.";
  const loginSubheading = document.querySelector(".auth-subtitle");
  if (loginSubheading) loginSubheading.textContent = "Use your work account to continue.";
  document.querySelector(".auth-panel .eyebrow")?.remove();
  document.querySelector(".welcome-copy .eyebrow")?.remove();
  const bannerTitle = document.querySelector(".welcome-copy h2");
  if (bannerTitle) bannerTitle.textContent = "Ask about documents shared with your groups.";
  const bannerDescription = document.querySelector(".welcome-copy p");
  if (bannerDescription) bannerDescription.textContent = "Search policies, reports, and team documents.";
  document.querySelector(".banner-art")?.remove();
}

const originalRenderAuth = renderAuth;
renderAuth = function(mode) { originalRenderAuth(mode); removePromotionalCopy(); };
const originalRender = render;
render = function() { originalRender(); removePromotionalCopy(); };
const originalRenderChat = renderChat;
renderChat = function() { originalRenderChat(); removePromotionalCopy(); };

async function boot() {
  if (!state.token) return renderAuth();
  try { await loadWorkspace(); render(); }
  catch (error) {
    if (!state.token) return renderAuth();
    app.innerHTML = `<main class="reconnect-screen"><span class="brand-mark logo-mark"><img src="/assets/northstar%20logo%202%20no%20bg.png" alt="Northstar"></span><p class="eyebrow muted">SESSION SAVED</p><h1>Your workspace is having trouble connecting.</h1><p>${esc(error.message)} Your sign-in is saved on this device.</p><button class="button button-primary" id="retry-session">Try again</button><button class="text-button reconnect-signout" id="reconnect-signout">Sign out</button></main>`;
    document.querySelector("#retry-session").onclick = boot;
    document.querySelector("#reconnect-signout").onclick = () => { clearSession(); renderAuth(); };
  }
}
boot();
