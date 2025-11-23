# EnglishTeacher Commerce Skeleton

This repository contains a Vue 3 + TypeScript frontend (Vite) and a FastAPI backend with MySQL persistence and JWT-based authentication.

## Frontend
- Located in `frontend/`
- Vue Router with login and admin role guards
- Pinia stores for user/session and cart
- Axios interceptors attach JWT and redirect to login on 401
- Basic pages: Home, Login, Product List/Detail, Checkout with WeChat JS-SDK hooks, admin placeholders

### Run
```bash
cd frontend
npm install
npm run dev
```

## Backend
- Located in `backend/`
- FastAPI with SQLAlchemy, JWT auth, product/order/payment services, and admin routes
- MySQL connection configured via `DATABASE_URL`

### Run
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker Compose
A `docker-compose.yml` is provided to start MySQL, backend, and frontend together.

## Fresh macOS setup tips
If you're setting up on a nearly blank macOS machine, install tools as a regular user (do **not** use `sudo su -`):

```bash
# Homebrew (any directory, regular user shell)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add Homebrew to PATH (Apple Silicon default)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$($(brew --prefix)/bin/brew shellenv)"

# Command Line Tools and packages
xcode-select --install
brew install git node python@3.11 mysql
```

If the Homebrew installer stops after asking for your login password, check that your prompt is not a root shell (`#` or `root@`).
Rerun the script from a normal user terminal instead of `sudo` or `sudo su -`.

### If you only have one admin user and install still fails
These steps keep you in your normal macOS account (not root) and work even if the installer prompts for your login password:

1. Open a new Terminal window (avoid `sudo su -`). Prompt should end with `$`, not `#`.
2. Confirm you are your own user:
   ```bash
   whoami
   groups
   ```
   You should see your short username and `admin` in the groups list.
3. Remove any partial Homebrew install (only if you tried before):
   ```bash
   rm -rf /opt/homebrew /usr/local/Homebrew
   ```
4. Run the installer again as your user (no sudo):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
5. Follow the on-screen prompt to add Homebrew to PATH, then verify:
   ```bash
   eval "$(/opt/homebrew/bin/brew shellenv)"  # Apple Silicon default
   brew --version
   ```
6. Install the required tools (still in the same terminal):
   ```bash
   xcode-select --install
   brew install git node python@3.11 mysql
   ```

If any step errors, copy the exact terminal output and rerun from a fresh non-root terminal.
