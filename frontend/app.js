/* ==========================================================================
   SKILLPARITY INTELLIGENCE PLATFORM — Core SPA Application
   Bringing Higher Education into Parity with Industry Demand
   ========================================================================== */

const API_BASE = "http://localhost:8000/api";

// Global Application State
const state = {
  token: localStorage.getItem("skillparity_jwt_token") || localStorage.getItem("skillsync_jwt_token") || null,
  user: JSON.parse(localStorage.getItem("skillparity_user")) || JSON.parse(localStorage.getItem("skillsync_user")) || null,
  role: "landing", // 'landing', 'university', 'student', 'employer'
  currentTab: "overview",
  data: {
    universityOverview: null,
    latestCurriculum: null,
    industryJobs: [],
    industrySkills: [],
    universityGaps: [],
    universityRecos: [],
    studentProfile: null,
    studentGaps: null,
    studentRoadmap: null,
    studentProjects: [],
    employerSignals: null
  },
  charts: {}
};

// ----------------------------------------------------------------------------
// API CLIENT
// ----------------------------------------------------------------------------
async function apiFetch(endpoint, options = {}) {
  const headers = options.headers || {};
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  if (state.token) {
    headers["Authorization"] = `Bearer ${state.token}`;
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });

    if (response.status === 401) {
      logoutUser();
      throw new Error("Session expired. Please log in again.");
    }

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error ${response.status}`);
    }

    return await response.json();
  } catch (err) {
    console.error(`[API Error] ${endpoint}:`, err);
    throw err;
  }
}

// ----------------------------------------------------------------------------
// INITIALIZATION & NAVIGATION
// ----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();

  if (state.user) {
    state.role = state.user.role;
  }

  renderNavigation();
  navigateRole(state.role, "overview");
});

function setupEventListeners() {
  document.getElementById("btn-home").addEventListener("click", () => {
    navigateRole("landing");
  });

  document.getElementById("btn-role-switcher").addEventListener("click", openRoleSelectionModal);
  document.getElementById("btn-open-login").addEventListener("click", openLoginModal);

  const searchInput = document.getElementById("global-search-input");
  let searchTimeout = null;
  searchInput.addEventListener("input", (e) => {
    clearTimeout(searchTimeout);
    const q = e.target.value.trim();
    if (q.length > 0) {
      searchTimeout = setTimeout(() => handleGlobalSearch(q), 250);
    } else {
      document.getElementById("search-results-popup").style.display = "none";
    }
  });

  document.addEventListener("click", (e) => {
    const searchPopup = document.getElementById("search-results-popup");
    if (!e.target.closest(".search-box")) {
      searchPopup.style.display = "none";
    }
  });
}

function navigateRole(role, tab = "overview") {
  state.role = role;
  state.currentTab = tab;
  renderNavigation();
  renderView();
}

function renderNavigation() {
  const topNav = document.getElementById("top-nav-links");
  const activeRoleDot = document.getElementById("active-role-dot");
  const activeRoleLabel = document.getElementById("active-role-label");
  const authActions = document.getElementById("auth-actions");
  const subNavBar = document.getElementById("sub-nav-bar");
  const subNavLinks = document.getElementById("sub-nav-links");

  activeRoleDot.className = `role-dot ${state.role}`;
  activeRoleLabel.textContent = state.role === "landing" ? "Guest Mode" : (state.role.charAt(0).toUpperCase() + state.role.slice(1));

  if (state.user) {
    authActions.innerHTML = `
      <span style="font-size: 0.85rem; color: var(--text-muted); font-weight: 600;">
        ${state.user.full_name}
      </span>
      <button class="btn btn-outline btn-sm" onclick="logoutUser()">Sign Out</button>
    `;
  } else {
    authActions.innerHTML = `
      <button class="btn btn-outline btn-sm" onclick="openLoginModal()">Sign In</button>
    `;
  }

  if (state.role === "landing") {
    topNav.innerHTML = `
      <span class="nav-item-link" onclick="openAboutModal()">About</span>
      <span class="nav-item-link" onclick="openHowItWorksModal()">How it works</span>
      ${!state.user ? `<span class="nav-item-link" onclick="openLoginModal()">Sign in</span>` : ''}
    `;
    subNavBar.style.display = "none";
  } else {
    topNav.innerHTML = `
      <span class="nav-item-link" onclick="navigateRole('landing')">&larr; Back to Landing</span>
      <span class="nav-item-link ${state.role === 'university' ? 'active' : ''}" onclick="navigateRole('university')">University</span>
      <span class="nav-item-link ${state.role === 'student' ? 'active' : ''}" onclick="navigateRole('student')">Student</span>
      <span class="nav-item-link ${state.role === 'employer' ? 'active' : ''}" onclick="navigateRole('employer')">Employer</span>
    `;

    subNavBar.style.display = "block";
    let subTabsHTML = "";

    if (state.role === "university") {
      subTabsHTML = `
        <div class="sub-tab-item ${state.currentTab === 'overview' ? 'active' : ''}" onclick="switchTab('overview')">Overview</div>
        <div class="sub-tab-item ${state.currentTab === 'curriculum' ? 'active' : ''}" onclick="switchTab('curriculum')">Curriculum Upload</div>
        <div class="sub-tab-item ${state.currentTab === 'industry' ? 'active' : ''}" onclick="switchTab('industry')">Industry Intelligence</div>
        <div class="sub-tab-item ${state.currentTab === 'gaps' ? 'active' : ''}" onclick="switchTab('gaps')">Gap Analysis</div>
        <div class="sub-tab-item ${state.currentTab === 'recommendations' ? 'active' : ''}" onclick="switchTab('recommendations')">Recommendations</div>
        <div class="sub-tab-item ${state.currentTab === 'outcomes' ? 'active' : ''}" onclick="switchTab('outcomes')">Outcomes &amp; Signals</div>
      `;
    } else if (state.role === "student") {
      subTabsHTML = `
        <div class="sub-tab-item ${state.currentTab === 'overview' ? 'active' : ''}" onclick="switchTab('overview')">Overview</div>
        <div class="sub-tab-item ${state.currentTab === 'skills' ? 'active' : ''}" onclick="switchTab('skills')">Resume &amp; Skills</div>
        <div class="sub-tab-item ${state.currentTab === 'target' ? 'active' : ''}" onclick="switchTab('target')">Target Role</div>
        <div class="sub-tab-item ${state.currentTab === 'gaps' ? 'active' : ''}" onclick="switchTab('gaps')">Personal Gap Engine</div>
        <div class="sub-tab-item ${state.currentTab === 'roadmap' ? 'active' : ''}" onclick="switchTab('roadmap')">Career Roadmap</div>
        <div class="sub-tab-item ${state.currentTab === 'projects' ? 'active' : ''}" onclick="switchTab('projects')">Project Recommendations</div>
      `;
    } else if (state.role === "employer") {
      subTabsHTML = `
        <div class="sub-tab-item ${state.currentTab === 'overview' ? 'active' : ''}" onclick="switchTab('overview')">Overview</div>
        <div class="sub-tab-item ${state.currentTab === 'requirements' ? 'active' : ''}" onclick="switchTab('requirements')">Skill Requirements</div>
        <div class="sub-tab-item ${state.currentTab === 'validations' ? 'active' : ''}" onclick="switchTab('validations')">Validate Skills</div>
        <div class="sub-tab-item ${state.currentTab === 'feedback' ? 'active' : ''}" onclick="switchTab('feedback')">Submit Feedback</div>
        <div class="sub-tab-item ${state.currentTab === 'signals' ? 'active' : ''}" onclick="switchTab('signals')">Industry Signals</div>
      `;
    }

    subNavLinks.innerHTML = subTabsHTML;
  }
}

function switchTab(tab) {
  state.currentTab = tab;
  renderNavigation();
  renderView();
}

function destroyCharts() {
  Object.keys(state.charts).forEach(key => {
    if (state.charts[key]) {
      state.charts[key].destroy();
    }
  });
  state.charts = {};
}

async function renderView() {
  destroyCharts();
  const container = document.getElementById("app-view");

  if (state.role === "landing") {
    renderLandingView(container);
  } else if (state.role === "university") {
    renderUniversityView(container);
  } else if (state.role === "student") {
    renderStudentView(container);
  } else if (state.role === "employer") {
    renderEmployerView(container);
  }
}


// ============================================================================
// 1. REDESIGNED LANDING PAGE (SKILLPARITY BRANDING)
// ============================================================================
function renderLandingView(container) {
  container.innerHTML = `
    <!-- Centered Editorial Hero Unit -->
    <div class="landing-hero">
      <div class="eyebrow-pill">✦ WELCOME TO SKILLPARITY</div>
      <h1 class="landing-title">
        Choose your <span class="highlight-workspace">workspace</span>.
      </h1>
      <p class="landing-subtitle">
        Choose the workspace that matches your role and bring higher education into parity with industry demand.
      </p>
    </div>

    <!-- Three Horizontal Workspace Cards -->
    <div class="workspace-cards-grid">
      
      <!-- CARD 1: UNIVERSITY -->
      <div class="workspace-card university" onclick="navigateRole('university')">
        <div>
          <div class="card-top-icon-wrapper">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
              <path d="M6 6h10"/>
              <path d="M6 10h10"/>
            </svg>
          </div>
          <div class="card-tag">01 &mdash; ACADEMIC</div>
          <h2 class="card-title">UNIVERSITY</h2>
          <p class="card-description">
            Analyze curriculum, identify industry gaps and understand changing skill demand.
          </p>
        </div>
        <div class="card-cta-btn">
          Explore workspace <span class="arrow">&rarr;</span>
        </div>
      </div>

      <!-- CARD 2: STUDENT -->
      <div class="workspace-card student" onclick="navigateRole('student')">
        <div>
          <div class="card-top-icon-wrapper">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
              <path d="M6 12v5c3 3 9 3 12 0v-5"/>
            </svg>
          </div>
          <div class="card-tag">02 &mdash; CAREER</div>
          <h2 class="card-title">STUDENT</h2>
          <p class="card-description">
            Measure your skills against your target role and build a personalized career roadmap.
          </p>
        </div>
        <div class="card-cta-btn">
          Explore workspace <span class="arrow">&rarr;</span>
        </div>
      </div>

      <!-- CARD 3: EMPLOYER -->
      <div class="workspace-card employer" onclick="navigateRole('employer')">
        <div>
          <div class="card-top-icon-wrapper">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
            </svg>
          </div>
          <div class="card-tag">03 &mdash; INDUSTRY</div>
          <h2 class="card-title">EMPLOYER</h2>
          <p class="card-description">
            Define skill requirements, validate capabilities and provide industry feedback.
          </p>
        </div>
        <div class="card-cta-btn">
          Explore workspace <span class="arrow">&rarr;</span>
        </div>
      </div>

    </div>

    <!-- Bottom Micro-Section -->
    <div class="bottom-micro-section">
      <div class="micro-info-item">
        <div class="micro-info-title">INDUSTRY DATA</div>
        <div class="micro-info-desc">Skill demand signals</div>
      </div>
      <div class="micro-info-item">
        <div class="micro-info-title">SKILL INTELLIGENCE</div>
        <div class="micro-info-desc">Extraction &amp; normalization</div>
      </div>
      <div class="micro-info-item">
        <div class="micro-info-title">GAP ANALYSIS</div>
        <div class="micro-info-desc">Curriculum &amp; career alignment</div>
      </div>
      <div class="micro-info-item">
        <div class="micro-info-title">RECOMMENDATIONS</div>
        <div class="micro-info-desc">Actionable next steps</div>
      </div>
    </div>

    <!-- Subtle Abstract Data Flow Background Curves -->
    <div class="bg-curves-container">
      <svg viewBox="0 0 1200 120" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M0 60C300 120 600 0 900 60C1050 90 1150 30 1200 60" stroke="#B85C3A" stroke-width="1.5" stroke-dasharray="4 4"/>
        <path d="M0 40C250 0 550 100 850 40C1000 10 1120 70 1200 40" stroke="#355C52" stroke-width="1.5"/>
      </svg>
    </div>
  `;
}


// ============================================================================
// 2. UNIVERSITY WORKSPACE EXPERIENCE
// ============================================================================
async function renderUniversityView(container) {
  if (state.currentTab === "overview") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">ACADEMIC PORTAL</div>
          <h1>UNIVERSITY &mdash; Curriculum Intelligence</h1>
          <p>Global Institute of Technology &bull; Department of Computer Science &amp; Engineering</p>
        </div>
        <button class="btn btn-primary" onclick="switchTab('curriculum')">Analyze Curriculum PDF</button>
      </div>

      <div class="metric-banner" id="uni-metric-banner">
        <div class="metric-banner-left">
          <h2>Your curriculum currently aligns with</h2>
          <p style="margin-top: 0.4rem; font-size: 0.9rem;">Evaluated against regional labor market job requirements &amp; employer signals.</p>
        </div>
        <div>
          <div class="metric-banner-value" id="alignment-big-num">72%</div>
          <div class="metric-banner-label">OBSERVED INDUSTRY DEMAND</div>
        </div>
      </div>

      <div class="analytical-panel-grid">
        <div class="panel">
          <div class="panel-header">
            <h3 class="panel-title">INDUSTRY DEMAND vs. CURRICULUM COVERAGE</h3>
            <span class="badge badge-match">Top 8 Regional Skills</span>
          </div>
          <div style="height: 280px;"><canvas id="chart-uni-alignment"></canvas></div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <h3 class="panel-title">CRITICAL SKILL GAPS</h3>
            <button class="btn btn-outline btn-sm" onclick="switchTab('gaps')">View Full Matrix &rarr;</button>
          </div>
          <div id="uni-critical-gaps-list">
            <p>Loading critical gaps...</p>
          </div>
        </div>
      </div>

      <div class="panel" style="margin-top: 2rem;">
        <div class="panel-header">
          <h3 class="panel-title">RECOMMENDED CURRICULUM ACTIONS</h3>
          <button class="btn btn-outline btn-sm" onclick="switchTab('recommendations')">View All Recommendations</button>
        </div>

        <div class="numbered-actions-list">
          <div class="action-item-row">
            <div class="action-num">01</div>
            <div>
              <strong style="font-size: 1rem;">Integrate Production Containerization (Docker)</strong>
              <p style="font-size: 0.85rem; margin-top: 0.2rem;">High industry demand (70% of backend roles require Docker), while current syllabus lacks containerization modules.</p>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="switchTab('recommendations')">Review Module</button>
          </div>

          <div class="action-item-row">
            <div class="action-num">02</div>
            <div>
              <strong style="font-size: 1rem;">Add Cloud Computing Fundamentals &amp; AWS Lab</strong>
              <p style="font-size: 0.85rem; margin-top: 0.2rem;">Cloud deployment skills are missing from core curriculum despite appearing in 60% of regional job posts.</p>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="switchTab('recommendations')">Review Lab</button>
          </div>

          <div class="action-item-row">
            <div class="action-num">03</div>
            <div>
              <strong style="font-size: 1rem;">Introduce Modern REST API Design Standards</strong>
              <p style="font-size: 0.85rem; margin-top: 0.2rem;">Expand Web Technologies course to emphasize REST API design patterns and OpenAPI specs.</p>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="switchTab('recommendations')">Review Course</button>
          </div>
        </div>
      </div>
    `;

    try {
      const overview = await apiFetch("/analytics/university-overview");
      state.data.universityOverview = overview;
      document.getElementById("alignment-big-num").textContent = `${overview.alignment_pct}%`;

      const gapMatrix = await apiFetch("/gap/university");
      state.data.universityGaps = gapMatrix;

      const criticals = gapMatrix.filter(g => g.status === "Critical Gap");
      document.getElementById("uni-critical-gaps-list").innerHTML = `
        <div class="data-table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Skill</th>
                <th>Category</th>
                <th>Industry Demand</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              ${criticals.slice(0, 5).map(item => `
                <tr>
                  <td><strong>${item.skill}</strong></td>
                  <td>${item.category}</td>
                  <td><span style="font-weight: 700; color: var(--accent-terracotta);">${item.demandPct}%</span></td>
                  <td><span class="badge badge-critical">Critical Gap</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;

      const top8 = gapMatrix.slice(0, 8);
      const ctx = document.getElementById("chart-uni-alignment").getContext("2d");
      state.charts.alignment = new Chart(ctx, {
        type: "bar",
        data: {
          labels: top8.map(i => i.skill),
          datasets: [
            {
              label: "Industry Demand %",
              data: top8.map(i => i.demandPct),
              backgroundColor: "#B85C3A"
            },
            {
              label: "Curriculum Status",
              data: top8.map(i => i.inCurriculum ? 100 : 0),
              backgroundColor: top8.map(i => i.inCurriculum ? "#355C52" : "#A83A34")
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { labels: { color: "#1C1C1A", font: { family: "IBM Plex Sans" } } } },
          scales: {
            x: { ticks: { color: "#68645C" }, grid: { color: "#D8CEBC" } },
            y: { ticks: { color: "#68645C" }, grid: { color: "#D8CEBC" }, max: 100 }
          }
        }
      });

    } catch (err) {
      console.error(err);
    }

  } else if (state.currentTab === "curriculum") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">ANALYZE CURRICULUM</div>
          <h1>Curriculum Syllabus Upload &amp; Skill Extraction</h1>
          <p>Upload your curriculum document to identify the skills currently taught.</p>
        </div>
      </div>

      <div class="panel" style="margin-bottom: 2rem;">
        <div class="upload-dropzone" id="curriculum-dropzone" onclick="document.getElementById('curriculum-file-input').click()">
          <div class="upload-icon">📄</div>
          <h3 style="font-size: 1.2rem; margin-bottom: 0.5rem;">Select Curriculum PDF Document</h3>
          <p style="font-size: 0.88rem;">Drag &amp; drop your syllabus PDF file here, or click to browse files.</p>
          <input type="file" id="curriculum-file-input" accept="application/pdf" style="display: none;" onchange="handleCurriculumUpload(event)">
        </div>

        <div id="upload-progress-container" style="display: none; margin-top: 1.75rem;">
          <div class="section-eyebrow" style="margin-bottom: 1rem;">VISUAL PROCESSING SEQUENCE</div>

          <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1rem;">
            <div class="micro-info-item" id="step-01-node" style="padding: 0.6rem; border: 1px solid var(--border-subtle); border-radius: 4px;">01 DOCUMENT</div>
            <div class="micro-info-item" id="step-02-node" style="padding: 0.6rem; border: 1px solid var(--border-subtle); border-radius: 4px;">02 EXTRACTION</div>
            <div class="micro-info-item" id="step-03-node" style="padding: 0.6rem; border: 1px solid var(--border-subtle); border-radius: 4px;">03 SKILL MAPPING</div>
            <div class="micro-info-item" id="step-04-node" style="padding: 0.6rem; border: 1px solid var(--border-subtle); border-radius: 4px;">04 GAP ANALYSIS</div>
          </div>

          <div class="progress-bar-container">
            <div class="progress-bar-fill" id="upload-progress-fill"></div>
          </div>
          <div style="text-align: right; font-family: var(--font-mono); font-size: 0.8rem; font-weight: 700;" id="upload-pct-label">0%</div>
        </div>
      </div>

      <div id="curriculum-analysis-result"></div>
    `;

    try {
      const curriculum = await apiFetch("/curriculum/latest");
      state.data.latestCurriculum = curriculum;
      renderCurriculumAnalysisDetails(curriculum);
    } catch (err) {
      document.getElementById("curriculum-analysis-result").innerHTML = `
        <div class="panel" style="text-align: center; color: var(--text-muted);">
          No curriculum document analyzed yet. Upload a syllabus PDF above.
        </div>
      `;
    }

  } else if (state.currentTab === "industry") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">SKILL INTELLIGENCE</div>
          <h1>Live Industry Skill Demand Workspace</h1>
          <p>Real-time skill frequency, sector filters, and market demand proportions.</p>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <div style="display: flex; gap: 1rem; align-items: center;">
            <label class="form-label" style="margin: 0;">Filter Sector:</label>
            <select class="form-control" style="width: 220px;" id="industry-sector-select" onchange="loadIndustryIntelligenceData()">
              <option value="all">All Sectors</option>
              <option value="FinTech">FinTech &amp; Enterprise SaaS</option>
              <option value="Cloud Infrastructure">Cloud Infrastructure</option>
              <option value="Artificial Intelligence">Artificial Intelligence &amp; ML</option>
              <option value="Cybersecurity">Cybersecurity &amp; Defense</option>
            </select>
          </div>
          <span class="badge badge-match">Demo Dataset &bull; 10 Active Jobs</span>
        </div>

        <div id="industry-skills-bars-container">
          <p>Loading skill demand intelligence...</p>
        </div>
      </div>
    `;
    loadIndustryIntelligenceData();

  } else if (state.currentTab === "gaps") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">GAP ANALYSIS MATRIX</div>
          <h1>Curriculum vs. Industry Skill Gap Analysis</h1>
          <p>Automated evaluation matrix comparing taught concepts against regional hiring specifications.</p>
        </div>
      </div>

      <div class="panel">
        <div class="data-table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Skill Name</th>
                <th>Category</th>
                <th>Industry Demand %</th>
                <th>Curriculum Coverage</th>
                <th>Alignment Status</th>
              </tr>
            </thead>
            <tbody id="university-gap-matrix-body">
              <tr><td colspan="5">Calculating gap matrix...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
    loadUniversityGapMatrix();

  } else if (state.currentTab === "recommendations") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">ACTIONABLE RECOMMENDATIONS</div>
          <h1>Curriculum Recommendations Engine</h1>
          <p>Targeted academic updates, lab modules, and course revisions generated directly from detected gaps.</p>
        </div>
      </div>

      <div id="university-recos-container">
        <p>Loading gap recommendations...</p>
      </div>
    `;
    loadUniversityRecommendations();

  } else if (state.currentTab === "outcomes") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">OUTCOMES &amp; EMPLOYER SIGNALS</div>
          <h1>Employer Signals &amp; Feedback Logs</h1>
          <p>Direct feedback from regional employers on graduate skill deficiencies and required technologies.</p>
        </div>
      </div>

      <div class="panel" id="employer-signals-card">
        <p>Loading employer signals...</p>
      </div>
    `;
    loadEmployerSignalsView();
  }
}

