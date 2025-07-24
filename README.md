eir-project/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # Point d’entrée FastAPI
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── crud/                # Fonctions DB (CRUD)
│   │   ├── api/                 # Routes API
│   │   ├── auth/                # JWT, OAuth2
│   │   ├── core/                # Config, sécurité, settings
│   │   └── utils/               # Fonctions utilitaires
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                    # Optionnel si Jinja2/HTMX
│   ├── templates/
│   ├── static/
│   └── main.py ou index.html
│
├── docker-compose.yml
├── .env
├── README.md
└── docs/
    └── cahier_de_charges.pdf
