For development purposes:

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
which python  # should output inside .venv
```

```bash
python -m pip install --upgrade pip
```

```bash
echo * > .venv/.gitignore
```

```bash
pip install -r requirements.txt
```

```bash
fastapi dev mainapi.py
```

```bash
npm run dev
```

## FRONTEND NOTE
- Currently auth0 not fully set up, to skip auth go to frontend-src -> src -> App.jsx and switch Home and LandingPage in the first Route