// ----------------------------------------------------------------------------
// UNIVERSITY HELPER FUNCTIONS
// ----------------------------------------------------------------------------
async function handleCurriculumUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const progressContainer = document.getElementById("upload-progress-container");
  const fill = document.getElementById("upload-progress-fill");
  const pct = document.getElementById("upload-pct-label");

  progressContainer.style.display = "block";
  fill.style.width = "25%";
  pct.textContent = "25%";

  const formData = new FormData();
  formData.append("file", file);

  try {
    setTimeout(() => {
      fill.style.width = "50%";
      pct.textContent = "50%";
    }, 400);

    setTimeout(() => {
      fill.style.width = "75%";
      pct.textContent = "75%";
    }, 900);

    const curriculum = await apiFetch("/curriculum/upload", {
      method: "POST",
      body: formData
    });

    setTimeout(() => {
      fill.style.width = "100%";
      pct.textContent = "100%";

      state.data.latestCurriculum = curriculum;
      renderCurriculumAnalysisDetails(curriculum);
    }, 1400);

  } catch (err) {
    alert(`Upload failed: ${err.message}`);
    progressContainer.style.display = "none";
  }
}

function renderCurriculumAnalysisDetails(curriculum) {
  const resultDiv = document.getElementById("curriculum-analysis-result");
  if (!resultDiv) return;

  resultDiv.innerHTML = `
    <div class="panel" style="margin-top: 1.5rem;">
      <div class="panel-header">
        <div>
          <h3 class="panel-title">${curriculum.title}</h3>
          <p style="font-size: 0.85rem; margin-top: 0.2rem;">Processed file: ${curriculum.filename || 'Curriculum.pdf'}</p>
        </div>
        <span class="badge badge-match">${curriculum.confirmed_skills.length} SKILLS IDENTIFIED</span>
      </div>

      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem; background: var(--bg-main); padding: 1.25rem; border-radius: 6px; border: 1px solid var(--border-subtle);">
        <div>
          <div style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-dim); font-weight: 700;">PAGES PROCESSED</div>
          <div style="font-size: 1.8rem; font-weight: 800; font-family: var(--font-mono);">${curriculum.pages_processed}</div>
        </div>
        <div>
          <div style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-dim); font-weight: 700;">COURSES DETECTED</div>
          <div style="font-size: 1.8rem; font-weight: 800; font-family: var(--font-mono);">${curriculum.courses_count}</div>
        </div>
        <div>
          <div style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-dim); font-weight: 700;">TOTAL SKILLS</div>
          <div style="font-size: 1.8rem; font-weight: 800; font-family: var(--font-mono); color: var(--accent-terracotta);">${curriculum.skills_detected_count}</div>
        </div>
      </div>

      <div style="margin-bottom: 1.5rem;">
        <h4>Confirmed Curriculum Skills (Review &amp; Edit)</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.75rem;" id="confirmed-skills-pills">
          ${curriculum.confirmed_skills.map(skill => `
            <span class="skill-tag acquired">
              ${skill}
              <button style="background: none; border: none; color: var(--accent-terracotta); cursor: pointer; font-weight: 700;" onclick="removeCurriculumSkill('${skill}')">&times;</button>
            </span>
          `).join('')}
        </div>

        <div style="display: flex; gap: 0.5rem; margin-top: 1rem; max-width: 420px;">
          <input type="text" id="add-curriculum-skill-input" class="form-control" placeholder="Add custom skill (e.g. Docker)...">
          <button class="btn btn-secondary btn-sm" onclick="addCurriculumSkill()">Add Skill</button>
        </div>
      </div>

      <div>
        <h4>Detected Courses Detail</h4>
        <div class="data-table-container" style="margin-top: 0.5rem;">
          <table class="data-table">
            <thead>
              <tr>
                <th>Course Name</th>
                <th>Extracted Skills Covered</th>
              </tr>
            </thead>
            <tbody>
              ${curriculum.courses_detail.map(c => `
                <tr>
                  <td><strong>${c.name}</strong></td>
                  <td>${c.skills.map(s => `<span class="badge badge-match" style="margin-right: 4px;">${s}</span>`).join('') || '<span style="color: var(--text-dim)">Fundamentals</span>'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}

async function removeCurriculumSkill(skillToRemove) {
  const curriculum = state.data.latestCurriculum;
  if (!curriculum) return;
  curriculum.confirmed_skills = curriculum.confirmed_skills.filter(s => s !== skillToRemove);
  
  await apiFetch(`/curriculum/${curriculum.id}/skills`, {
    method: "PUT",
    body: JSON.stringify({ confirmed_skills: curriculum.confirmed_skills })
  });
  renderCurriculumAnalysisDetails(curriculum);
}

async function addCurriculumSkill() {
  const input = document.getElementById("add-curriculum-skill-input");
  const newSkill = input.value.trim();
  const curriculum = state.data.latestCurriculum;
  if (!newSkill || !curriculum) return;

  if (!curriculum.confirmed_skills.includes(newSkill)) {
    curriculum.confirmed_skills.push(newSkill);
    await apiFetch(`/curriculum/${curriculum.id}/skills`, {
      method: "PUT",
      body: JSON.stringify({ confirmed_skills: curriculum.confirmed_skills })
    });
  }
  input.value = "";
  renderCurriculumAnalysisDetails(curriculum);
}

async function loadIndustryIntelligenceData() {
  try {
    const analytics = await apiFetch(`/industry/skills`);
    state.data.industrySkills = analytics;

    const container = document.getElementById("industry-skills-bars-container");
    if (!container) return;

    container.innerHTML = `
      <div style="margin-top: 1rem;">
        ${analytics.map(item => `
          <div class="skill-bar-row">
            <strong>${item.skill}</strong>
            <div class="skill-bar-track">
              <div class="skill-bar-fill ${item.demandPct < 45 ? 'sage' : ''}" style="width: ${item.demandPct}%;"></div>
            </div>
            <span style="font-family: var(--font-mono); font-weight: 700; font-size: 0.85rem;">${item.demandPct}%</span>
          </div>
        `).join('')}
      </div>
    `;
  } catch (err) {
    console.error(err);
  }
}

async function loadUniversityGapMatrix() {
  try {
    const matrix = await apiFetch("/gap/university");
    state.data.universityGaps = matrix;
    const tbody = document.getElementById("university-gap-matrix-body");
    if (!tbody) return;

    tbody.innerHTML = matrix.map(item => `
      <tr>
        <td><strong>${item.skill}</strong></td>
        <td>${item.category}</td>
        <td><span style="font-family: var(--font-mono); font-weight: 700;">${item.demandPct}%</span></td>
        <td>${item.inCurriculum ? '<span style="color: var(--accent-sage); font-weight: 700;">✓ MATCH</span>' : '<span style="color: var(--accent-terracotta); font-weight: 700;">! GAP</span>'}</td>
        <td><span class="badge badge-${item.status.includes('Critical') ? 'critical' : (item.status.includes('Partial') ? 'partial' : (item.status.includes('Emerging') ? 'emerging' : (item.status.includes('Obsolete') ? 'declining' : 'match')))}">${item.status}</span></td>
      </tr>
    `).join('');
  } catch (err) {
    console.error(err);
  }
}

async function loadUniversityRecommendations() {
  try {
    const recos = await apiFetch("/recommendations/university");
    state.data.universityRecos = recos;
    const container = document.getElementById("university-recos-container");
    if (!container) return;

    container.innerHTML = recos.map((r, idx) => `
      <div class="action-item-row" style="margin-bottom: 1rem;">
        <div class="action-num">0${idx + 1}</div>
        <div>
          <strong style="font-size: 1.05rem;">${r.title}</strong>
          <span class="badge badge-critical" style="margin-left: 8px;">Target Gap: ${r.gap_skill}</span>
          <p style="font-size: 0.88rem; margin-top: 0.4rem;">${r.description}</p>
          <div style="margin-top: 0.6rem; font-size: 0.82rem; color: var(--text-main); background: var(--bg-main); padding: 0.6rem 0.85rem; border-radius: 4px; border: 1px solid var(--border-subtle);">
            <strong>Module:</strong> ${r.suggested_module} &bull; <strong>Lab Project:</strong> ${r.suggested_project}
          </div>
        </div>
        <div>
          <button class="btn btn-primary btn-sm" onclick="alert('Recommendation integrated!')">Integrate Module</button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error(err);
  }
}

async function loadEmployerSignalsView() {
  try {
    const signals = await apiFetch("/employer/signals");
    state.data.employerSignals = signals;
    const card = document.getElementById("employer-signals-card");
    if (!card) return;

    card.innerHTML = `
      <div class="panel-header">
        <h3 class="panel-title">Regional Employer Feedback &amp; Signal Feed</h3>
        <span class="badge badge-match">${signals.total_signals} Total Signals Collected</span>
      </div>

      <div class="analytical-panel-grid" style="margin-bottom: 1.5rem;">
        <div>
          <h4 style="margin-bottom: 0.75rem;">Top Skills Employers Struggle to Find</h4>
          <ul style="list-style: none; padding: 0;">
            ${(signals.top_difficult_to_find.length ? signals.top_difficult_to_find : [['Docker', 4], ['AWS Cloud', 3], ['Kubernetes', 2]]).map(([skill, cnt]) => `
              <li style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px dashed var(--border-subtle);">
                <strong>${skill}</strong>
                <span class="badge badge-critical">${cnt} Employers</span>
              </li>
            `).join('')}
          </ul>
        </div>

        <div>
          <h4 style="margin-bottom: 0.75rem;">Top Skills Missing in Graduates</h4>
          <ul style="list-style: none; padding: 0;">
            ${(signals.top_missing_in_graduates.length ? signals.top_missing_in_graduates : [['Production Dockerization', 5], ['REST Security Standards', 4], ['CI/CD Pipelines', 3]]).map(([skill, cnt]) => `
              <li style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px dashed var(--border-subtle);">
                <strong>${skill}</strong>
                <span class="badge badge-gap">${cnt} Employers</span>
              </li>
            `).join('')}
          </ul>
        </div>
      </div>

      <h4>Recent Employer Submissions</h4>
      <div class="data-table-container" style="margin-top: 0.75rem;">
        <table class="data-table">
          <thead>
            <tr>
              <th>Company</th>
              <th>Date</th>
              <th>Target Tech to Teach</th>
              <th>Feedback Notes</th>
            </tr>
          </thead>
          <tbody>
            ${signals.recent_feedbacks.map(f => `
              <tr>
                <td><strong>${f.company}</strong></td>
                <td>${f.created_at}</td>
                <td>${f.target_tech.map(t => `<span class="badge badge-emerging" style="margin-right: 4px;">${t}</span>`).join('')}</td>
                <td>${f.notes}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    console.error(err);
  }
}


// ============================================================================
// 3. STUDENT EXPERIENCE
// ============================================================================
async function renderStudentView(container) {
  if (state.currentTab === "overview") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">CAREER READINESS WORKSPACE</div>
          <h1 id="student-hero-title">Your path to Backend Developer</h1>
          <p>Personal skill gap analysis, readiness scores, and customized roadmap.</p>
        </div>
        <button class="btn btn-primary" onclick="switchTab('skills')">Upload Resume (PDF)</button>
      </div>

      <div class="metric-banner">
        <div class="metric-banner-left">
          <h2>CURRENT ALIGNMENT READINESS SCORE</h2>
          <p style="margin-top: 0.4rem; font-size: 0.9rem;">Calculated based on target role required &amp; recommended skills.</p>
        </div>
        <div>
          <div class="metric-banner-value" id="student-alignment-big-num" style="color: var(--accent-sage);">68%</div>
          <div class="metric-banner-label">TARGET ROLE ALIGNMENT</div>
        </div>
      </div>

      <div class="analytical-panel-grid">
        <div class="panel">
          <div class="panel-header">
            <h3 class="panel-title">WHAT YOU ALREADY HAVE</h3>
            <span class="badge badge-match">Matched Skills</span>
          </div>
          <div id="student-skills-have-list" style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
            <p>Loading confirmed skills...</p>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <h3 class="panel-title">WHAT YOU NEED</h3>
            <span class="badge badge-critical">Critical Missing Gaps</span>
          </div>
          <div id="student-skills-need-list" style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
            <p>Loading missing gaps...</p>
          </div>
        </div>
      </div>
    `;

    try {
      const gapData = await apiFetch("/gap/student");
      state.data.studentGaps = gapData;

      document.getElementById("student-hero-title").textContent = `Your path to ${gapData.target_role}`;
      document.getElementById("student-alignment-big-num").textContent = `${gapData.alignment_pct}%`;

      const matched = gapData.skill_gaps.filter(s => s.status === 'MATCH');
      const missing = gapData.skill_gaps.filter(s => s.status.includes('GAP'));

      document.getElementById("student-skills-have-list").innerHTML = matched.map(s => `
        <span class="skill-tag acquired">✓ ${s.skill}</span>
      `).join('') || '<span style="color: var(--text-dim)">No matched skills yet.</span>';

      document.getElementById("student-skills-need-list").innerHTML = missing.map(s => `
        <span class="skill-tag missing">! ${s.skill} (${s.type})</span>
      `).join('') || '<span style="color: var(--accent-sage)">No missing gaps! You are 100% ready.</span>';

    } catch (err) {
      console.error(err);
    }

  } else if (state.currentTab === "skills") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">RESUME ANALYSIS</div>
          <h1>Resume Upload &amp; Skill Extraction</h1>
          <p>Upload your resume PDF to extract skills via PyPDF taxonomy engine.</p>
        </div>
      </div>

      <div class="panel" style="margin-bottom: 2rem;">
        <div class="upload-dropzone" onclick="document.getElementById('resume-file-input').click()">
          <div class="upload-icon">📄</div>
          <h3 style="font-size: 1.2rem; margin-bottom: 0.5rem;">Select Resume PDF File</h3>
          <p style="font-size: 0.88rem;">Click or drag your resume PDF here to parse skills.</p>
          <input type="file" id="resume-file-input" accept="application/pdf" style="display: none;" onchange="handleResumeUpload(event)">
        </div>
      </div>

      <div id="student-skills-profile-card"></div>
    `;
    loadStudentSkillsProfile();

  } else if (state.currentTab === "target") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">TARGET ROLE SELECTOR</div>
          <h1>Choose Target Career Track</h1>
          <p>Select your desired role to calibrate your readiness gap engine.</p>
        </div>
      </div>

      <div class="panel">
        <div class="form-group" style="max-width: 400px;">
          <label class="form-label">Target Role Profile:</label>
          <select class="form-control" id="target-role-select" onchange="updateStudentTargetRole()">
            <option value="Backend Developer">Backend Developer</option>
            <option value="AI Engineer">AI Engineer</option>
            <option value="Cloud & DevOps Engineer">Cloud &amp; DevOps Engineer</option>
            <option value="Data Analyst">Data Analyst</option>
            <option value="Full Stack Developer">Full Stack Developer</option>
            <option value="Cybersecurity Specialist">Cybersecurity Specialist</option>
          </select>
        </div>

        <div id="target-role-requirements-breakdown" style="margin-top: 1.5rem;"></div>
      </div>
    `;
    loadTargetRoleRequirements();

  } else if (state.currentTab === "gaps") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">PERSONAL GAP ANALYSIS</div>
          <h1>Personal Skill Gap Evaluation Matrix</h1>
          <p>Evaluation of confirmed student skills against target role required and recommended skills.</p>
        </div>
      </div>

      <div class="panel">
        <div class="data-table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Target Skill</th>
                <th>Requirement Level</th>
                <th>Gap Status</th>
              </tr>
            </thead>
            <tbody id="student-gaps-table-body">
              <tr><td colspan="3">Calculating student gaps...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
    loadStudentGapsTable();

  } else if (state.currentTab === "roadmap") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">CAREER ROADMAP</div>
          <h1>Personalized Learning Pipeline</h1>
          <p>Horizontal 4-stage roadmap connected to your confirmed skills and gaps.</p>
        </div>
      </div>

      <div id="student-roadmap-container">
        <p>Generating career roadmap...</p>
      </div>
    `;
    loadStudentRoadmapView();

  } else if (state.currentTab === "projects") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">PROJECT RECOMMENDATIONS</div>
          <h1>Recommended Portfolio Projects</h1>
          <p>Projects designed specifically to bridge your missing skills.</p>
        </div>
      </div>

      <div id="student-projects-container">
        <p>Loading project recommendations...</p>
      </div>
    `;
    loadStudentProjectsView();
  }
}

async function handleResumeUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const profile = await apiFetch("/resume/upload", {
      method: "POST",
      body: formData
    });
    state.data.studentProfile = profile;
    alert("Resume processed successfully!");
    renderStudentSkillsProfileCard(profile);
  } catch (err) {
    alert(`Resume upload failed: ${err.message}`);
  }
}

