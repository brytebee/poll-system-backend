const slides = [
  {
    type: "title",
    title: "NexusPolls",
    subtitle: "Enterprise-Grade Online Poll System",
    tagline:
      "Built with Django Rest Framework (DRF), PostgreSQL, Redis & Docker",
    satisfies:
      "In satisfaction of the ALX ProDev Backend Program - Project Nexus",
    author: "Bright Atsighi",
  },
  {
    type: "overview",
    title: "Project Overview",
    content: [
      {
        icon: "database",
        text: "Real-time voting system with optimized data models",
      },
      {
        icon: "shield",
        text: "Secure authentication & duplicate vote prevention",
      },
      {
        icon: "zap",
        text: "Redis caching for high-performance result computation",
      },
      {
        icon: "cloud",
        text: "Production deployment on DigitalOcean with CI/CD, Domain with Ngrok",
      },
    ],
    stats: [
      { label: "API Endpoints", value: "15+" },
      { label: "Test Coverage", value: "90%+" },
      { label: "Response Time", value: "<100ms" },
    ],
  },
  {
    type: "architecture",
    title: "System Architecture",
    sections: [
      {
        title: "Backend Stack",
        items: [
          "Django Rest Framework",
          "PostgreSQL 15",
          "Redis 7 (Caching)",
          "JWT Authentication",
        ],
      },
      {
        title: "DevOps Stack",
        items: [
          "Docker & Docker Compose",
          "Nginx Reverse Proxy",
          "GitHub Actions CI/CD",
          "Domain from Ngrok",
          "DigitalOcean Hosting",
        ],
      },
      {
        title: "Key Features",
        items: [
          "RESTful API Design",
          "Swagger Documentation",
          "Health Monitoring",
          "Rate Limiting",
        ],
      },
    ],
  },
  {
    type: "database",
    title: "Database Design & Optimization",
    placeholder: "[INSERT ERD DIAGRAM HERE - Nexus Polls.drawio.svg]",
    highlights: [
      "Normalized schema (3NF) for data integrity",
      "Optimized indexes on foreign keys & query fields",
      "Efficient vote counting with database aggregations",
      "Prevents N+1 queries with select_related/prefetch_related",
    ],
  },
  {
    type: "features",
    title: "Core Features Demonstration",
    features: [
      {
        name: "Authentication System",
        description: "Create, update, delete User Accounts",
        placeholder: "[SCREENSHOT: Authentication]",
        image: "account_creation.png",
      },
      {
        name: "Poll Management",
        description: "Create, update, delete polls with multiple options",
        placeholder: "[SCREENSHOT: Poll Creation]",
        image: "poll_creation.png",
      },
      {
        name: "Voting System",
        description:
          "Secure voting with duplicate prevention (IP + User-based)",
        placeholder: "[SCREENSHOT: Voting]",
        image: "poll_result.png",
      },
      {
        name: "Real-time Results",
        description: "Live vote counting with Redis caching",
        placeholder: "[SCREENSHOT: Results]",
        image: "poll_result.png",
      },
    ],
  },
  {
    type: "code",
    title: "Code Quality & Best Practices",
    placeholder: "[INSERT CODE SNIPPET: Optimized vote counting query]",
    practices: [
      "Clean, modular code structure",
      "Comprehensive unit & integration tests",
      "Type hints and docstrings throughout",
      "PEP 8 compliance with automated linting",
    ],
  },
  {
    type: "performance",
    title: "Performance & Security",
    columns: [
      {
        title: "Performance Optimizations",
        items: [
          "Redis caching reduces DB queries by 70%",
          "Database query optimization with indexes",
          "Pagination for large datasets",
          "Response compression with Nginx",
        ],
      },
      {
        title: "Security Measures",
        items: [
          "JWT-based authentication",
          "Rate limiting (100 req/hour)",
          "Input validation & sanitization",
          "CORS & security headers configured",
        ],
      },
    ],
  },
  {
    type: "api",
    title: "API Documentation with Swagger",
    placeholder: "[SCREENSHOT: Swagger UI interface]",
    endpoints: [
      "POST /api/polls/ - Create new poll",
      "GET /api/polls/{id}/ - Retrieve poll details",
      "POST /api/votes/ - Cast a vote",
      "GET /api/polls/{id}/results/ - Get real-time results",
    ],
  },
  {
    type: "devops",
    title: "Production Deployment & CI/CD",
    pipeline: [
      {
        stage: "Code Push",
        icon: "git",
        desc: "Push/Merge to GitHub main branch",
      },
      {
        stage: "Automated Testing",
        icon: "check",
        desc: "Run test suite & security checks",
      },
      {
        stage: "Build & Deploy",
        icon: "cloud",
        desc: "Docker build & container deployment",
      },
      {
        stage: "Health Check",
        icon: "trending",
        desc: "Verify application health",
      },
    ],
    deployment: "Live on DigitalOcean with containerized architecture",
  },
  {
    type: "challenges",
    title: "Challenges & Solutions",
    items: [
      {
        challenge: "Preventing duplicate votes efficiently",
        solution:
          "Implemented composite unique constraint (user + poll) with database-level enforcement and IP tracking for anonymous users",
      },
      {
        challenge: "Real-time result computation at scale",
        solution:
          "Redis caching strategy with cache invalidation on new votes, reducing computation time from ~500ms to <50ms",
      },
      {
        challenge: "Cost-effective deployment strategy",
        solution:
          "Single-server architecture with embedded PostgreSQL, keeping costs at $6/month while maintaining performance",
      },
    ],
  },
  {
    type: "demo",
    title: "Live Application Demo",
    links: [
      { label: "Live Application", url: "https://37ae27a7e64b.ngrok-free.app" },
      {
        label: "API Documentation",
        url: "https://37ae27a7e64b.ngrok-free.app/api/docs/",
      },
      {
        label: "Health Check",
        url: "https://37ae27a7e64b.ngrok-free.app/api/health/",
      },
      {
        label: "GitHub Repository",
        url: "https://github.com/brytebee/poll-system-backend",
      },
    ],
  },
  {
    type: "takeaways",
    title: "Key Takeaways & Skills Demonstrated",
    skills: [
      "Full-stack backend development with Django & DRF",
      "Database design & optimization for real-time applications",
      "Caching strategies with Redis for performance",
      "RESTful API design with comprehensive documentation",
      "DevOps practices: Docker, CI/CD, cloud deployment",
      "Security best practices & authentication",
      "Production monitoring & health checks",
      "Problem-solving with scalable solutions",
    ],
  },
];

