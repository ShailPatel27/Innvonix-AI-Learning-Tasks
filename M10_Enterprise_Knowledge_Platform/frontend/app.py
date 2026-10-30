import os
import html
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
API_URL = os.getenv("PLATFORM_API_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = 180

st.set_page_config(page_title="Enterprise Knowledge", layout="wide")
session_store = components.declare_component(
    "northstar_session_store",
    path=str(Path(__file__).resolve().parent / "session_component"),
)
st.markdown(
    """<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root { font-family:'DM Sans',sans-serif; color:#243149; }
    .stApp,[data-testid="stAppViewContainer"] { background:#f4f6fa; color:#243149; }
    [data-testid="stHeader"] { background:transparent; }
    [data-testid="stMainBlockContainer"] { max-width:1440px; padding:2.3rem 3rem 4rem; }
    [data-testid="stSidebar"] { background:#121e35; border-right:1px solid #23314b; }
    [data-testid="stSidebar"] * { color:#dce4f1; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#9eacc1; }
    [data-testid="stSidebar"] [data-testid="stRadio"] > label { color:#8494ad; font-size:.67rem; font-weight:700; letter-spacing:.13em; }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] { gap:.25rem; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label { padding:.55rem .65rem; border-radius:8px; transition:.15s ease; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#ffffff12; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label p { color:#c1ccdc; font-size:.88rem; }
    [data-testid="stSidebar"] button { border:1px solid #ffffff22; border-radius:9px; }
    [data-testid="stSidebar"] .stButton button { color:#c5d0e0; text-align:left; background:transparent; border-color:transparent; }
    [data-testid="stSidebar"] .stButton button:hover { color:#fff; background:#ffffff12; border-color:#ffffff12; }
    [data-testid="stSidebar"] .stButton button[kind="primary"] { color:#fff; background:#354d7e; border-color:#52699a; }
    [data-testid="stMetric"] { padding:1.05rem 1.2rem; border:1px solid #e7ebf2; border-radius:12px; background:white; box-shadow:0 3px 12px #20335208; }
    [data-testid="stMetricLabel"] { color:#7a879a; font-size:.72rem; }
    [data-testid="stMetricValue"] { color:#1f2d45; font-family:'Manrope',sans-serif; font-weight:700; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-color:#e6eaf1; border-radius:12px; background:white; box-shadow:0 3px 13px #20335208; }
    .stTabs [data-baseweb="tab-list"] { gap:1.4rem; border-bottom:1px solid #e4e9f1; }
    .stTabs [data-baseweb="tab"] { padding:.8rem .15rem; }
    .stButton button,.stFormSubmitButton button { min-height:2.55rem; border-radius:8px; font-weight:600; transition:.16s ease; }
    .stButton button[kind="primary"],.stFormSubmitButton button[kind="primary"] { border:0; color:white; background:#4566df; }
    .stButton button:hover,.stFormSubmitButton button:hover { border-color:#8da0e7; transform:translateY(-1px); }
    [data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stSelectbox"] [data-baseweb="select"] > div { border-radius:8px; }
    [data-testid="stChatMessage"] { border:1px solid #e8ecf2; border-radius:12px; background:white; }
    .brand-lockup { display:flex; align-items:center; gap:10px; color:#17243a; font:800 16px Manrope,sans-serif; letter-spacing:-.035em; }
    .brand-square { display:grid; place-items:center; width:36px; height:36px; border-radius:11px; color:white; background:linear-gradient(145deg,#6985ff,#3c5ed9); box-shadow:0 7px 18px #4665dc42; font:800 18px Manrope,sans-serif; }
    .login-hero { position:relative; min-height:510px; overflow:hidden; padding:35px; border-radius:18px; color:white; background:radial-gradient(ellipse at 80% 18%,#395893 0,transparent 38%),linear-gradient(145deg,#121e35,#1d365d); }
    .login-hero:after { position:absolute; right:-90px; bottom:-170px; width:360px; height:360px; border:1px solid #ffffff20; border-radius:50%; box-shadow:0 0 0 45px #ffffff08,0 0 0 90px #ffffff05; content:""; }
    .login-hero .brand-lockup { color:white; }.login-hero .brand-square { color:#324c9e; background:#e4eaff; box-shadow:none; }
    .login-copy { position:relative; z-index:1; margin-top:100px; }.login-copy .kicker,.kicker { color:#8396d8; font-size:.68rem; font-weight:700; letter-spacing:.14em; }
    .login-copy h1 { max-width:430px; margin:.75rem 0; color:#fff; font:800 clamp(2.2rem,4vw,3.3rem)/1.08 Manrope,sans-serif; letter-spacing:-.055em; }
    .login-copy h1 em { color:#9fb2ff; font-style:normal; }.login-copy p { max-width:400px; color:#c1cde0; font-size:.95rem; line-height:1.75; }
    .login-points { display:flex; flex-wrap:wrap; gap:9px; margin-top:25px; }.login-points span { padding:8px 10px; border:1px solid #ffffff24; border-radius:20px; color:#e2e9f5; background:#ffffff0b; font-size:.72rem; }
    .page-kicker { margin:0 0 .35rem; color:#8090a6; font-size:.68rem; font-weight:700; letter-spacing:.13em; }
    .page-title { margin:0; color:#1e2b43; font:800 clamp(1.75rem,3vw,2.15rem)/1.2 Manrope,sans-serif; letter-spacing:-.045em; }
    .page-subtitle { margin:.5rem 0 1.4rem; color:#78869a; font-size:.91rem; }
    .dashboard-banner { position:relative; overflow:hidden; padding:27px 30px; border-radius:15px; color:white; background:radial-gradient(ellipse at 88% 30%,#3c5c96 0,transparent 36%),linear-gradient(110deg,#172744,#294878); }
    .dashboard-banner h2 { max-width:550px; margin:.45rem 0; color:white; font:700 clamp(1.3rem,2.5vw,1.85rem)/1.35 Manrope,sans-serif; letter-spacing:-.035em; }
    .dashboard-banner p { max-width:560px; margin:.35rem 0 0; color:#c0cee3; font-size:.88rem; line-height:1.6; }
    .dashboard-banner .kicker { color:#aabaff; }.secure-chip { display:inline-flex; align-items:center; gap:6px; padding:7px 10px; border:1px solid #cfe9df55; border-radius:20px; color:#d7f0e7; background:#61bb9f1c; font-size:.68rem; font-weight:600; }
    .stDataFrame { border:1px solid #e7ebf2; border-radius:10px; overflow:hidden; }
    @media (max-width:900px) { [data-testid="stMainBlockContainer"] { padding:1.5rem 1.2rem 3rem; }.login-hero { min-height:410px; }.login-copy { margin-top:65px; } }
    @media (max-width:650px) { [data-testid="stMainBlockContainer"] { padding:1rem .8rem 2rem; }.login-hero { min-height:320px; padding:22px; }.login-copy { margin-top:45px; }.dashboard-banner { padding:22px; } }
    </style>""",
    unsafe_allow_html=True,
)


def api_request(method, path, token=None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.request(
            method,
            f"{API_URL}{path}",
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
        try:
            payload = response.json()
        except ValueError:
            payload = {"detail": response.text or "The server returned an invalid response."}
        if isinstance(payload, dict) and isinstance(payload.get("detail"), list):
            payload["detail"] = "; ".join(
                item.get("msg", str(item)) if isinstance(item, dict) else str(item)
                for item in payload["detail"]
            )
        return response.status_code, payload
    except requests.RequestException as error:
        return 0, {"detail": f"Could not connect to the API at {API_URL}: {error}"}


def save_auth(payload):
    st.session_state.access_token = payload["access_token"]
    st.session_state.current_user = payload["user"]
    st.session_state.conversation_id = None
    st.session_state.chat_messages = []


def clear_auth():
    st.session_state.access_token = None
    st.session_state.current_user = None
    st.session_state.chat_messages = []
    st.session_state.conversation_id = None
    st.session_state.clear_saved_session = True


def show_login():
    left, right = st.columns([1.05, .95], gap="large", vertical_alignment="center")
    with left:
        st.markdown(
            """<section class="login-hero">
              <div class="brand-lockup"><span class="brand-square">N</span><span>northstar<span style="color:#9baaca;font-weight:500">.work</span></span></div>
              <div class="login-copy"><span class="kicker">KNOWLEDGE, IN CONTEXT</span>
              <h1>Every answer has a source.</h1>
              <p>A secure workspace for the knowledge your teams rely on. Ask better questions and get grounded answers from the documents you can access.</p>
              <div class="login-points"><span>Group-level access</span><span>Source-linked answers</span></div></div>
            </section>""",
            unsafe_allow_html=True,
        )
    with right:
        with st.container(border=True):
            st.markdown('<div class="kicker">YOUR TEAM WORKSPACE</div>', unsafe_allow_html=True)
            st.markdown("### Sign in to Northstar")
            st.caption("Pick up where your team’s knowledge lives.")
            login_tab, signup_tab = st.tabs(["Sign in", "Create account"])

            with login_tab:
                with st.form("login_form"):
                    email = st.text_input("Work email", placeholder="you@company.com")
                    password = st.text_input("Password", type="password", placeholder="Your password")
                    submitted = st.form_submit_button("Sign in to workspace", type="primary", use_container_width=True)
                if submitted:
                    code, result = api_request(
                        "POST", "/auth/login", json={"email": email, "password": password}
                    )
                    if code == 200:
                        save_auth(result)
                        st.rerun()
                    st.error(result.get("detail", "Could not sign in."))

            with signup_tab:
                with st.form("signup_form"):
                    full_name = st.text_input("Full name", placeholder="Jordan Lee")
                    new_email = st.text_input("Work email", key="signup_email", placeholder="you@company.com")
                    department = st.text_input("Department", key="signup_department", placeholder="Engineering")
                    new_password = st.text_input(
                        "Password · 8 characters minimum", type="password", key="signup_password"
                    )
                    submitted = st.form_submit_button("Create employee account", type="primary", use_container_width=True)
                if submitted:
                    code, result = api_request(
                        "POST",
                        "/auth/signup",
                        json={
                            "full_name": full_name,
                            "email": new_email,
                            "department": department,
                            "password": new_password,
                        },
                    )
                    if code == 201:
                        save_auth(result)
                        st.rerun()
                    st.error(result.get("detail", "Could not create the account."))
            st.caption("New accounts are employees. An administrator grants access by assigning groups.")


def show_overview(token, user, groups):
    st.markdown('<div class="page-kicker">YOUR WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="page-title">Welcome back, {html.escape(user["full_name"].split()[0])}</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Your team knowledge, conversations, and access at a glance.</p>', unsafe_allow_html=True)
    st.markdown(
        """<div class="dashboard-banner"><span class="kicker">NORTHSTAR ASSISTANT</span>
        <h2>Find clarity in your company knowledge.</h2>
        <p>Ask a question and get a grounded answer with sources you can verify.</p></div>""",
        unsafe_allow_html=True,
    )
    documents_code, documents = api_request("GET", "/documents", token=token)
    conversations_code, conversations = api_request("GET", "/conversations", token=token)
    documents = documents if documents_code == 200 else []
    conversations = conversations if conversations_code == 200 else []
    metrics = st.columns(3)
    metrics[0].metric("AVAILABLE DOCUMENTS", len(documents), "Shared with your groups")
    metrics[1].metric("YOUR GROUPS", len(groups), "Knowledge spaces you can access")
    metrics[2].metric("CONVERSATIONS", len(conversations), "Saved assistant chats")

    recent_col, access_col = st.columns([1.45, 1], gap="large")
    with recent_col:
        st.markdown("#### Recently added")
        st.caption("Documents available in your workspace")
        with st.container(border=True):
            if documents:
                st.dataframe(
                    pd.DataFrame([
                        {
                            "Document": item["filename"],
                            "Shared with": item.get("shared_groups") or "—",
                            "Added": item.get("created_at", "")[:10],
                        }
                        for item in documents[:5]
                    ]),
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.write("Your knowledge base is ready for its first document.")
    with access_col:
        st.markdown("#### Your access")
        st.caption("Groups that determine what you can search")
        with st.container(border=True):
            if groups:
                for group in groups:
                    st.markdown(f"**{html.escape(group['name'])}**")
                    if group.get("description"):
                        st.caption(group["description"])
            else:
                st.info("An administrator needs to add you to a group before you can search shared documents.")


def show_sources(sources):
    if sources:
        with st.expander(f"Sources ({len(sources)})"):
            for source in sources:
                location = source["filename"]
                if source.get("page"):
                    location += f" | page {source['page']}"
                elif source.get("sheet"):
                    location += f" | sheet {source['sheet']}"
                st.write(f"**{location}**")
                if source.get("excerpt"):
                    st.caption(source["excerpt"])


def show_chat(token, groups):
    st.markdown('<div class="page-kicker">NORTHSTAR ASSISTANT</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Ask your knowledge base</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Answers are grounded in documents shared with your groups, with sources included.</p>', unsafe_allow_html=True)

    code, conversations = api_request("GET", "/conversations", token=token)
    if code != 200:
        st.error(conversations.get("detail", "Could not load conversations."))
        return

    active_conversation = st.session_state.get("conversation_id")
    if active_conversation:
        message_code, stored_messages = api_request(
            "GET", f"/conversations/{active_conversation}", token=token
        )
        if message_code == 200:
            st.session_state.chat_messages = stored_messages
        elif message_code == 404:
            st.session_state.conversation_id = None
            st.session_state.chat_messages = []

    button_col, select_col, load_col = st.columns([1, 3, 1])
    with button_col:
        if st.button("New chat", use_container_width=True):
            st.session_state.conversation_id = None
            st.session_state.chat_messages = []
            st.rerun()
    if conversations:
        with select_col:
            conversation_ids = [item["id"] for item in conversations]
            selected_id = st.selectbox(
                "Previous chats",
                conversation_ids,
                index=conversation_ids.index(st.session_state.conversation_id)
                if st.session_state.get("conversation_id") in conversation_ids
                else 0,
                format_func=lambda item_id: next(
                    (item["title"] for item in conversations if item["id"] == item_id), item_id
                ),
                label_visibility="collapsed",
            )
        with load_col:
            if st.button("Load", use_container_width=True):
                code, messages = api_request(
                    "GET", f"/conversations/{selected_id}", token=token
                )
                if code == 200:
                    st.session_state.conversation_id = selected_id
                    st.session_state.chat_messages = messages
                    st.rerun()
                st.error(messages.get("detail", "Could not load this conversation."))

    for message in st.session_state.get("chat_messages", []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            show_sources(message.get("sources", []))

    if not groups:
        st.info("You are not in a document group yet. Ask an administrator to add you to a group.")

    question = st.chat_input("Ask about documents shared with your groups", disabled=not groups)
    if question:
        st.session_state.chat_messages.append(
            {"role": "user", "content": question, "sources": []}
        )
        code, result = api_request(
            "POST",
            "/chat",
            token=token,
            json={
                "question": question,
                "conversation_id": st.session_state.get("conversation_id"),
            },
        )
        if code == 200:
            st.session_state.conversation_id = result["conversation_id"]
            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                }
            )
        else:
            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": result.get("detail", "The assistant could not answer."),
                    "sources": [],
                }
            )
        st.rerun()


def show_knowledge_base(token, groups):
    st.markdown('<div class="page-kicker">SHARED KNOWLEDGE</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Knowledge base</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Upload documents and choose which groups can use them to find answers.</p>', unsafe_allow_html=True)

    if not groups:
        st.info("An administrator must add you to a group before you can share documents.")
    else:
        group_by_label = {
            f"{group['name']} (ID {group['id']})": group["id"] for group in groups
        }
        selected_labels = st.multiselect(
            "Share with groups",
            list(group_by_label),
            help="Only members of the selected groups and administrators can retrieve these documents.",
        )
        files = st.file_uploader(
            "Choose files",
            type=["pdf", "docx", "xlsx", "xlsm", "csv", "txt", "md"],
            accept_multiple_files=True,
        )
        if st.button("Upload and index", disabled=not files or not selected_labels):
            form_data = [
                ("group_ids", str(group_by_label[label])) for label in selected_labels
            ]
            multipart_files = [
                (
                    "files",
                    (file.name, file.getvalue(), file.type or "application/octet-stream"),
                )
                for file in files
            ]
            with st.spinner("Extracting text and creating searchable chunks..."):
                code, result = api_request(
                    "POST",
                    "/documents",
                    token=token,
                    data=form_data,
                    files=multipart_files,
                )
            if code == 201:
                added = ", ".join(item["filename"] for item in result["documents"])
                st.success(f"Indexed {added} and shared it with the selected groups.")
                st.rerun()
            st.error(result.get("detail", "Could not upload the selected files."))

    code, documents = api_request("GET", "/documents", token=token)
    if code != 200:
        st.error(documents.get("detail", "Could not load documents."))
        return

    st.markdown("#### Documents available to you")
    if not documents:
        st.info("No documents have been shared with your groups yet.")
    for document in documents:
        details = (
            f"{document['filename']} | shared with {document.get('shared_groups') or 'no groups'}"
        )
        with st.container(border=True):
            left, right = st.columns([5, 1])
            left.write(details)
            left.caption(f"Uploaded by {document.get('uploader') or 'former user'} | {document['size_bytes']:,} bytes")
            if document["can_delete"] and right.button("Delete", key=f"delete_{document['id']}"):
                code, result = api_request(
                    "DELETE", f"/documents/{document['id']}", token=token
                )
                if code == 200:
                    st.success(result["message"])
                    st.rerun()
                st.error(result.get("detail", "Could not delete this document."))


def show_admin(token):
    st.markdown('<div class="page-kicker">WORKSPACE CONTROLS</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Administration</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Manage groups, membership, and workspace activity.</p>', unsafe_allow_html=True)
    group_tab, audit_tab = st.tabs(["Groups and users", "Audit history"])

    with group_tab:
        with st.form("create_group_form"):
            name = st.text_input("Group name")
            description = st.text_input("Description")
            create = st.form_submit_button("Create group")
        if create:
            code, result = api_request(
                "POST", "/groups", token=token, json={"name": name, "description": description}
            )
            if code == 201:
                st.success(f"Created group {result['name']}.")
                st.rerun()
            st.error(result.get("detail", "Could not create group."))

        groups_code, groups = api_request("GET", "/groups", token=token)
        users_code, users = api_request("GET", "/admin/users", token=token)
        if groups_code != 200 or users_code != 200:
            failure = groups if groups_code != 200 else users
            st.error(failure.get("detail", "Could not load administration data."))
            return

        if groups and users:
            group_by_label = {f"{g['name']} (ID {g['id']})": g for g in groups}
            user_by_label = {f"{u['full_name']} | {u['email']}": u for u in users}
            selected_group_label = st.selectbox("Select a group", list(group_by_label))
            selected_group = group_by_label[selected_group_label]
            current_members = {
                user["id"]
                for user in users
                if any(group["id"] == selected_group["id"] for group in user["groups"])
            }
            available_users = {
                label: user for label, user in user_by_label.items()
                if user["id"] not in current_members
            }
            if available_users:
                with st.form("add_member_form"):
                    member_label = st.selectbox("Add employee", list(available_users))
                    add_member = st.form_submit_button("Add to group")
                if add_member:
                    member = available_users[member_label]
                    code, result = api_request(
                        "POST",
                        f"/groups/{selected_group['id']}/members",
                        token=token,
                        json={"user_id": member["id"]},
                    )
                    if code == 201:
                        st.success(result["message"])
                        st.rerun()
                    st.error(result.get("detail", "Could not update group membership."))
            else:
                st.caption("All employee accounts already belong to this group.")

            members = [user for user in users if user["id"] in current_members]
            st.markdown("**Current members**")
            if not members:
                st.caption("No employees are assigned to this group yet.")
            for member in members:
                row_left, row_right = st.columns([4, 1])
                row_left.write(f"{member['full_name']} | {member['email']}")
                if row_right.button("Remove", key=f"remove_{selected_group['id']}_{member['id']}"):
                    code, result = api_request(
                        "DELETE",
                        f"/groups/{selected_group['id']}/members/{member['id']}",
                        token=token,
                    )
                    if code == 200:
                        st.success(result["message"])
                        st.rerun()
                    st.error(result.get("detail", "Could not remove this member."))

        st.markdown("#### Employee accounts")
        if users:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Name": user["full_name"],
                            "Email": user["email"],
                            "Department": user["department"],
                            "Role": user["role"],
                            "Groups": ", ".join(group["name"] for group in user["groups"]),
                        }
                        for user in users
                    ]
                ),
                hide_index=True,
                use_container_width=True,
            )

    with audit_tab:
        code, events = api_request("GET", "/admin/audit", token=token)
        if code == 200 and events:
            st.dataframe(pd.DataFrame(events), hide_index=True, use_container_width=True)
        elif code == 200:
            st.info("No activity has been recorded yet.")
        else:
            st.error(events.get("detail", "Could not load audit history."))


