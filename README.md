# AccuKnox User Management Automation Framework

A robust, enterprise-grade end-to-end (E2E) testing framework engineered with **Playwright** and **TypeScript**. This repository implements the **Page Object Model (POM)** architectural design pattern to automate and validate the complete user management lifecycle within the OrangeHRM platform.

---

## 🚀 Key Features

* **Page Object Model (POM):** Clean separation of UI element locators and structural interaction workflows from the core test assertions.
* **Race-Condition Mitigation:** Advanced synchronization handlers and calculated buffer strategies designed to bypass flaky, API-driven autocomplete elements securely.
* **Strict Mode Violation Protection:** Refined locator queries utilizing element filtering layers to maintain seamless test executions against duplicate runtime elements.
* **Comprehensive Test Coverage:** Single, cohesive script execution mapping out user creation, search filtering, dynamic role upgrading, profile removal, and empty-state verification.
* **CI/CD Pipeline Ready:** Fully integrated setup ready to run tests seamlessly in cloud environments via headless container configurations.

---

## 📁 Repository Directory Architecture

AccuKnox-user-management-tests/
├── .github/
│   └── workflows/
│       └── playwright.yml         # CI/CD Automated Test Runner Config
├── pages/
│   ├── LoginPage.ts               # Authentication Locators & Actions
│   └── AdminPage.ts               # User Modification & Management Core Logic
├── tests/
│   └── userManagement.spec.ts     # Main E2E Lifecycle Specification Suite
├── playwright-report/             # Auto-generated HTML execution logs
├── playwright.config.ts           # Core Framework Execution Engine Settings
├── package.json                   # Dependency Mapping & Script Shortcuts
└── README.md                      # Framework Documentation

---

💻 Technical Setup & Getting Started

Prerequisites

Before initializing the framework, verify that you have Node.js (LTS version) installed locally on your operating machine.

Installation Steps
Navigate to the project workspace directory:

Bash
cd AccuKnox-user-management-tests
Install core project dependencies mapped inside the file layout:

Bash
npm install
Download required native Playwright browser binaries along with their OS-level dependencies:

Bash
npx playwright install --with-deps
🛠️ Executing the Automation Suite
You can execute the test suite across different configurations depending on your debugging requirements:

1. Headed Mode (Visual Verification)
To watch the automated tests physically open the browser engine and click through the application components in real-time, execute:

Bash
npx playwright test --headed
2. Headless Mode (Standard Background CLI Run)
To trigger high-velocity test execution inside the background (ideal for continuous integration flows and pipeline jobs):

Bash
npx playwright test
3. Reviewing Interactive Diagnostic Reports
Playwright saves granular execution logs following every run. To open the interactive HTML data dashboard and drill down into the timeline metrics:

Bash
npx playwright show-report
🌐 Continuous Integration (CI/CD)
The project includes an operational GitHub Actions workflow setup inside .github/workflows/playwright.yml.

Every time you execute a git push or run a pull request to the main or master branches, GitHub will spin up a secure Ubuntu instance, install dependencies, run the complete suite headlessly, and automatically upload the interactive HTML execution reports straight to your repository artifacts storage dashboard.