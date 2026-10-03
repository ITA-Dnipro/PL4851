# Forum-Project-Stage-CC
Forum Project Stage CC Template Repo

**Project Vision Statement:**

*"Empowering Innovation: Bridging Startups and Investors for Ukraine's Economic Growth"*

**Overview:**

In the dynamic world of entrepreneurship, the path from a transformative idea to a successful venture is often complex and challenging. Our WebAPI application, developed using the Django Rest Framework, is designed to be a cornerstone in simplifying this journey. We aim to create a robust and secure digital platform that caters to two pivotal groups in the business ecosystem: innovative startups with compelling ideas and forward-thinking investors seeking valuable opportunities.

**Goals:**

1. **Fostering Collaborative Opportunities:** Our platform bridges startups and investors, enabling startups to showcase their groundbreaking proposals and investors to discover and engage with high-potential ventures.

2. **Seamless User Experience:** We prioritize intuitive navigation and interaction, ensuring that startups and investors can easily connect, communicate, and collaborate.

3. **Secure and Trustworthy Environment:** Security is at the forefront of our development, ensuring the confidentiality and integrity of all shared information and communications.

4. **Supporting Economic Growth:** By aligning startups with the right investors, our platform not only cultivates individual business success but also contributes significantly to the growth and diversification of Ukraine's economy.

**Commitment:**

We are committed to delivering a platform that is not just a marketplace for ideas and investments but a thriving community that nurtures innovation fosters economic development, and supports the aspirations of entrepreneurs and investors alike. Our vision is to see a world where every transformative idea has the opportunity to flourish and where investors can confidently fuel the engines of progress and innovation.

![image](https://github.com/mehalyna/Forum-Project-Stage-CC/assets/39273210/54b0de76-f6e3-4bf3-bf38-fb5bf1d1d63d)



### Basic Epics

0. **As a user of the platform**, I want the ability to represent both as a startup and as an investor company, so that I can engage in the platform's ecosystem from both perspectives using a single account.

   - Features:
     - implement the functionality for users to select and switch roles.

2. **As a startup company,** I want to create a profile on the platform, so that I can present my ideas and proposals to potential investors.

   - Features:
     -  user registration functionality for startups.
     -  profile setup page where startups can add details about their company and ideas.

3. **As an investor,** I want to view profiles of startups, so that I can find promising ideas to invest in.

   - Features:
     -  feature for investors to browse and filter startup profiles.
     -  viewing functionality for detailed startup profiles.

4. **As a startup company,** I want to update my project information, so that I can keep potential investors informed about our progress and milestones.

   - Features:
     -  functionality for startups to edit and update their project information.
     -  system to notify investors about updates to startups they are following.

5. **As an investor,** I want to be able to contact startups directly through the platform, so that I can discuss investment opportunities.

   - Features:
     -  secure messaging system within the platform for communication between startups and investors.
     -  privacy and security measures to protect the communication.

6. **As a startup company,** I want to receive notifications about interested investors, so that I can engage with them promptly.

   - Features:
     -  notification functionality for startups when an investor shows interest or contacts them.
     -  dashboard for startups to view and manage investor interactions.

7. **As an investor,** I want to save and track startups that interest me, so that I can manage my investment opportunities effectively.

   - Features:
     -  feature for investors to save and track startups.
     -  dashboard for investors to manage their saved startups and investment activities.

### Additional Features

- **Security and Data Protection**: Ensure that user data, especially sensitive financial information, is securely handled.

- **User Feedback System**: Create a system for users to provide feedback on the platform, contributing to continuous improvement.

- **Analytical Tools**: Implement analytical tools for startups to understand investor engagement and for investors to analyze startup potential.

### Agile Considerations

- Each user story can be broken down into smaller tasks and developed in sprints.
- Regular feedback from both user groups (startups and investors) should be incorporated.


## Local Development with Docker

### Prerequisites

- Docker Desktop
- Docker Compose

### Environment Setup

Create a local `.env` file from `.env.example`:

```powershell
Copy-Item .env.example .env
```

Update the values in `.env` if necessary.

### Run the Project

Build and start all services:

```powershell
docker compose up --build
```

This starts:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432

### Database Migrations

After the containers are running, open another terminal and run:

```powershell
docker compose exec backend python manage.py migrate
```

### Initial Content

Load the initial landing content (see [backend/README.md](backend/README.md#landing-content)):

```powershell
docker compose exec backend python manage.py loaddata landing
```

This is enough for the frontend to get data from `GET /api/content/landing/`.

### Admin Panel (optional)

To edit content in the admin, create an admin user:

```powershell
docker compose exec backend python manage.py createsuperuser
```

Then open http://localhost:8000/admin/

### Backend Health Check

Open:

http://localhost:8000/api/health/

A working backend should return:

```json
{
  "status": "ok"
}
```

### Stop the Project

To stop all containers:

```powershell
docker compose down
```


### Code Style & Linting


Checks run automatically on `git commit` via [pre-commit](https://pre-commit.com/) hooks (config: `.pre-commit-config.yaml`).

| Part | Tools | Config |
|---|---|---|
| Backend | black (formatting), isort (imports), flake8 + flake8-quotes (lint) | `backend/pyproject.toml`, `backend/.flake8` |
| Frontend | ESLint | `frontend/eslint.config.js` |
| Any file | trailing whitespace, end of file, YAML syntax, merge conflicts, large files | `.pre-commit-config.yaml` |

Style rules: line length 88, **single quotes** in Python (black keeps quotes as written, flake8-quotes enforces single).

#### Setup

Install pre-commit globally, once per machine (it does not depend on the backend venv or Docker):

```bash
# with uv (works on Linux, macOS and Windows; uv downloads Python itself if needed)
uv tool install pre-commit

# or, if Python is already installed
pipx install pre-commit         # or: pip install --user pre-commit
```

Check: `pre-commit --version`.

Then, once per clone, from the repo root:

```bash
pre-commit install

# frontend dependencies are needed for the ESLint hook
npm --prefix frontend install
```

Hooks install their own isolated copies of black, isort and flake8 (versions pinned in `.pre-commit-config.yaml`). To run these tools manually or get them in your IDE, install `backend/requirements-dev.txt` into the backend venv (see `backend/README.md`).

#### Run manually

```bash
pre-commit run --all-files      # all hooks on the whole repo

# or individual tools
cd backend && black . && isort . && flake8
cd frontend && npm run lint
```

If a hook modifies files (black, isort, end-of-file-fixer), the commit is stopped: review the changes, `git add` them and commit again.
