# Docker Setup for M30 Instagram Script

## Quick Start

### Prerequisites
- Docker and Docker Compose installed on your machine

### Running the Script

1. **Build and run the container:**
   ```bash
   docker-compose up
   ```

2. **The first time**, Docker will:
   - Build the image from the Dockerfile
   - Install all Python dependencies
   - Run your Instagram script

3. **Subsequent runs** are faster because the image is cached:
   ```bash
   docker-compose up
   ```

## Common Commands

**Run and see logs:**
```bash
docker-compose up
```

**Run in background:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f
```

**Stop the container:**
```bash
docker-compose down
```

**Rebuild the image (if you change requirements.txt):**
```bash
docker-compose up --build
```

**Run a one-off command inside the container:**
```bash
docker-compose run insta-bot python -m pytest
```

## How It Works

- **Dockerfile** - Defines the container with Python 3.11, dependencies, and your code
- **docker-compose.yml** - Simplifies running the container with:
  - Environment variables loaded from `.env`
  - Volume mounts so your `utils/`, image folders, and credentials persist
  - Container name for easy reference

## Important Notes

- Your `.env` file is automatically loaded - no need to change it
- All data (session.json, state.json, downloaded images) are saved locally in their respective folders
- The container runs your `src.main` by default
- If you need to test with pytest instead:
  ```bash
  docker-compose run insta-bot pytest
  ```

## Troubleshooting

**Container won't start:**
- Check Docker is running: `docker --version`
- Check `.env` file exists with valid credentials
- View logs: `docker-compose logs`

**Dependencies not installing:**
- Rebuild the image: `docker-compose up --build`

**Need to install new packages:**
- Add them to `requirements.txt`
- Rebuild: `docker-compose up --build`

## Deploying to a Server

To run this on a remote server (like AWS, DigitalOcean, etc.):

1. Install Docker on the server
2. Copy your project files (excluding `__pycache__`, `.venv`)
3. Copy your `.env` file with credentials
4. Run: `docker-compose up -d`
5. View logs: `docker-compose logs -f`

That's it! No Python, pip, or virtual environment setup needed.
