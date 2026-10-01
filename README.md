# Hardik Portfolio

Portfolio of Hardik Goel, Data & AI Architecture Leader: enterprise GenAI, agentic systems, MLOps governance, open-source AI tooling, and AI-augmented engineering workflows.

Built as a modern interactive portfolio experience highlighting:

* Enterprise AI/Data architecture
* GenAI & Agentic AI systems
* Open-source AI projects
* MLOps governance platforms
* Technical leadership
* AI education & thought leadership

---

## Live Portfolio

🌐 Portfolio Website
[Hardik Goel Portfolio](https://hardik-portfolio-rho.vercel.app/)

💼 LinkedIn
[Hardik Goel LinkedIn](https://www.linkedin.com/in/hardikgoelai/)

🐙 GitHub
[Hardik Goel GitHub](https://github.com/hardik-goel)

---

# Highlights

* Interactive AI/Data Architect portfolio
* AI-powered “Chat with Hardik” assistant
* Enterprise-scale experience timeline
* Open-source AI project showcase
* GenAI + MLOps + Agentic AI positioning
* Modern responsive UI with premium visual design
* Optimized for recruiter storytelling and technical branding

---

# Featured Work

## Switchboard

Provider-agnostic AI model routing and orchestration framework focused on:

* dynamic model routing
* fallback strategies
* cost-aware orchestration
* latency-aware execution
* enterprise AI integration

## AudioSummariser

GenAI-powered audio intelligence framework featuring:

* transcription
* embeddings
* chunking
* summarization
* conversational RAG retrieval
* PyPI distribution

## CommodityBuddy

Enterprise GenAI assistant for commodity forecasting and procurement intelligence using:

* embeddings
* conversational retrieval
* forecasting workflows
* stakeholder analytics

## CompliSense AI

AI governance and compliance platform for regulated industries:

* agentic compliance monitoring
* alerting and remediation
* EU AI Act and India's DPDP Act coverage
* finance, retail and healthcare

[complisenseai.com](https://complisenseai.com/)

---

# Tech Stack

## Frontend

* HTML5
* CSS3
* Vanilla JavaScript

## AI / GenAI

* Claude
* GPT
* Gemini
* RAG
* MCP
* Vector Databases
* Agentic AI

## Data & MLOps

* Azure ML
* MLflow
* SHAP
* PSI Drift Monitoring
* Spark
* Kafka
* Airflow
* DBT
* Databricks

## Cloud

* AWS
* Azure
* Vercel

---

# Design Philosophy

This portfolio was intentionally designed to bridge:

Enterprise Engineering and Modern GenAI Systems

The goal was not to create a generic developer portfolio, but a platform reflecting:

* architecture thinking
* systems design maturity
* AI-native engineering
* technical storytelling
* open-source builder mindset

---

# Local Development

Clone the repository:

```bash
git clone https://github.com/hardik-goel/hardik-portfolio.git
```

Open locally:

```bash
cd hardik-portfolio
```

Run using any static server:

```bash
python -m http.server 8000
```

or use VSCode Live Server.

---

# Deployment

Recommended deployment:

* GitHub Pages
* Vercel

Deploy instantly on Vercel:

[Vercel](https://vercel.com)

---

# Future Enhancements

Planned roadmap:

* Next.js migration
* Backend-powered AI chat
* RAG-powered recruiter assistant
* Architecture visualizations
* Dynamic markdown-driven content
* Blog integration
* AI project demos
* Analytics dashboard

---

# Blog build (SEO canonical pages)

Per-post static pages live under `/blog`. They make this domain the canonical
source of truth for each essay (own `<head>`, canonical=self, Open Graph,
`BlogPosting` JSON-LD) while still linking out to Substack and Medium.

Regenerate after publishing a new post (pulls both RSS feeds, dedupes
cross-posts, rewrites `blog/*.html` + `sitemap.xml`):

```bash
python3 build_blog.py
```

No dependencies, Python stdlib only. Thin/placeholder posts are skipped.

# Resume

`/resume` redirects to the PDF at `resources/Hardik_Goel_Resume.pdf` (see `vercel.json`).
A web version of the same content is kept at `resume/index.html`.

# Self-hosted fonts (perf)

Fonts and icons are vendored under `resources/fonts/` so the page makes zero
external CDN calls (Google Fonts + jsdelivr removed). Inter/JetBrains Mono use
the latin woff2 subsets; the Tabler icon webfont is subset from 829KB down to
only the ~30 icons the page uses (~7KB).

Rerun only if you add a new icon or font weight (needs `fonttools`):

```bash
pip install fonttools brotli
python3 build_fonts.py
```

---

# Author

Hardik Goel
Data & AI Architecture Leader
Enterprise GenAI · Agentic Systems · MLOps Governance · Bengaluru, India

---

# License

MIT License