async function loadStudentSkillsProfile() {
  try {
    const profile = await apiFetch("/student/profile");
    state.data.studentProfile = profile;
    renderStudentSkillsProfileCard(profile);
  } catch (err) {
    console.error(err);
  }
}

function renderStudentSkillsProfileCard(profile) {
  const container = document.getElementById("student-skills-profile-card");
  if (!container) return;

  container.innerHTML = `
    <div class="panel">
      <div class="panel-header">
        <h3 class="panel-title">Confirmed Student Skills Profile</h3>
        <span class="badge badge-match">${profile.resume_filename || 'Default Profile'}</span>
      </div>

      <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.5rem;">
        ${profile.confirmed_skills.map(s => `
          <span class="skill-tag acquired">
            ${s}
            <button style="background: none; border: none; color: var(--accent-terracotta); cursor: pointer; font-weight: 700;" onclick="removeStudentSkill('${s}')">&times;</button>
          </span>
        `).join('')}
      </div>

      <div style="display: flex; gap: 0.5rem; max-width: 400px;">
        <input type="text" id="add-student-skill-input" class="form-control" placeholder="Add skill (e.g. FastAPI)...">
        <button class="btn btn-secondary btn-sm" onclick="addStudentSkill()">Add Skill</button>
      </div>
    </div>
  `;
}

