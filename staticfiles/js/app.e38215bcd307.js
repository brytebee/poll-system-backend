// Get API base URL from global variable set in template
const API_BASE_URL = window.API_BASE_URL || "/api";

let currentPoll = null;
let selectedOptions = [];

// ============= Auth State Management =============
function getToken() {
  return localStorage.getItem("access_token");
}

function setToken(access, refresh) {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}

function clearToken() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

function isAuthenticated() {
  return !!getToken();
}

function updateUIAuth() {
  const authElements = document.querySelectorAll(".auth-only");
  const guestElements = document.querySelectorAll(".guest-only");

  if (isAuthenticated()) {
    authElements.forEach((el) => el.classList.remove("hidden"));
    guestElements.forEach((el) => el.classList.add("hidden"));

    // Get user profile to display username
    getUserProfile();
  } else {
    authElements.forEach((el) => el.classList.add("hidden"));
    guestElements.forEach((el) => el.classList.remove("hidden"));
  }
}

async function getUserProfile() {
  try {
    const response = await apiCall("/auth/profile/");
    if (response.ok) {
      const data = await response.json();
      const usernameDisplay = document.getElementById("username-display");
      if (usernameDisplay) {
        usernameDisplay.textContent = `Hello, ${data.username}`;
      }
    }
  } catch (error) {
    console.error("Error fetching profile:", error);
  }
}

// ============= API Calls =============
async function apiCall(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
    updateUIAuth();
    throw new Error("Authentication required");
  }

  return response;
}

