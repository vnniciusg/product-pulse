# Product Pulse AI

**Product Pulse AI** Its an AI-powered product research assistant for the Amazon marketplace. Utilizing advanced AI agents, the system helps users navigate the vast world of products, offering honest, analytical, and visually rich recommendations.


![Demo](assets/demo.gif)

> This demo shows the Product Pulse AI in action, helping users navigate the vast world of products and offering honest, analytical, and visually rich recommendations.
--- 

## Features

- **Strategic Research**: Executes precise searches on Amazon using optimized keyword combinations.
- **Specialized Analysis**: Breaks down product data (reviews, ratings, specifications) into actionable insights.
- **Visual Showcases**: Delivers detailed and visually appealing presentations of recommended products.
- **Precise Comparison**: Compares similar products through detailed Markdown tables.
- **Chatbot Inteligente**: Interface de chat com streaming em tempo real para uma experiência interativa.

---

## Tech Stack

### Backend
- **Python 3.12+**
- **FastAPI**: Web framework moderno and high performance.
- **LangChain & LangGraph**: AI agent orchestration and stateful flows.
- **Pydantic**: Data validation and configuration.
- **Loguru**: Logging management.
- **ScraperAPI**: The API used for scraping Amazon products.
- **uv**: Python package manager and environment manager ultra-rápido.

### Frontend
- **Next.js 15 (App Router)**
- **React 19**
- **Tailwind CSS 4**: Modern and responsive styling.
- **Framer Motion**: Smooth and premium animations.
- **Radix UI**: Accessible and customizable components.
- **Bun**: Runtime and JavaScript package manager.

---

## Architecture

The project is divided into a monorepo structure:

- `/src`: Contains the core backend, including the agent logic (`/agent`), API services (`/api`), and general configurations.
- `/frontend`: Complete Next.js application with modern UI components and integration with the streaming API.

---

## Setup

### Prerequisites
- [uv](https://github.com/astral-sh/uv) installed.
- [Bun](https://bun.sh/) installed.
- OpenAI API key (or provider configured in LangChain).
- ScraperAPI API key.

### Backend
1. Navigate to the root of the project.
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Configure the `.env` file based on the `.env.example`.
4. Start the server:
   ```bash
   make run
   ```

### Frontend
1. Navigate to the `/frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   bun install
   ```
3. Create a `.env` file with the following variables:
   ```bash
   AGENT_API_URL="http://127.0.0.1:8000/api/v1/agent/stream"
   AGENT_API_KEY=   
   ```
   
4. Start the development server:
   ```bash
   bun dev
   ```

---

## License

This project is licensed under the [MIT](LICENSE).