let currentSlide = 0;

const icons = {
  database:
    '<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"/></svg>',
  shield:
    '<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>',
  zap: '<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>',
  cloud:
    '<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"/></svg>',
  check:
    '<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
  git: '<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>',
  trending:
    '<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>',
  chevronLeft:
    '<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>',
  chevronRight:
    '<svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>',
};

function renderSlide(slide) {
  switch (slide.type) {
    case "title":
      return `
                <div class="slide slide-title">
                    <h1>${slide.title}</h1>
                    <p class="subtitle">${slide.subtitle}</p>
                    <p class="tagline">${slide.tagline}</p>
                    <p class="author">${slide.author}</p>
                </div>`;

    case "overview":
      return `
                <div class="slide slide-overview">
                    <h2>${slide.title}</h2>
                    <div class="overview-grid">
                        ${slide.content
                          .map(
                            (item) => `
                            <div class="overview-item">
                                ${icons[item.icon]}
                                <p>${item.text}</p>
                            </div>
                        `
                          )
                          .join("")}
                    </div>
                    <div class="stats-grid">
                        ${slide.stats
                          .map(
                            (stat) => `
                            <div class="stat-card">
                                <div class="value">${stat.value}</div>
                                <div class="label">${stat.label}</div>
                            </div>
                        `
                          )
                          .join("")}
                    </div>
                </div>`;

    case "architecture":
      return `
                <div class="slide slide-architecture">
                    <h2>${slide.title}</h2>
                    <div class="arch-grid">
                        ${slide.sections
                          .map(
                            (section) => `
                            <div class="arch-section">
                                <h3>${section.title}</h3>
                                <ul>
                                    ${section.items
                                      .map((item) => `<li>${item}</li>`)
                                      .join("")}
                                </ul>
                            </div>
                        `
                          )
                          .join("")}
                    </div>
                </div>`;

    case "database":
      return `
            <div class="slide slide-database">
                <h2>${slide.title}</h2>
                <div class="diagram-placeholder">
                    <img src="/static/images/presentation/erd_diagram.svg" 
                        alt="ERD Diagram" 
                        style="max-width: 100%; max-height: 42rem; object-fit: contain;">
                </div>
            </div>
        `;
    case "features":
      return `
                <div class="slide slide-features">
                    <h2>${slide.title}</h2>
                    <div class="features-grid">
                        ${slide.features
                          .map(
                            (f) => `
                            <div class="feature-card">
                                <div class="feature-header">
                                    <img src="/static/images/presentation/${f.image}" 
                                        style="width: 100%; height: 100%; object-fit: cover;">
                                </div>
                                <div class="feature-body">
                                    <h3>${f.name}</h3>
                                    <p>${f.description}</p>
                                </div>
                            </div>
                        `
                          )
                          .join("")}
                    </div>
                </div>`;

    case "code":
      return `
                <div class="slide slide-code">
                    <h2>${slide.title}</h2>
                    <div class="diagram-placeholder">
                        <img src="/static/images/presentation/clean_code.png" 
                            alt="ERD Diagram" 
                            style="max-width: 100%; max-height: 16rem; object-fit: contain;">
                    </div>
                    <div class="practices-grid">
                        ${slide.practices
                          .map(
                            (p) => `
                            <div class="practice-item">
                                ${icons.check}
                                <p>${p}</p>
                            </div>
                        `
                          )
                          .join("")}
                    </div>
                </div>`;

    case "performance":
      return `
                <div class="slide slide-performance">
                    <h2>${slide.title}</h2>
                    <div class="perf-grid">
                        ${slide.columns
                          .map(
                            (col) => `
                            <div class="perf-column">
                                <h3>${col.title}</h3>
                                <ul>
                                    ${col.items
                                      .map(
                                        (item) => `
                                        <li>${icons.check}<span>${item}</span></li>
                                    `
                                      )
                                      .join("")}
                                </ul>
                            </div>
                        `
                          )
                          .join("")}
                    </div>
                </div>`;

    case "api":
      return `
                <div class="slide slide-api">
                    <h2>${slide.title}</h2>
                    <div class="api-placeholder">
                        <img src="/static/images/presentation/swagger_docs.png" 
                            alt="ERD Diagram" 
                            style="max-width: 100%; max-height: 16rem; object-fit: contain;">
                    </div>
                    <div class="api-endpoints">
                        <h3>Key API Endpoints</h3>
                        ${slide.endpoints
                          .map((e) => `<div class="endpoint">${e}</div>`)
                          .join("")}
                    </div>
                </div>`;

    case "devops":
      return `
                <div class="slide slide-devops">
                    <h2>${slide.title}</h2>
                    <div class="pipeline-grid">
                        ${slide.pipeline
                          .map(
                            (step) => `
                            <div class="pipeline-step">
                                ${icons[step.icon]}
                                <h3>${step.stage}</h3>
                                <p>${step.desc}</p>
                            </div>
                        `
                          )
                          .join("")}
                    </div>
                    <div class="deployment-info">
                        <p>${slide.deployment}</p>
                    </div>
                </div>`;

    case "challenges":
      return `
                <div class="slide slide-challenges">
                    <h2>${slide.title}</h2>
                    ${slide.items
                      .map(
                        (item) => `
                        <div class="challenge-item">
                            <h3>Challenge: ${item.challenge}</h3>
                            <p><span class="solution-label">Solution:</span> ${item.solution}</p>
                        </div>
                    `
                      )
                      .join("")}
                </div>`;

    case "demo":
      return `
                <div class="slide slide-demo">
                    <h2>${slide.title}</h2>
                    <div class="demo-grid">
                        <div class="demo-qr">
                            <p>[QR Code Placeholder]</p>
                        </div>
                        <div class="demo-links">
                            <h3>Access Links</h3>
                            ${slide.links
                              .map(
                                (link) => `
                                <div class="demo-link">
                                    <p>${link.label}</p>
                                    <p>${link.url}</p>
                                </div>
                            `
                              )
                              .join("")}
                        </div>
                    </div>
                </div>`;

    case "takeaways":
      return `
                <div class="slide slide-takeaways">
                    <h2>${slide.title}</h2>
                    <div class="takeaways-grid">
                        ${slide.skills
                          .map(
                            (skill) => `
                            <div class="takeaway-item">
                                ${icons.trending}
                                <p>${skill}</p>
                            </div>
                        `
                          )
                          .join("")}
                    </div>
                </div>`;

    default:
      return '<div class="slide"><p>Slide type not found</p></div>';
  }
}