// ============= Auth Functions =============
async function login(e) {
  e.preventDefault();
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;

  try {
    const response = await apiCall("/auth/login/", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (response.ok) {
      setToken(data.access, data.refresh);
      updateUIAuth();
      closeModal("login-modal");
      showHome();
    } else {
      showError("login-error", data.detail || "Login failed");
    }
  } catch (error) {
    showError("login-error", "Network error. Please try again.");
  }
}

async function register(e) {
  e.preventDefault();
  const email = document.getElementById("register-email").value;
  const username = document.getElementById("register-username").value;
  const first_name = document.getElementById("register-firstname").value;
  const last_name = document.getElementById("register-lastname").value;
  const password = document.getElementById("register-password").value;
  const password_confirm = document.getElementById(
    "register-password-confirm"
  ).value;

  if (password !== password_confirm) {
    showError("register-error", "Passwords do not match");
    return;
  }

  try {
    const response = await apiCall("/auth/register/", {
      method: "POST",
      body: JSON.stringify({
        email,
        username,
        first_name,
        last_name,
        password,
        password_confirm,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      setToken(data.tokens.access, data.tokens.refresh);
      updateUIAuth();
      closeModal("register-modal");
      showHome();
    } else {
      showError("register-error", JSON.stringify(data));
    }
  } catch (error) {
    showError("register-error", "Network error. Please try again.");
  }
}

async function logout() {
  const refresh_token = localStorage.getItem("refresh_token");
  try {
    await apiCall("/auth/logout/", {
      method: "POST",
      body: JSON.stringify({ refresh_token }),
    });
  } catch (error) {
    console.error("Logout error:", error);
  }

  clearToken();
  updateUIAuth();
  showHome();
}

// ============= Poll Functions =============
async function loadPolls() {
  const container = document.getElementById("polls-container");
  container.innerHTML = '<div class="spinner"></div>';

  try {
    const response = await apiCall("/polls/");
    const data = await response.json();

    displayPolls(data.results || data);
  } catch (error) {
    container.innerHTML =
      '<p style="text-align: center; color: white;">Error loading polls</p>';
  }
}

function displayPolls(polls) {
  const container = document.getElementById("polls-container");

  if (polls.length === 0) {
    container.innerHTML =
      '<p style="text-align: center; color: white;">No polls found</p>';
    return;
  }

  container.innerHTML =
    '<div class="grid">' +
    polls
      .map(
        (poll) => `
        <div class="card">
            <div class="card-header">
                <div>
                    <h3 class="card-title">${escapeHtml(poll.title)}</h3>
                    <span class="badge ${
                      poll.is_active ? "badge-success" : "badge-danger"
                    }">
                        ${poll.is_active ? "Active" : "Closed"}
                    </span>
                </div>
            </div>
            <p style="color: var(--text-light); margin-bottom: 1rem;">${escapeHtml(
              poll.description || ""
            )}</p>
            <div class="card-meta">
                <span>📊 ${poll.total_votes || 0} votes</span>
                <span>👥 ${poll.unique_voters || 0} voters</span>
                ${
                  poll.category
                    ? `<span>🏷️ ${escapeHtml(poll.category.name)}</span>`
                    : ""
                }
            </div>
            <div style="display: flex; gap: 0.5rem;">
                <button class="btn btn-primary" onclick="openVoteModal('${
                  poll.id
                }')">View & Vote</button>
                <button class="btn btn-outline" onclick="viewResults('${
                  poll.id
                }')">Results</button>
            </div>
        </div>
    `
      )
      .join("") +
    "</div>";
}

async function createPoll(e) {
  e.preventDefault();

  const title = document.getElementById("poll-title").value;
  const description = document.getElementById("poll-description").value;
  const category = document.getElementById("poll-category").value;
  const allowMultiple = document.getElementById("allow-multiple-votes").checked;

  const optionInputs = document.querySelectorAll(
    "#poll-options-container input"
  );
  const options = Array.from(optionInputs)
    .map((input) => input.value.trim())
    .filter((text) => text)
    .map((text) => ({ text }));

  if (options.length < 2) {
    showError("create-poll-error", "Please provide at least 2 options");
    return;
  }

  try {
    const response = await apiCall("/polls/", {
      method: "POST",
      body: JSON.stringify({
        title,
        description,
        category,
        options,
        allow_multiple_votes: allowMultiple,
        is_active: true,
      }),
    });

    if (response.ok) {
      closeModal("create-poll-modal");
      // Reset form
      document.getElementById("poll-title").value = "";
      document.getElementById("poll-description").value = "";
      document.getElementById("allow-multiple-votes").checked = false;
      const container = document.getElementById("poll-options-container");
      container.innerHTML = `
                <input type="text" class="form-control" placeholder="Option 1" style="margin-bottom: 0.5rem;" required>
                <input type="text" class="form-control" placeholder="Option 2" style="margin-bottom: 0.5rem;" required>
            `;
      showHome();
    } else {
      const data = await response.json();
      showError("create-poll-error", JSON.stringify(data));
    }
  } catch (error) {
    showError("create-poll-error", "Network error. Please try again.");
  }
}

async function openVoteModal(pollId) {
  try {
    const response = await apiCall(`/polls/${pollId}/`);
    const poll = await response.json();
    currentPoll = poll;
    selectedOptions = [];

    document.getElementById("vote-modal-title").textContent = poll.title;

    const container = document.getElementById("vote-options-container");
    container.innerHTML = poll.options
      .map(
        (option) => `
            <div class="poll-option" onclick="selectOption('${option.id}', ${
          poll.allow_multiple_votes
        })">
                <div class="option-bar" style="width: ${
                  poll.total_votes > 0
                    ? (option.vote_count / poll.total_votes) * 100
                    : 0
                }%"></div>
                <div class="option-content">
                    <span>${escapeHtml(option.text)}</span>
                    <strong>${option.vote_count || 0} votes (${
          poll.total_votes > 0
            ? Math.round((option.vote_count / poll.total_votes) * 100)
            : 0
        }%)</strong>
                </div>
            </div>
        `
      )
      .join("");

    openModal("vote-modal");
  } catch (error) {
    alert("Error loading poll");
  }
}

function selectOption(optionId, allowMultiple) {
  if (!isAuthenticated()) {
    alert("Please login to vote");
    openLoginModal();
    return;
  }

  if (allowMultiple) {
    const index = selectedOptions.indexOf(optionId);
    if (index > -1) {
      selectedOptions.splice(index, 1);
    } else {
      selectedOptions.push(optionId);
    }
  } else {
    selectedOptions = [optionId];
  }

  document.querySelectorAll(".poll-option").forEach((el) => {
    el.classList.remove("selected");
  });

  selectedOptions.forEach((id) => {
    const element = document.querySelector(`[onclick*="${id}"]`);
    if (element) {
      element.classList.add("selected");
    }
  });
}

async function submitVote() {
  if (selectedOptions.length === 0) {
    showError("vote-error", "Please select an option");
    return;
  }

  try {
    const response = await apiCall(`/polls/${currentPoll.id}/vote/`, {
      method: "POST",
      body: JSON.stringify({
        option_id: selectedOptions[0],
      }),
    });

    if (response.ok) {
      closeModal("vote-modal");
      viewResults(currentPoll.id);
    } else {
      const data = await response.json();
      showError("vote-error", data.error || "Vote failed");
    }
  } catch (error) {
    showError("vote-error", "Network error. Please try again.");
  }
}

async function viewResults(pollId) {
  await openVoteModal(pollId);
}

async function showMyPolls() {
  if (!isAuthenticated()) {
    alert("Please login to view your polls");
    openLoginModal();
    return;
  }

  const container = document.getElementById("polls-container");
  container.innerHTML = '<div class="spinner"></div>';
  document.getElementById("hero-section").classList.add("hidden");

  try {
    const response = await apiCall("/polls/mine/");
    const data = await response.json();
    displayPolls(data.results || data);
  } catch (error) {
    container.innerHTML =
      '<p style="text-align: center; color: white;">Error loading your polls</p>';
  }
}

async function searchPolls() {
  const searchTerm = document.getElementById("search-input").value;
  const category = document.getElementById("category-filter").value;

  let url = "/polls/?";
  if (searchTerm) url += `search=${encodeURIComponent(searchTerm)}&`;
  if (category) url += `category=${category}&`;

  const container = document.getElementById("polls-container");
  container.innerHTML = '<div class="spinner"></div>';
  document.getElementById("hero-section").classList.add("hidden");

  try {
    const response = await apiCall(url);
    const data = await response.json();
    displayPolls(data.results || data);
  } catch (error) {
    container.innerHTML =
      '<p style="text-align: center; color: white;">Error searching polls</p>';
  }
}

// ============= Category Functions =============
async function loadCategories() {
  try {
    const response = await apiCall("/categories/");
    const data = await response.json();
    const categories = data.results || data;

    const filterSelect = document.getElementById("category-filter");
    const pollCategorySelect = document.getElementById("poll-category");

    categories.forEach((cat) => {
      filterSelect.innerHTML += `<option value="${cat.id}">${escapeHtml(
        cat.name
      )}</option>`;
      pollCategorySelect.innerHTML += `<option value="${cat.id}">${escapeHtml(
        cat.name
      )}</option>`;
    });
  } catch (error) {
    console.error("Error loading categories:", error);
  }
}

// ============= Modal Functions =============
function openModal(modalId) {
  document.getElementById(modalId).classList.add("active");
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.remove("active");
  document
    .querySelectorAll(".alert")
    .forEach((alert) => alert.classList.add("hidden"));
}

function openLoginModal() {
  closeModal("register-modal");
  openModal("login-modal");
}

function openRegisterModal() {
  closeModal("login-modal");
  openModal("register-modal");
}

function openCreatePollModal() {
  if (!isAuthenticated()) {
    alert("Please login to create a poll");
    openLoginModal();
    return;
  }
  openModal("create-poll-modal");
}

function addPollOption() {
  const container = document.getElementById("poll-options-container");
  const optionCount = container.querySelectorAll("input").length + 1;
  const input = document.createElement("input");
  input.type = "text";
  input.className = "form-control";
  input.placeholder = `Option ${optionCount}`;
  input.style.marginBottom = "0.5rem";
  container.appendChild(input);
}

// ============= Helper Functions =============
function showError(elementId, message) {
  const errorEl = document.getElementById(elementId);
  errorEl.textContent = message;
  errorEl.classList.remove("hidden");
  setTimeout(() => errorEl.classList.add("hidden"), 5000);
}

function showHome() {
  document.getElementById("hero-section").classList.remove("hidden");
  loadPolls();
}

function escapeHtml(text) {
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return text ? text.replace(/[&<>"']/g, (m) => map[m]) : "";
}

// Close modals when clicking outside
window.onclick = function (event) {
  if (event.target.classList.contains("modal")) {
    event.target.classList.remove("active");
  }
};

// ============= Initialize =============
document.addEventListener("DOMContentLoaded", () => {
  updateUIAuth();
  loadCategories();
  loadPolls();
});
