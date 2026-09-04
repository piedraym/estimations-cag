ESTIMATION_EXAMPLES: list[dict] = [
    {
        "meeting_summary": (
            "The client needs an inventory management web platform for a mid-size warehouse "
            "operation. They want real-time stock tracking, automated reorder alerts when items "
            "fall below a configurable threshold, a role-based access system (admin, warehouse "
            "manager, viewer), CSV/Excel import and export of inventory data, and a dashboard "
            "with key metrics (turnover rate, stock value, low-stock items). They already have "
            "a PostgreSQL database running in AWS that we should integrate with. No mobile app "
            "is needed — the warehouse team will use tablets with the web interface."
        ),
        "estimation": {
            "title": "Inventory Management Web Platform",
            "phases": [
                {"name": "Discovery & design", "hours": 24, "cost_eur": 1500, "confidence_pct": 85},
                {"name": "Backend & data model", "hours": 56, "cost_eur": 3500, "confidence_pct": 75},
                {"name": "Core features (alerts, import/export, dashboard)", "hours": 64, "cost_eur": 4000, "confidence_pct": 70},
                {"name": "Frontend", "hours": 36, "cost_eur": 2250, "confidence_pct": 75},
                {"name": "Testing & deployment", "hours": 20, "cost_eur": 1250, "confidence_pct": 80},
            ],
            "total_hours": 200,
            "total_cost_eur": 12500,
            "team": [
                "1 Senior Backend Developer (lead)",
                "1 Mid-level Full-Stack Developer",
                "1 QA Engineer (part-time, last 3 weeks)",
            ],
            "duration_weeks": 10,
            "narrative": None,
        },
    },
    {
        "meeting_summary": (
            "A real estate agency wants a high-conversion landing page to capture leads for "
            "luxury property listings. The page should feature a hero section with a video "
            "background, a curated property gallery with filtering by price range and location, "
            "a lead capture form, and client testimonials. All leads must be pushed in real-time "
            "to their existing HubSpot CRM via the API. The design must be responsive, "
            "mobile-first, and follow their brand guidelines (they will provide a Figma file). "
            "They also want basic analytics integration with Google Tag Manager and Meta Pixel "
            "for ad campaign tracking."
        ),
        "estimation": {
            "title": "Real Estate Landing Page with CRM Integration",
            "phases": [
                {"name": "Discovery & design", "hours": 24, "cost_eur": 1300, "confidence_pct": 85},
                {"name": "Implementation (gallery, form, CRM integration)", "hours": 44, "cost_eur": 2750, "confidence_pct": 70},
                {"name": "Analytics & integrations", "hours": 12, "cost_eur": 750, "confidence_pct": 75},
                {"name": "Testing & launch", "hours": 24, "cost_eur": 1500, "confidence_pct": 80},
            ],
            "total_hours": 104,
            "total_cost_eur": 6300,
            "team": [
                "1 Senior Frontend Developer",
                "1 UI/UX Designer (part-time, first 2 weeks)",
            ],
            "duration_weeks": 5,
            "narrative": None,
        },
    },
    {
        "meeting_summary": (
            "A B2B startup is building a SaaS platform to manage software subscriptions for "
            "SMEs. Core features include: user registration and company onboarding, a dashboard "
            "showing all active subscriptions with renewal dates and monthly spend, the ability "
            "to add/edit/cancel subscriptions, integration with Stripe for payment processing "
            "and invoice generation, a notification system (email alerts 30/7/1 days before "
            "renewal), and an admin panel to manage customer accounts. They want a REST API "
            "with a React frontend. MVP scope — they plan to iterate after launch."
        ),
        "estimation": {
            "title": "SaaS Subscription Management Platform (MVP)",
            "phases": [
                {"name": "Discovery & architecture", "hours": 24, "cost_eur": 1500, "confidence_pct": 85},
                {"name": "Backend & Stripe integration", "hours": 96, "cost_eur": 6000, "confidence_pct": 65},
                {"name": "Frontend (React)", "hours": 60, "cost_eur": 3750, "confidence_pct": 75},
                {"name": "Testing & security", "hours": 40, "cost_eur": 2500, "confidence_pct": 70},
                {"name": "Deployment & docs", "hours": 24, "cost_eur": 1500, "confidence_pct": 80},
            ],
            "total_hours": 244,
            "total_cost_eur": 15250,
            "team": [
                "1 Senior Full-Stack Developer (lead)",
                "1 Mid-level Backend Developer",
                "1 Mid-level Frontend Developer",
                "1 QA Engineer (part-time, last 4 weeks)",
            ],
            "duration_weeks": 12,
            "narrative": None,
        },
    },
]
