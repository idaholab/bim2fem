# bim2fem

<!-- ![Tests](https://github.com/idaholab/bim2fem/workflows/Tests/badge.svg) -->
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-LGPL-green)

Convert Building Information Models (BIM) to Finite Element Models (FEM) for structural analysis.

<table>
  <tr>
    <td align="center"><strong>Revit Model</strong></td>
    <td align="center"><strong>IFC4 ReferenceView</strong></td>
    <td align="center"><strong>IFC4 StructuralAnalysisView</strong></td>
  </tr>
  <tr>
    <td><img src="src/bim2fem/images/Revit_original.png" alt="Original Revit model" width="300"/></td>
    <td><img src="src/bim2fem/images/Revit_IFC4_ReferenceView.png" alt="IFC4 ReferenceView" width="300"/></td>
    <td><img src="src/bim2fem/images/Revit_IFC4_StructuralAnalysisView.png" alt="IFC4 StructuralAnalysisView" width="300"/></td>
  </tr>
</table>

## What is bim2fem?

**bim2fem** is an open-source ([LGPL]) Python-based software that converts 3D architectural [BIM] models into [FEM] models ready for structural analysis. Support for transforming 3D building and piping models is implemented for the Industry Foundation Classes ([IFC]) standard. 

### Key Features

- **BIM to FEM conversion** - Transform architectural models into structural analysis models (support for building and piping elements)
- **IFC4 support** - Compatibility with IFC standard (release [IFC4 Add2 TC1])
- **Enhanced IFC manipulation** - Extended IfcOpenShell functionality for building and piping elements via IfcPlus subpackage
- **GLB export** - Convert IFC to GLB format for 3D visualization
- **Web interface** - User-friendly GUI for non-programmers
- **Python API** - Full programmatic control for developers


### Contents

| Module | Description |
|--------|-------------|
| `bim2fem.core` | Core utility for converting IFC4 from ReferenceView/DesignTransferView to StructuralAnalysisView |
| `bim2fem.ifcplus` | Extension of the IfcOpenShell-Python library for enhanced IFC manipulation of building and piping models      |
| `bim2fem.bim2glb` | Extension of IfcConvert for improved IFC to GLB conversion for 3D visualization |


## Getting Started

### Interactive GUI (for non-developers)

If you just want to convert files using the graphical interface:

