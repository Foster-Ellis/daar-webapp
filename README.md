# DAAR Project 3 - Document Search Web App

This repository contains the frontend and backend code for the document search app project for DAAR.

The project report is found in REPORT.pdf. The project repository is found at https://github.com/Foster-Ellis/daar-webapp.

## Usage

The backend is written in Python, and was set up using uv. Installation instructions can be found [here](https://docs.astral.sh/uv/getting-started/installation/).

Start by installing dependencies:

```bash
cd backend
uv sync
```

Then start the backend:

```bash
uv run manage.py runserver
```

This will first build the search index, and then start the web server. The web scraping and indexing may take some time, as it attempts to fetch 2000 documents.

Next, setup start the frontend.

```bash
cd frontend
npm install
npm run dev
```

This will start the frontend on http://localhost:5173. From here, the frontend can be used to search the document database.