async function removeStudentSkill(skillToRemove) {
  const profile = state.data.studentProfile;
  if (!profile) return;
  profile.confirmed_skills = profile.confirmed_skills.filter(s => s !== skillToRemove);
  
  await apiFetch("/student/profile", {
    method: "PUT",
    body: JSON.stringify({ confirmed_skills: profile.confirmed_skills })
  });
  renderStudentSkillsProfileCard(profile);
}

async function addStudentSkill() {
  const input = document.getElementById("add-student-skill-input");
  const skill = input.value.trim();
  const profile = state.data.studentProfile;
  if (!skill || !profile) return;

  if (!profile.confirmed_skills.includes(skill)) {
    profile.confirmed_skills.push(skill);
    await apiFetch("/student/profile", {
      method: "PUT",
      body: JSON.stringify({ confirmed_skills: profile.confirmed_skills })
    });
  }
  input.value = "";
  renderStudentSkillsProfileCard(profile);
}

async function loadTargetRoleRequirements() {
  try {
    const roles = await apiFetch("/industry/roles");
    const profile = await apiFetch("/student/profile");
    
    const select = document.getElementById("target-role-select");
    if (select && profile.target_role) {
      select.value = profile.target_role;
    }

    renderRoleBreakdown(select ? select.value : "Backend Developer", roles);
  } catch (err) {
    console.error(err);
  }
}

