# Event Horizon

A web-based probability toolkit that converts an observed event probability within a time window into actionable metrics.

**Two analyses from one input:**
1. **Poisson Frequency** — How many times per year does this event happen?
2. **Survival Analysis (Half-Life)** — How long until there's a 50% chance the event occurs? What's the mean time between events?

**How it works:** You provide a time range, and a probability (e.g., 30%). The tool computes annualized frequency, half-life, mean time between events, and survival probabilities at various horizons.

**Stack:** FastAPI backend with REST API, plain HTML/CSS/JS frontend (Flatpickr for datetime). Token-based auth.