def select_workspace_page(page):
    st.session_state.workspace_page = page


def main():
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    clear_saved = st.session_state.pop("clear_saved_session", False)
    saved_token = session_store(
        token=st.session_state.access_token,
        clear=clear_saved,
        default=None,
        key="persistent-session",
        height=1,
    )
    if not clear_saved and not st.session_state.access_token and saved_token:
        st.session_state.access_token = saved_token

    token = st.session_state.access_token
    if not token:
        show_login()
        return

    code, user = api_request("GET", "/me", token=token)
    if code == 401:
        clear_auth()
        st.warning(user.get("detail", "Please sign in again."))
        st.rerun()
        return
    if code != 200:
        st.error(user.get("detail", "Could not connect to the workspace. Your sign-in is saved."))
        if st.button("Retry connection"):
            st.rerun()
        return
    st.session_state.current_user = user

    pages = ["Overview", "Assistant", "Knowledge Base"] + (["Administration"] if user["role"] == "admin" else [])
    if st.session_state.get("workspace_page") not in pages:
        st.session_state.workspace_page = "Overview"

    with st.sidebar:
        st.markdown(
            """<div class="brand-lockup" style="color:#fff;margin:3px 0 4px">
            <span class="brand-square">N</span><span>northstar<span style="color:#9baaca;font-weight:500">.work</span></span></div>
            <div style="margin:0 0 18px 46px;color:#8291a8;font-size:10px;letter-spacing:.13em">KNOWLEDGE WORKSPACE</div>""",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown('<div style="color:#8494ad;font-size:10px;font-weight:700;letter-spacing:.13em;margin:0 0 8px">NAVIGATION</div>', unsafe_allow_html=True)
        for index, page in enumerate(pages, start=1):
            active = st.session_state.workspace_page == page
            st.button(
                f"{index:02d}   {page}",
                key=f"nav_{page.lower().replace(' ', '_')}",
                type="primary" if active else "secondary",
                use_container_width=True,
                on_click=select_workspace_page,
                args=(page,),
            )
        st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"**{html.escape(user['full_name'])}**")
        st.caption(f"{user['department'] or 'Workspace member'} · {user['role'].title()}")
        if st.button("Sign out", use_container_width=True):
            api_request("POST", "/auth/logout", token=token)
            clear_auth()
            st.rerun()

    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px">'
        f'<div><span class="page-kicker">NORTHSTAR WORKSPACE</span><div style="color:#56647a;font-size:12px">{html.escape(st.session_state.workspace_page)}</div></div>'
        '<span class="secure-chip">● &nbsp;SECURE WORKSPACE</span></div>',
        unsafe_allow_html=True,
    )
    page = st.session_state.workspace_page
    if page == "Overview":
        show_overview(token, user, user["groups"])
    elif page == "Assistant":
        show_chat(token, user["groups"])
    elif page == "Knowledge Base":
        show_knowledge_base(token, user["groups"])
    elif page == "Administration" and user["role"] == "admin":
        show_admin(token)


main()