1. **Install Python** (<3.14, >=3.9) from [python.org](https://python.org)
   - ✅ During installation, check "Add Python to PATH"

2. **Download this project**
   ```bash
   git clone https://github.com/idaholab/bim2fem.git
   cd bim2fem
   ```

3. **Double-click `run_bim2fem.py`** or run:
   ```bash
   python run_bim2fem.py
   ```
   Note: Initial setup may take a couple minutes.

4. **Your browser will open** with the web interface at `http://localhost:5000`

### For Developers (API)

#### Installation from PyPI (Coming Soon)

```bash
pip install bim2fem
```

#### Installation from Source

```bash
# Clone the repository
git clone https://github.com/idaholab/bim2fem.git
cd bim2fem

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt  # For development tools and base requirements
```

#### Basic Usage (coming soon)

```python
import ifcopenshell
from bim2fem.core import convert_ifc_to_fem
from bim2fem.bim2glb import convert_ifc_to_glb

# Additional Details Coming Soon!
```




## Contributing

We welcome contributions! Whether you're fixing bugs, adding features, or improving documentation, here's how to get started.

### Prerequisites

- A GitHub account (free at [github.com](https://github.com))
- Git installed on your computer ([download here](https://git-scm.com/downloads))
- Python 3.11+ installed ([python.org](https://python.org))
- Basic familiarity with command line/terminal

### Step-by-Step Contribution Guide for External Contributors

#### 1. Fork the Repository

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

#### 2. Create a new branch for your work

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


#### 3. Set Up Development Environment (same for both external and team member contributors)

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




#### 4. Make Your Changes, Run Tests, and Commit Regularly (same for both external and team member contributors)

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



#### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

#### 6. Create a Pull Request

- Go to your fork on GitHub
- You'll see a banner saying "feature/your-feature-name had recent pushes"
- Click "Compare & pull request"
- Fill out the PR template:
  - **Title**: Brief description (e.g., "Add IFC2x3 support for wall elements")
  - **Description**: Explain what changed and why
  - **Testing**: Describe how you tested it
  - **Screenshots**: Include if relevant
- Click "Create pull request"

#### 7. Respond to Feedback

- Maintainers may request changes
- Make changes in your local branch
- Commit and push again - the PR updates automatically
- Mark conversations as resolved when addressed


### Step-by-Step Contribution Guide for Team Members

#### 1. Set up Your Local Repo

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


#### 2. Create a new branch for your work

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

#### 3. Set Up Development Environment (same for both external and team member contributors)

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

#### 4. Make Your Changes, Run Tests, and Commit Regularly (same for both external and team member contributors)

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



#### 5. Push your branch to GitHub

```bash
# First push (creates the branch on GitHub)
git push -u origin your-branch-name

# Subsequent pushes (after more commits)
git push
```

#### 6. Create a Pull Request

- Go to the repository on GitHub
- You'll see a yellow banner with your branch name
- Click "Compare & pull request"
- Add a description of your changes
- Assign a team member to review (optional)
- Click "Create pull request"

#### 7. After PR is merged, clean up

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

#### Team Member Best Practices

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

### What Makes a Good Contribution?

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

### Types of Contributions We Need

- 🐛 **Bug fixes**: Found something broken? Fix it!
- ✨ **Features**: New IFC entities, conversion options, etc.
- 📖 **Documentation**: Clarify usage, add examples, fix typos
- 🧪 **Tests**: Increase test coverage
- 🎨 **Code cleanup**: Improve code organization (discuss first)
- 🌐 **Examples**: Sample IFC files, usage tutorials

### Getting Help

- **Questions?** Open a [Discussion](https://github.com/YOUR_USERNAME/bim2fem/discussions)
- **Bug?** Open an [Issue](https://github.com/YOUR_USERNAME/bim2fem/issues)
- **Need guidance?** Comment on the issue you want to work on

### First Time Contributing to Open Source?

These resources can help:
- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [First Timers Only](https://www.firsttimersonly.com/)
- [GitHub's Fork & PR Workflow](https://docs.github.com/en/get-started/quickstart/contributing-to-projects)




### Quick Command Reference

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












## Requirements

- Python <3.14, >=3.9
- IfcOpenShell
- NumPy
- Flask (for web interface)
- See `requirements.txt` for full list

## Platform Support

- ✅ Windows
- ✅ Linux
- ✅ macOS

Note: The project includes platform-specific IfcConvert executables for each OS.

## License

This project is licensed under the LGPL License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Developed at [Idaho National Lab]
- Built on top of [IfcOpenShell]
- IFC standard by [buildingSMART]

## Roadmap

- [ ] PyPI package publication
- [ ] Detailed Documentation
- [ ] Extension of capabilities for complex building and piping elements
- [ ] Support for IFC4x3 input files

## Support

- 📖 [Documentation](https://github.com/Crowder44/bim2fem/wiki) (Coming Soon)
- 🐛 [Report Issues](https://github.com/Crowder44/bim2fem/issues)
- 💬 [Discussions](https://github.com/Crowder44/bim2fem/discussions)

---

**Note**: This project is under active development. APIs may change in future versions.

[BIM]: https://en.wikipedia.org/wiki/Building_information_modeling "BIM"
[FEM]: https://en.wikipedia.org/wiki/Finite_element_method "FEM"
[LGPL]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/COPYING.LESSER "LGPL-3.0-or-later"
[IFC]: https://technical.buildingsmart.org/standards/ifc/ "IFC"
[IFC4 Add2 TC1]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/ "IFC4 Add2 TC1"
[IfcOpenShell]: http://ifcopenshell.org/ "IfcOpenShell"
[buildingSMART]: https://www.buildingsmart.org/ "buildingSMART"
[Idaho National Lab]: https://inl.gov/ "Idaho National Lab"