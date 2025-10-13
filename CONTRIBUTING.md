# Contributing

We welcome contributions! Whether you're fixing bugs, adding features, or improving documentation, here's how to get started.

## Table of Contents
- [Prerequisites](#prerequisites)
- [External Contributors](#step-by-step-contribution-guide-for-external-contributors)
- [Team Members](#step-by-step-contribution-guide-for-team-members)
- [Best Practices](#what-makes-a-good-contribution)
- [Quick Command Reference](#quick-command-reference)
- [VS Code Setup](#vs-code-setup-optional)

## Prerequisites

- A GitHub account (free at [github.com](https://github.com))
- Git installed on your computer ([download here](https://git-scm.com/downloads))
- Python 3.11+ installed ([python.org](https://python.org))
- Basic familiarity with command line/terminal

## Step-by-Step Contribution Guide for External Contributors

### 1. Fork the Repository

A "fork" is your personal copy of the project where you can make changes.

- Go to https://github.com/idaholab/bim2fem
- Click the "Fork" button in the top-right corner
- GitHub creates a copy under your account (e.g., `contributor_username/bim2fem`)

Clone Your Fork Locally

```bash
# Clone your fork (not the original repo)
git clone https://github.com/contributor_username/bim2fem.git
cd bim2fem

# Add the original repo as "upstream" to keep your fork updated
git remote add upstream https://github.com/idaholab/bim2fem.git
```

### 2. Create a new branch for your work

Never work directly on `main`. Create a branch for your changes:

```bash
# Create and switch to a new branch
git checkout -b your-branch-name

# Good branch names:
# feature/add-wall-snapping
# fix/correct-beam-rotation
# test/add-geometry-tests
# docs/update-readme
```

Note: Keeping Your Fork and New Branch Updated

Before starting new work, sync with the original repository:

```bash
# Update your fork's main (as we discussed)
git checkout main
git fetch upstream
git merge upstream/main
git push origin main

# Switch to feature branch
git checkout feature/my-feature

# Merge your updated main
git merge main

# Push updated branch
git push origin feature/my-feature
```


### 3. Set Up Development Environment (same for both external and team member contributors)

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
```




### 4. Make Your Changes, Run Tests, and Commit Regularly (same for both external and team member contributors)

- Write your code
- Add/update tests in the `tests/` directory
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/ifcplus/api/test_geometry.py
```
- Update documentation if needed
- Follow existing code style and patterns
- **Commit regularly as you work**
```bash
# After completing each logical piece of work

# See what files you've changed
git status

# Add specific files
git add src/bim2fem/core/your_file.py

# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Add support for IFC2x3 wall elements"

# Good commit messages:
# ✅ "Fix wall-to-slab snapping for non-perpendicular connections"
# ✅ "Add GLB export options for material transparency"
# ❌ "Fixed stuff"
# ❌ "Updates"

# Don't wait until everything is done!
# Many small commits are better than one massive commit
```



### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create a Pull Request

- Go to your fork on GitHub
- You'll see a banner saying "feature/your-feature-name had recent pushes"
- Click "Compare & pull request"
- Fill out the PR template:
  - **Title**: Brief description (e.g., "Add IFC2x3 support for wall elements")
  - **Description**: Explain what changed and why
  - **Testing**: Describe how you tested it
  - **Screenshots**: Include if relevant
- Click "Create pull request"

### 7. Respond to Feedback

- Maintainers may request changes
- Make changes in your local branch
- Commit and push again - the PR updates automatically
- Mark conversations as resolved when addressed


## Step-by-Step Contribution Guide for Team Members

### 1. Set up Your Local Repo

Initial Setup (one-time only)

```bash
# Clone the repository directly
git clone https://github.com/idaholab/bim2fem.git
cd bim2fem

# Set up your identity (if not already done)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```


Start fresh from main

```bash
# Always start by updating your local main branch
git checkout main
git pull origin main
```


### 2. Create a new branch for your work

Never work directly on `main`. Create a branch for your changes:

```bash
# Create and switch to a new branch
git checkout -b your-branch-name

# Good branch names:
# feature/add-wall-snapping
# fix/correct-beam-rotation
# test/add-geometry-tests
# docs/update-readme
```

Note: Keeping Your Local Repo and New Branch Updated

Before starting new work, sync with the original repository:

```bash
# While on your feature branch
git checkout main
git pull origin main
git checkout your-branch-name
git merge main

# Or in one command (while on your branch)
git pull origin main
```

### 3. Set Up Development Environment (same for both external and team member contributors)

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
```

### 4. Make Your Changes, Run Tests, and Commit Regularly (same for both external and team member contributors)

- Write your code
- Add/update tests in the `tests/` directory
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/ifcplus/api/test_geometry.py
```
- Update documentation if needed
- Follow existing code style and patterns
- **Commit regularly as you work**
```bash
# After completing each logical piece of work

# See what files you've changed
git status

# Add specific files
git add src/bim2fem/core/your_file.py

# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Add support for IFC2x3 wall elements"

# Good commit messages:
# ✅ "Fix wall-to-slab snapping for non-perpendicular connections"
# ✅ "Add GLB export options for material transparency"
# ❌ "Fixed stuff"
# ❌ "Updates"

# Don't wait until everything is done!
# Many small commits are better than one massive commit
```



### 5. Push your branch to GitHub

```bash
# First push (creates the branch on GitHub)
git push -u origin your-branch-name

# Subsequent pushes (after more commits)
git push
```

### 6. Create a Pull Request

- Go to the repository on GitHub
- You'll see a yellow banner with your branch name
- Click "Compare & pull request"
- Add a description of your changes
- Assign a team member to review (optional)
- Click "Create pull request"

### 7. After PR is merged, clean up

```bash
# Switch back to main
git checkout main

# Pull the latest changes (including your merged PR)
git pull origin main

# Delete your local branch
git branch -d your-branch-name

# Delete the remote branch (optional, GitHub can do this automatically)
git push origin --delete your-branch-name
```

### Team Member Best Practices

✅ **Do:**
- Pull from main before starting new work
- Create a branch for each feature/fix
- Make small, focused commits
- Write clear commit messages
- Test your changes before pushing
- Ask for help if unsure

❌ **Don't:**
- Work directly on main branch
- Force push to main (it's protected anyway)
- Merge your own PRs without review (unless agreed upon)
- Leave branches lying around after merging

## What Makes a Good Contribution?

✅ **Do:**
- Include tests for new features
- Update documentation for user-facing changes
- Keep changes focused - one feature per PR
- Follow existing code patterns
- Ask questions if unsure

❌ **Don't:**
- Submit huge PRs with many unrelated changes
- Break existing tests
- Include files specific to your setup (.vscode/, .idea/, etc.)
- Commit sensitive information (API keys, passwords)

## Types of Contributions We Need

- 🐛 **Bug fixes**: Found something broken? Fix it!
- ✨ **Features**: New IFC entities, conversion options, etc.
- 📖 **Documentation**: Clarify usage, add examples, fix typos
- 🧪 **Tests**: Increase test coverage
- 🎨 **Code cleanup**: Improve code organization (discuss first)
- 🌐 **Examples**: Sample IFC files, usage tutorials

## Getting Help

- **Questions?** Open a [Discussion](https://github.com/idaholab/bim2fem/discussions)
- **Bug?** Open an [Issue](https://github.com/idaholab/bim2fem/issues)
- **Need guidance?** Comment on the issue you want to work on

## First Time Contributing to Open Source?

These resources can help:
- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [First Timers Only](https://www.firsttimersonly.com/)
- [GitHub's Fork & PR Workflow](https://docs.github.com/en/get-started/quickstart/contributing-to-projects)




## Quick Command Reference

| Task | Command |
|------|---------|
| See current branch | `git branch` |
| Switch branches | `git checkout branch-name` |
| Update current branch | `git pull` |
| See what's changed | `git status` |
| See commit history | `git log --oneline` |
| Undo uncommitted changes | `git checkout -- filename` |
| See remote URL | `git remote -v` |

---


## VS Code Setup (Optional)

If you're using VS Code, you can use our recommended settings for better Python and pytest integration:

1. Create a `.vscode` folder in the project root (if it doesn't exist)
2. Create a `settings.json` file inside `.vscode/`
3. Add the following configuration:
```json
{
    "python.testing.pytestEnabled": true,
    "python.analysis.extraPaths": [
        "./src"
    ],
    "python.testing.pytestArgs": [
        "."
    ],
    "python.testing.unittestEnabled": false
}
```

This configuration:

- Enables pytest as the test framework
- Adds the src/ directory to Python paths (fixes import warnings)
- Configures pytest to discover tests from the project root
- Disables unittest to avoid conflicts

Note: The .vscode/ folder is gitignored, so these settings won't be tracked. Each developer can customize them as needed.