function updateSlide() {
  const container = document.querySelector(".slide-container");
  container.innerHTML = renderSlide(slides[currentSlide]);

  document.getElementById("slide-number").textContent = `Slide ${
    currentSlide + 1
  } of ${slides.length}`;

  document.getElementById("prev-btn").disabled = currentSlide === 0;
  document.getElementById("next-btn").disabled =
    currentSlide === slides.length - 1;

  const indicators = document.querySelectorAll(".indicator");
  indicators.forEach((ind, idx) => {
    ind.classList.toggle("active", idx === currentSlide);
  });
}

function nextSlide() {
  if (currentSlide < slides.length - 1) {
    currentSlide++;
    updateSlide();
  }
}

function prevSlide() {
  if (currentSlide > 0) {
    currentSlide--;
    updateSlide();
  }
}

function init() {
  const root = document.getElementById("presentation-root");

  root.innerHTML = `
        <div class="slide-container"></div>
        <div class="nav-bar">
            <button id="prev-btn" class="nav-btn" onclick="prevSlide()">
                ${icons.chevronLeft}
                <span>Previous</span>
            </button>
            <div class="nav-info">
                <span id="slide-number">Slide 1 of ${slides.length}</span>
                <div class="slide-indicators">
                    ${slides
                      .map(
                        (_, idx) =>
                          `<div class="indicator ${
                            idx === 0 ? "active" : ""
                          }"></div>`
                      )
                      .join("")}
                </div>
            </div>
            <button id="next-btn" class="nav-btn" onclick="nextSlide()">
                <span>Next</span>
                ${icons.chevronRight}
            </button>
        </div>
    `;

  updateSlide();

  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") nextSlide();
    if (e.key === "ArrowLeft") prevSlide();
  });
}

document.addEventListener("DOMContentLoaded", init);