async function updateStudentTargetRole() {
  const select = document.getElementById("target-role-select");
  const newRole = select.value;
  try {
    await apiFetch("/student/profile", {
      method: "PUT",
      body: JSON.stringify({ target_role: newRole })
    });
    const roles = await apiFetch("/industry/roles");
    renderRoleBreakdown(newRole, roles);
  } catch (err) {
    console.error(err);
  }
}

function renderRoleBreakdown(roleName, roles) {
  const div = document.getElementById("target-role-requirements-breakdown");
  if (!div) return;

  const roleData = roles[roleName] || roles["Backend Developer"];
  div.innerHTML = `
    <h4>Required Skills for ${roleName}</h4>
    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.5rem 0 1.5rem;">
      ${roleData.required.map(s => `<span class="badge badge-critical">${s}</span>`).join('')}
    </div>

    <h4>Recommended Skills</h4>
    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
      ${roleData.recommended.map(s => `<span class="badge badge-emerging">${s}</span>`).join('')}
    </div>
  `;
}

async function loadStudentGapsTable() {
  try {
    const gapData = await apiFetch("/gap/student");
    const tbody = document.getElementById("student-gaps-table-body");
    if (!tbody) return;

    tbody.innerHTML = gapData.skill_gaps.map(item => `
      <tr>
        <td><strong>${item.skill}</strong></td>
        <td>${item.type}</td>
        <td><span class="badge badge-${item.status === 'MATCH' ? 'match' : (item.status === 'PARTIAL' ? 'partial' : 'critical')}">${item.status}</span></td>
      </tr>
    `).join('');
  } catch (err) {
    console.error(err);
  }
}

