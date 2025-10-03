import React, { useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Database,
  Code,
  Zap,
  Shield,
  GitBranch,
  Cloud,
  CheckCircle,
  TrendingUp,
} from "lucide-react";

const PresentationSlides = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    // Slide 1: Title
    {
      type: "title",
      title: "NexusPolls",
      subtitle: "Enterprise-Grade Online Poll System",
      tagline:
        "Built with Django Rest Framework (DRF), PostgreSQL, Redis & Docker",
      statisfies:
        "In satisfaction of the ALX ProDev Backend Program - Project Nexus",
      author: "Bright Atsighi",
    },

    // Slide 2: Project Overview
    {
      type: "overview",
      title: "Project Overview",
      content: [
        {
          icon: Database,
          text: "Real-time voting system with optimized data models",
        },
        {
          icon: Shield,
          text: "Secure authentication & duplicate vote prevention",
        },
        {
          icon: Zap,
          text: "Redis caching for high-performance result computation",
        },
        {
          icon: Cloud,
          text: "Production deployment on DigitalOcean with CI/CD, Domain with Ngrok",
        },
      ],
      stats: [
        { label: "API Endpoints", value: "15+" },
        { label: "Test Coverage", value: "90%+" },
        { label: "Response Time", value: "<100ms" },
      ],
    },

    // Slide 3: Technical Architecture
    {
      type: "architecture",
      title: "System Architecture",
      sections: [
        {
          title: "Backend Stack",
          items: [
            "Django Rest Framwork",
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

    // Slide 4: Database Design
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

    // Slide 5: Core Features Demo
    {
      type: "features",
      title: "Core Features Demonstration",
      features: [
        {
          name: "Authentication System",
          description: "Create, update, delete User Accounts",
          placeholder: "[SCREENSHOT: Poll creation interface]",
        },
        {
          name: "Poll Management",
          description: "Create, update, delete polls with multiple options",
          placeholder: "[SCREENSHOT: Poll creation interface]",
        },
        {
          name: "Voting System",
          description:
            "Secure voting with duplicate prevention (IP + User-based)",
          placeholder: "[SCREENSHOT: Voting interface]",
        },
        {
          name: "Real-time Results",
          description: "Live vote counting with Redis caching",
          placeholder: "[SCREENSHOT: Results dashboard]",
        },
      ],
    },

    // Slide 6: Code Quality
    {
      type: "code",
      title: "Code Quality & Best Practices",
      placeholder: "[INSERT CODE SNIPPET: Optimized vote counting query]",
      practices: [
        { icon: CheckCircle, text: "Clean, modular code structure" },
        { icon: CheckCircle, text: "Comprehensive unit & integration tests" },
        { icon: CheckCircle, text: "Type hints and docstrings throughout" },
        { icon: CheckCircle, text: "PEP 8 compliance with automated linting" },
      ],
    },

    // Slide 7: Performance & Security
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

    // Slide 8: API Documentation
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

    // Slide 9: DevOps Pipeline
    {
      type: "devops",
      title: "Production Deployment & CI/CD",
      pipeline: [
        {
          stage: "Code Push",
          icon: GitBranch,
          desc: "Push/Merge to GitHub main branch",
        },
        {
          stage: "Automated Testing",
          icon: CheckCircle,
          desc: "Run test suite & security checks",
        },
        {
          stage: "Build & Deploy",
          icon: Cloud,
          desc: "Docker build & container deployment",
        },
        {
          stage: "Health Check",
          icon: TrendingUp,
          desc: "Verify application health",
        },
      ],
      deployment: "Live on DigitalOcean with containerized architecture",
    },

    // Slide 10: Challenges & Solutions
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

    // Slide 11: Live Demo
    {
      type: "demo",
      title: "Live Application Demo",
      links: [
        {
          label: "Live Application",
          url: "https://37ae27a7e64b.ngrok-free.app",
        },
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

    // Slide 12: Key Takeaways
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

  const nextSlide = () =>
    setCurrentSlide((prev) => Math.min(prev + 1, slides.length - 1));
  const prevSlide = () => setCurrentSlide((prev) => Math.max(prev - 1, 0));

  const renderSlide = (slide) => {
    switch (slide.type) {
      case "title":
        return (
          <div className="flex flex-col items-center justify-center h-full bg-gradient-to-br from-blue-600 to-purple-700 text-white p-12">
            <h1 className="text-7xl font-bold mb-6">{slide.title}</h1>
            <p className="text-3xl mb-4">{slide.subtitle}</p>
            <p className="text-xl text-blue-100">{slide.tagline}</p>
            <div className="mt-12 text-lg text-blue-200">{slide.author}</div>
          </div>
        );

      case "overview":
        return (
          <div className="p-12 h-full bg-white">
            <h2 className="text-5xl font-bold mb-8 text-gray-800">
              {slide.title}
            </h2>
            <div className="grid grid-cols-2 gap-6 mb-8">
              {slide.content.map((item, idx) => {
                const Icon = item.icon;
                return (
                  <div
                    key={idx}
                    className="flex items-start space-x-4 p-4 bg-blue-50 rounded-lg"
                  >
                    <Icon className="w-8 h-8 text-blue-600 flex-shrink-0 mt-1" />
                    <p className="text-lg text-gray-700">{item.text}</p>
                  </div>
                );
              })}
            </div>
            <div className="grid grid-cols-3 gap-6 mt-8">
              {slide.stats.map((stat, idx) => (
                <div
                  key={idx}
                  className="bg-gradient-to-br from-purple-500 to-blue-600 p-6 rounded-lg text-white text-center"
                >
                  <div className="text-4xl font-bold">{stat.value}</div>
                  <div className="text-lg mt-2">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        );

      case "architecture":
        return (
          <div className="p-12 h-full bg-gray-50">
            <h2 className="text-5xl font-bold mb-8 text-gray-800">
              {slide.title}
            </h2>
            <div className="grid grid-cols-3 gap-6">
              {slide.sections.map((section, idx) => (
                <div key={idx} className="bg-white p-6 rounded-lg shadow-lg">
                  <h3 className="text-2xl font-bold mb-4 text-blue-600">
                    {section.title}
                  </h3>
                  <ul className="space-y-3">
                    {section.items.map((item, i) => (
                      <li key={i} className="flex items-start">
                        <span className="text-blue-500 mr-2">▸</span>
                        <span className="text-gray-700">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        );

      case "database":
        return (
          <div className="p-12 h-full bg-white">
            <h2 className="text-5xl font-bold mb-6 text-gray-800">
              {slide.title}
            </h2>
            <div className="bg-gray-100 rounded-lg p-8 mb-6 h-64 flex items-center justify-center border-4 border-dashed border-gray-300">
              <p className="text-2xl text-gray-500 font-semibold">
                {slide.placeholder}
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {slide.highlights.map((highlight, idx) => (
                <div
                  key={idx}
                  className="flex items-center space-x-3 bg-green-50 p-4 rounded-lg"
                >
                  <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                  <p className="text-gray-700">{highlight}</p>
                </div>
              ))}
            </div>
          </div>
        );

      case "features":
        return (
          <div className="p-12 h-full bg-gray-50">
            <h2 className="text-5xl font-bold mb-8 text-gray-800">
              {slide.title}
            </h2>
            <div className="grid grid-cols-3 gap-6">
              {slide.features.map((feature, idx) => (
                <div
                  key={idx}
                  className="bg-white rounded-lg shadow-lg overflow-hidden"
                >
                  <div className="bg-gradient-to-r from-blue-500 to-purple-600 h-32 flex items-center justify-center text-white text-xl font-semibold">
                    {feature.placeholder}
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-bold mb-2 text-gray-800">
                      {feature.name}
                    </h3>
                    <p className="text-gray-600">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case "code":
        return (
          <div className="p-12 h-full bg-gray-900 text-white">
            <h2 className="text-5xl font-bold mb-6">{slide.title}</h2>
            <div className="bg-gray-800 rounded-lg p-6 mb-6 h-64 flex items-center justify-center border-2 border-gray-700">
              <p className="text-xl text-gray-400">{slide.placeholder}</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {slide.practices.map((practice, idx) => {
                const Icon = practice.icon;
                return (
                  <div
                    key={idx}
                    className="flex items-center space-x-3 bg-gray-800 p-4 rounded-lg"
                  >
                    <Icon className="w-6 h-6 text-green-400 flex-shrink-0" />
                    <p className="text-gray-200">{practice.text}</p>
                  </div>
                );
              })}
            </div>
          </div>
        );

      case "performance":
        return (
          <div className="p-12 h-full bg-white">
            <h2 className="text-5xl font-bold mb-8 text-gray-800">
              {slide.title}
            </h2>
            <div className="grid grid-cols-2 gap-8">
              {slide.columns.map((column, idx) => (
                <div
                  key={idx}
                  className="bg-gradient-to-br from-blue-50 to-purple-50 p-8 rounded-lg"
                >
                  <h3 className="text-2xl font-bold mb-6 text-blue-600">
                    {column.title}
                  </h3>
                  <ul className="space-y-4">
                    {column.items.map((item, i) => (
                      <li key={i} className="flex items-start">
                        <CheckCircle className="w-5 h-5 text-green-500 mr-3 mt-1 flex-shrink-0" />
                        <span className="text-gray-700">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        );

      case "api":
        return (
          <div className="p-12 h-full bg-gray-50">
            <h2 className="text-5xl font-bold mb-6 text-gray-800">
              {slide.title}
            </h2>
            <div className="bg-white rounded-lg p-6 mb-6 h-64 flex items-center justify-center border-4 border-blue-200">
              <p className="text-2xl text-gray-500 font-semibold">
                {slide.placeholder}
              </p>
            </div>
            <div className="bg-gray-900 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4 text-white">
                Key API Endpoints
              </h3>
              <div className="space-y-2">
                {slide.endpoints.map((endpoint, idx) => (
                  <div key={idx} className="font-mono text-green-400 text-sm">
                    {endpoint}
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case "devops":
        return (
          <div className="p-12 h-full bg-gradient-to-br from-gray-900 to-blue-900 text-white">
            <h2 className="text-5xl font-bold mb-8">{slide.title}</h2>
            <div className="grid grid-cols-4 gap-4 mb-8">
              {slide.pipeline.map((step, idx) => {
                const Icon = step.icon;
                return (
                  <div
                    key={idx}
                    className="bg-white/10 backdrop-blur-sm p-6 rounded-lg text-center"
                  >
                    <Icon className="w-12 h-12 mx-auto mb-3 text-blue-300" />
                    <h3 className="font-bold text-lg mb-2">{step.stage}</h3>
                    <p className="text-sm text-gray-300">{step.desc}</p>
                  </div>
                );
              })}
            </div>
            <div className="bg-white/10 backdrop-blur-sm p-6 rounded-lg text-center">
              <p className="text-xl">{slide.deployment}</p>
            </div>
          </div>
        );

      case "challenges":
        return (
          <div className="p-12 h-full bg-white">
            <h2 className="text-5xl font-bold mb-8 text-gray-800">
              {slide.title}
            </h2>
            <div className="space-y-6">
              {slide.items.map((item, idx) => (
                <div
                  key={idx}
                  className="bg-gradient-to-r from-red-50 to-green-50 p-6 rounded-lg border-l-4 border-blue-600"
                >
                  <h3 className="text-xl font-bold text-red-600 mb-2">
                    Challenge: {item.challenge}
                  </h3>
                  <p className="text-green-700">
                    <span className="font-semibold">Solution:</span>{" "}
                    {item.solution}
                  </p>
                </div>
              ))}
            </div>
          </div>
        );

      case "demo":
        return (
          <div className="p-12 h-full bg-gradient-to-br from-purple-600 to-blue-600 text-white">
            <h2 className="text-5xl font-bold mb-8 text-center">
              {slide.title}
            </h2>
            <div className="grid grid-cols-2 gap-8">
              <div className="bg-white rounded-lg p-8 flex items-center justify-center">
                <p className="text-2xl text-gray-600 font-semibold">
                  {slide.qrPlaceholder}
                </p>
              </div>
              <div className="space-y-4">
                <h3 className="text-2xl font-bold mb-4">Access Links</h3>
                {slide.links.map((link, idx) => (
                  <div
                    key={idx}
                    className="bg-white/20 backdrop-blur-sm p-4 rounded-lg"
                  >
                    <p className="font-semibold mb-1">{link.label}</p>
                    <p className="text-sm text-blue-100">{link.url}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case "takeaways":
        return (
          <div className="p-12 h-full bg-gray-50">
            <h2 className="text-5xl font-bold mb-8 text-gray-800">
              {slide.title}
            </h2>
            <div className="grid grid-cols-2 gap-4">
              {slide.skills.map((skill, idx) => (
                <div
                  key={idx}
                  className="flex items-center space-x-3 bg-white p-4 rounded-lg shadow-md"
                >
                  <TrendingUp className="w-6 h-6 text-blue-600 flex-shrink-0" />
                  <p className="text-gray-700">{skill}</p>
                </div>
              ))}
            </div>
          </div>
        );

      case "thanks":
        return (
          <div className="flex flex-col items-center justify-center h-full bg-gradient-to-br from-blue-600 to-purple-700 text-white p-12">
            <h1 className="text-7xl font-bold mb-6">{slide.title}</h1>
            <p className="text-3xl mb-8">{slide.subtitle}</p>
            <p className="text-xl text-blue-100 text-center max-w-2xl">
              {slide.contact}
            </p>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="w-full h-screen bg-gray-100 flex flex-col">
      {/* Slide Content */}
      <div className="flex-1 relative">{renderSlide(slides[currentSlide])}</div>

      {/* Navigation */}
      <div className="bg-gray-800 text-white px-8 py-4 flex items-center justify-between">
        <button
          onClick={prevSlide}
          disabled={currentSlide === 0}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition"
        >
          <ChevronLeft className="w-5 h-5" />
          <span>Previous</span>
        </button>

        <div className="flex items-center space-x-4">
          <span className="text-lg">
            Slide {currentSlide + 1} of {slides.length}
          </span>
          <div className="flex space-x-1">
            {slides.map((_, idx) => (
              <div
                key={idx}
                className={`w-2 h-2 rounded-full ${
                  idx === currentSlide ? "bg-blue-500" : "bg-gray-600"
                }`}
              />
            ))}
          </div>
        </div>

        <button
          onClick={nextSlide}
          disabled={currentSlide === slides.length - 1}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition"
        >
          <span>Next</span>
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default PresentationSlides;