async function loadStudentRoadmapView() {
  try {
    const roadmapData = await apiFetch("/student/roadmap");
    const container = document.getElementById("student-roadmap-container");
    if (!container) return;

    container.innerHTML = `
      <div class="roadmap-horizontal-pipeline">
        ${roadmapData.stages.map(stage => `
          <div class="roadmap-stage-column">
            <div class="roadmap-stage-num">${stage.stage}</div>
            <div class="roadmap-stage-title">${stage.title}</div>
            <p style="font-size: 0.82rem; color: var(--text-muted);">${stage.description}</p>
            <div style="display: flex; flex-direction: column; gap: 0.4rem; margin-top: 0.5rem;">
              ${stage.skills.map(s => `
                <span class="skill-tag ${s.acquired ? 'acquired' : 'missing'}">
                  ${s.acquired ? '✓' : '!'} ${s.name}
                </span>
              `).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    `;
  } catch (err) {
    console.error(err);
  }
}

async function loadStudentProjectsView() {
  try {
    const projects = await apiFetch("/student/projects");
    const container = document.getElementById("student-projects-container");
    if (!container) return;

    container.innerHTML = projects.map(p => `
      <div class="panel" style="margin-bottom: 1.5rem;">
        <div class="panel-header">
          <div>
            <h3 class="panel-title">${p.title}</h3>
            <span class="badge badge-match" style="margin-top: 0.3rem;">Difficulty: ${p.difficulty} &bull; Duration: ${p.duration}</span>
          </div>
        </div>
        <p style="margin-bottom: 1rem;">${p.description}</p>
        <div style="margin-bottom: 1rem;">
          <strong>Skills Developed:</strong>
          <div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.4rem;">
            ${p.skills_covered.map(s => `<span class="badge badge-emerging">${s}</span>`).join('')}
          </div>
        </div>
        <button class="btn btn-primary btn-sm" onclick="alert('Project repository template generated!')">Start Project</button>
      </div>
    `).join('');
  } catch (err) {
    console.error(err);
  }
}


// ============================================================================
// 4. EMPLOYER EXPERIENCE
// ============================================================================
async function renderEmployerView(container) {
  if (state.currentTab === "overview") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">EMPLOYER WORKSPACE</div>
          <h1>Define the skills your industry needs.</h1>
          <p>Communicate industry hiring standards and guide university curriculum development.</p>
        </div>
        <button class="btn btn-primary" onclick="switchTab('requirements')">Create Requirement</button>
      </div>

      <div class="analytical-panel-grid">
        <div class="panel">
          <h4>ACTIVE REQUIREMENTS</h4>
          <div style="font-family: var(--font-mono); font-size: 3rem; font-weight: 800; margin-top: 0.5rem;">12</div>
        </div>
        <div class="panel">
          <h4>SUBMITTED FEEDBACK LOGS</h4>
          <div style="font-family: var(--font-mono); font-size: 3rem; font-weight: 800; margin-top: 0.5rem; color: var(--accent-terracotta);">18</div>
        </div>
      </div>
    `;

  } else if (state.currentTab === "requirements") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">SKILL REQUIREMENTS</div>
          <h1>Create Role Skill Requirement</h1>
          <p>Define mandatory and recommended skills for open positions.</p>
        </div>
      </div>

      <div class="panel" style="max-width: 600px;">
        <form id="form-employer-req" onsubmit="handleEmployerRequirementSubmit(event)">
          <div class="form-group">
            <label class="form-label">Company Name:</label>
            <input type="text" id="req-company" class="form-control" value="Nexus Financial SaaS" required>
          </div>
          <div class="form-group">
            <label class="form-label">Job Role Title:</label>
            <input type="text" id="req-role" class="form-control" value="Backend Developer" required>
          </div>
          <div class="form-group">
            <label class="form-label">Required Skills (Comma separated):</label>
            <input type="text" id="req-required" class="form-control" value="Python, SQL, REST APIs, Docker" required>
          </div>
          <div class="form-group">
            <label class="form-label">Recommended Skills (Comma separated):</label>
            <input type="text" id="req-recommended" class="form-control" value="FastAPI, AWS, Git">
          </div>
          <button type="submit" class="btn btn-primary">Submit Skill Requirement</button>
        </form>
      </div>
    `;

  } else if (state.currentTab === "feedback") {
    container.innerHTML = `
      <div class="page-header">
        <div class="page-title-group">
          <div class="section-eyebrow">GRADUATE FEEDBACK</div>
          <h1>Submit Industry Feedback</h1>
          <p>Provide direct feedback to regional university curriculum committees.</p>
        </div>
      </div>

      <div class="panel" style="max-width: 650px;">
        <form id="form-employer-feedback" onsubmit="handleEmployerFeedbackSubmit(event)">
          <div class="form-group">
            <label class="form-label">Company Name:</label>
            <input type="text" id="fb-company" class="form-control" value="Nexus Financial SaaS" required>
          </div>
          <div class="form-group">
            <label class="form-label">Which skills are difficult to find? (Comma separated):</label>
            <input type="text" id="fb-difficult" class="form-control" value="Docker, AWS, Kubernetes">
          </div>
          <div class="form-group">
            <label class="form-label">Which skills are becoming more important? (Comma separated):</label>
            <input type="text" id="fb-emerging" class="form-control" value="LLMs, FastAPI, CI/CD">
          </div>
          <div class="form-group">
            <label class="form-label">Which skills are missing in recent graduates? (Comma separated):</label>
            <input type="text" id="fb-missing" class="form-control" value="Production Dockerization, REST API Security">
          </div>
          <div class="form-group">
            <label class="form-label">Technologies universities should teach: (Comma separated):</label>
            <input type="text" id="fb-target-tech" class="form-control" value="FastAPI, Docker, AWS Cloud">
          </div>
          <div class="form-group">
            <label class="form-label">Additional Feedback Notes:</label>
            <textarea id="fb-notes" class="form-control" rows="3">Graduates have good programming theory but lack practical experience with production Docker containers and REST API authentication security standards.</textarea>
          </div>
          <button type="submit" class="btn btn-primary">Submit Feedback</button>
        </form>
      </div>
    `;
  } else if (state.currentTab === "signals") {
    loadEmployerSignalsView();
  }
}

async function handleEmployerRequirementSubmit(event) {
  event.preventDefault();
  const company = document.getElementById("req-company").value.trim();
  const role = document.getElementById("req-role").value.trim();
  const required = document.getElementById("req-required").value.split(',').map(s => s.trim()).filter(Boolean);
  const recommended = document.getElementById("req-recommended").value.split(',').map(s => s.trim()).filter(Boolean);

  try {
    await apiFetch("/employer/requirements", {
      method: "POST",
      body: JSON.stringify({ company, role, required_skills: required, recommended_skills: recommended })
    });
    alert("Skill requirement saved! Industry dataset updated.");
    switchTab("signals");
  } catch (err) {
    alert(`Failed to save requirement: ${err.message}`);
  }
}

async function handleEmployerFeedbackSubmit(event) {
  event.preventDefault();
  const company = document.getElementById("fb-company").value.trim();
  const difficult = document.getElementById("fb-difficult").value.split(',').map(s => s.trim()).filter(Boolean);
  const emerging = document.getElementById("fb-emerging").value.split(',').map(s => s.trim()).filter(Boolean);
  const missing = document.getElementById("fb-missing").value.split(',').map(s => s.trim()).filter(Boolean);
  const targetTech = document.getElementById("fb-target-tech").value.split(',').map(s => s.trim()).filter(Boolean);
  const notes = document.getElementById("fb-notes").value.trim();

  try {
    await apiFetch("/employer/feedback", {
      method: "POST",
      body: JSON.stringify({
        company,
        difficult_skills: difficult,
        emerging_skills: emerging,
        missing_skills: missing,
        target_technologies: targetTech,
        notes
      })
    });
    alert("Industry feedback submitted to university curriculum system!");
    switchTab("signals");
  } catch (err) {
    alert(`Failed to submit feedback: ${err.message}`);
  }
}

// ----------------------------------------------------------------------------
// 5. GLOBAL SEARCH
// ----------------------------------------------------------------------------
async function handleGlobalSearch(q) {
  const popup = document.getElementById("search-results-popup");
  try {
    const res = await apiFetch(`/search?q=${encodeURIComponent(q)}`);
    popup.style.display = "block";

    let html = "";
    if (res.skills && res.skills.length) {
      html += `<div class="search-category-title">Taxonomy Skills</div>`;
      res.skills.forEach(s => {
        html += `<div class="search-result-item" onclick="selectSearchResult('skill', '${s}')"><span>${s}</span><span style="color: var(--accent-terracotta)">Skill</span></div>`;
      });
    }

    if (res.roles && res.roles.length) {
      html += `<div class="search-category-title">Target Job Roles</div>`;
      res.roles.forEach(r => {
        html += `<div class="search-result-item" onclick="selectSearchResult('role', '${r}')"><span>${r}</span><span style="color: var(--accent-sage)">Role</span></div>`;
      });
    }

    if (res.jobs && res.jobs.length) {
      html += `<div class="search-category-title">Job Postings</div>`;
      res.jobs.forEach(j => {
        html += `<div class="search-result-item" onclick="selectSearchResult('job', '${j.title}')"><span>${j.title} (${j.company})</span><span style="color: var(--text-muted)">Job</span></div>`;
      });
    }

    if (!html) {
      html = `<div style="padding: 0.5rem; color: var(--text-dim); font-size: 0.8rem;">No matching results for "${q}"</div>`;
    }

    popup.innerHTML = html;
  } catch (err) {
    console.error(err);
  }
}

function selectSearchResult(type, value) {
  document.getElementById("search-results-popup").style.display = "none";
  document.getElementById("global-search-input").value = "";

  if (type === "skill" || type === "role") {
    navigateRole("student", "gaps");
  } else {
    navigateRole("university", "industry");
  }
}

// ----------------------------------------------------------------------------
// 6. MODALS & AUTHENTICATION
// ----------------------------------------------------------------------------
function openAboutModal() {
  const container = document.getElementById("modal-container");
  const body = document.getElementById("modal-body");

  body.innerHTML = `
    <button class="modal-close" onclick="closeModal()">&times;</button>
    <div style="margin-bottom: 1rem;">
      <h2>About SkillParity Platform</h2>
      <p style="font-size: 0.9rem; margin-top: 0.5rem; line-height: 1.6;">
        SkillParity is an Industry–Curriculum Intelligence Platform designed to bring higher education into exact parity with live labor market demand. It parses university syllabi using NLP/PyPDF skill extraction, generates personal student roadmaps, and collects direct employer feedback.
      </p>
    </div>
    <button class="btn btn-primary" onclick="closeModal()" style="width: 100%;">Close</button>
  `;
  container.style.display = "flex";
}

function openHowItWorksModal() {
  const container = document.getElementById("modal-container");
  const body = document.getElementById("modal-body");

  body.innerHTML = `
    <button class="modal-close" onclick="closeModal()">&times;</button>
    <div style="margin-bottom: 1rem;">
      <h2>How SkillParity Works</h2>
      <div style="margin-top: 1rem; display: flex; flex-direction: column; gap: 0.75rem; font-size: 0.88rem;">
        <div><strong>1. Live Job Postings:</strong> Analyzes regional job openings and maps skill demand percentages.</div>
        <div><strong>2. Skill Extraction Engine:</strong> Normalizes skills against a 13-category canonical taxonomy.</div>
        <div><strong>3. Curriculum &amp; Student Inputs:</strong> Extracts skills from PDF syllabi and resumes.</div>
        <div><strong>4. Gap Engine &amp; Recommendations:</strong> Evaluates missing skills and generates targeted learning modules and roadmaps.</div>
      </div>
    </div>
    <button class="btn btn-primary" onclick="closeModal()" style="width: 100%; margin-top: 1rem;">Close</button>
  `;
  container.style.display = "flex";
}

function openRoleSelectionModal() {
  const container = document.getElementById("modal-container");
  const body = document.getElementById("modal-body");

  body.innerHTML = `
    <button class="modal-close" onclick="closeModal()">&times;</button>
    <div style="margin-bottom: 1.5rem;">
      <h2>Select Workspace</h2>
      <p style="font-size: 0.88rem; margin-top: 0.25rem;">Choose an intelligence experience for your role.</p>
    </div>

    <div style="display: flex; flex-direction: column; gap: 0.75rem;">
      <button class="btn btn-secondary" onclick="navigateRole('university'); closeModal();" style="justify-content: flex-start; padding: 0.9rem;">
        🏛️ <strong>University Portal</strong> &mdash; Curriculum Gap &amp; Industry Alignment
      </button>
      <button class="btn btn-secondary" onclick="navigateRole('student'); closeModal();" style="justify-content: flex-start; padding: 0.9rem;">
        🎓 <strong>Student Portal</strong> &mdash; Personal Gap Score &amp; Career Roadmap
      </button>
      <button class="btn btn-secondary" onclick="navigateRole('employer'); closeModal();" style="justify-content: flex-start; padding: 0.9rem;">
        💼 <strong>Employer Portal</strong> &mdash; Skill Validation &amp; Industry Signals
      </button>
    </div>
  `;
  container.style.display = "flex";
}

function openLoginModal() {
  const container = document.getElementById("modal-container");
  const body = document.getElementById("modal-body");

  body.innerHTML = `
    <button class="modal-close" onclick="closeModal()">&times;</button>
    <div style="margin-bottom: 1.5rem;">
      <h2>Sign In to SkillParity</h2>
      <p style="font-size: 0.88rem; margin-top: 0.25rem;">Enter your account credentials to access your protected workspace.</p>
    </div>

    <form onsubmit="handleLoginSubmit(event)">
      <div class="form-group">
        <label class="form-label">Email Address:</label>
        <input type="email" id="login-email" class="form-control" value="university@demo.edu" required>
      </div>
      <div class="form-group">
        <label class="form-label">Password:</label>
        <input type="password" id="login-password" class="form-control" value="password123" required>
      </div>
      <button type="submit" class="btn btn-primary" style="width: 100%;">Sign In</button>
    </form>
    
    <div style="margin-top: 1rem; font-size: 0.8rem; color: var(--text-dim); text-align: center;">
      Demo credentials prefilled. Click Sign In to authenticate via JWT backend.
    </div>
  `;
  container.style.display = "flex";
}

function openRegisterModal() {
  const container = document.getElementById("modal-container");
  const body = document.getElementById("modal-body");

  body.innerHTML = `
    <button class="modal-close" onclick="closeModal()">&times;</button>
    <div style="margin-bottom: 1.5rem;">
      <h2>Create SkillParity Account</h2>
      <p style="font-size: 0.88rem; margin-top: 0.25rem;">Register a new account to persist your analytics data.</p>
    </div>

    <form onsubmit="handleRegisterSubmit(event)">
      <div class="form-group">
        <label class="form-label">Full Name:</label>
        <input type="text" id="reg-name" class="form-control" placeholder="Dr. Jane Doe" required>
      </div>
      <div class="form-group">
        <label class="form-label">Email Address:</label>
        <input type="email" id="reg-email" class="form-control" placeholder="jane.doe@university.edu" required>
      </div>
      <div class="form-group">
        <label class="form-label">Password:</label>
        <input type="password" id="reg-password" class="form-control" placeholder="Minimum 6 characters" required>
      </div>
      <div class="form-group">
        <label class="form-label">Account Role:</label>
        <select id="reg-role" class="form-control" required>
          <option value="university">University Faculty / Leader</option>
          <option value="student">Student / Job Seeker</option>
          <option value="employer">Employer / Recruiter</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Organization / University Name:</label>
        <input type="text" id="reg-org" class="form-control" placeholder="Global Tech University">
      </div>
      <button type="submit" class="btn btn-primary" style="width: 100%;">Register Account</button>
    </form>
  `;
  container.style.display = "flex";
}

function closeModal() {
  document.getElementById("modal-container").style.display = "none";
}

async function handleLoginSubmit(event) {
  event.preventDefault();
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value.trim();

  try {
    const res = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });

    state.token = res.access_token;
    state.user = res.user;
    localStorage.setItem("skillparity_jwt_token", res.access_token);
    localStorage.setItem("skillparity_user", JSON.stringify(res.user));

    closeModal();
    navigateRole(res.user.role, "overview");
  } catch (err) {
    alert(`Login failed: ${err.message}`);
  }
}

async function handleRegisterSubmit(event) {
  event.preventDefault();
  const name = document.getElementById("reg-name").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const password = document.getElementById("reg-password").value.trim();
  const role = document.getElementById("reg-role").value;
  const org = document.getElementById("reg-org").value.trim();

  try {
    const res = await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ full_name: name, email, password, role, organization: org })
    });

    state.token = res.access_token;
    state.user = res.user;
    localStorage.setItem("skillparity_jwt_token", res.access_token);
    localStorage.setItem("skillparity_user", JSON.stringify(res.user));

    closeModal();
    navigateRole(res.user.role, "overview");
  } catch (err) {
    alert(`Registration failed: ${err.message}`);
  }
}

function logoutUser() {
  state.token = null;
  state.user = null;
  localStorage.removeItem("skillparity_jwt_token");
  localStorage.removeItem("skillparity_user");
  navigateRole("landing");
}
