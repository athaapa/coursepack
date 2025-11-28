# CoursePack

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Poetry](https://img.shields.io/badge/Poetry-1.0+-orange.svg)](https://python-poetry.org/)

AI-powered course planning and artifact generation for **Structure and Interpretation of Computer Programs (SICP)**. Automate the creation of comprehensive course materials, including lesson plans, homework assignments, exams, and student repositories—all generated using Google's Gemini AI.

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## 📖 About

CoursePack is a Python-based tool that leverages advanced AI to streamline the process of planning and generating educational materials for teaching SICP. By integrating with Google's Gemini AI, it automatically creates:

- Weekly course schedules
- Detailed lecture plans
- Homework assignments with LaTeX formatting
- Automated testing scripts in Scheme
- Midterm and final exams
- Complete student-facing repositories with CI/CD integration

This tool is designed for educators who want to focus on teaching rather than administrative tasks, providing a solid foundation for course delivery while allowing customization.

## ✨ Features

- **🤖 AI-Generated Content**: Utilizes Gemini AI to create contextually relevant course materials based on SICP subsections.
- **📄 LaTeX & PDF Generation**: Produces professional homework and exam documents, automatically compiled to PDF using pdflatex.
- **📅 Calendar Integration**: Exports course schedules to iCalendar (.ics) format for seamless import into calendar applications.
- **🧪 Automated Grading**: Generates Scheme test files for homework verification, with GitHub Actions support for continuous integration.
- **📚 Repository Generation**: Builds a complete student repository with assignments, solutions, and instructions.
- **🔧 Customizable**: Easily configurable for different course structures, quarters, and AI models.
- **🔒 Secure**: Uses environment variables for API keys to maintain security.

## 🚀 Installation

### Prerequisites

- **Python**: 3.8 or higher
- **Google Gemini API Key**: Obtain from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **LaTeX Distribution**: For PDF compilation
  - macOS: `brew install mactex`
  - Ubuntu/Debian: `sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-extra-utils texlive-latex-recommended`
  - Windows: Install [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)

### Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/coursepack.git
   cd coursepack
   ```

2. **Install Dependencies**:
   ```bash
   # Using pip
   pip install -r requirements.txt

   # Or using Poetry (recommended)
   poetry install
   ```

3. **Verify Installation**:
   ```bash
   python -c "import coursepack; print('CoursePack installed successfully!')"
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your-gemini-api-key-here
```

### Course Configuration

Edit `config.json` to customize your course:

```json
{
  "book": {
    "title": "SICP",
    "subsections": [
      "1.1.1 Expressions",
      "1.1.2 Naming and the Environment",
      "1.1.3 Evaluating Combinations"
    ]
  },
  "quarter": {
    "start": "2024-09-01",
    "lectures_per_week": 3,
    "lecture_start_time": "12:30",
    "lecture_duration_minutes": 50
  }
}
```

- **book.subsections**: List of SICP subsections to cover
- **quarter.start**: ISO date for the first Monday of the quarter
- **quarter.lectures_per_week**: Number of lectures per week (typically 3)
- **quarter.lecture_start_time**: Start time for lectures (HH:MM format)
- **quarter.lecture_duration_minutes**: Length of each lecture

## 📚 Usage

### Basic Usage

Generate a complete course plan:

```bash
python -m coursepack.planner
```

This command will:
- 📝 Generate weekly lesson plans
- 📅 Export a calendar (`plan.ics`)
- 📄 Create LaTeX documents and compile to PDFs
- 🧪 Generate Scheme test files
- 📦 Build a student repository (`course_repo/`)

### Advanced Usage

#### Custom AI Models

Modify `coursepack/planner.py` to use different Gemini models:

```python
response = client.models.generate_content(
    model="gemini-1.5-pro",  # Change model here
    contents=prompt,
    config=types.GenerateContentConfig(...)
)
```

#### LaTeX Customization

Edit the LaTeX templates in `coursepack/planner.py` to customize document formatting.

#### Selective Generation

Use the individual functions for specific tasks:

```python
from coursepack.planner import generate_plan, export_calendar, generate_course_artifacts

plan = generate_plan(config)
export_calendar(plan, config)
generate_course_artifacts(client, plan, config)
```

## 🏗️ Project Structure

```
coursepack/
├── coursepack/
│   ├── __init__.py
│   ├── planner.py          # Core planning and generation logic
│   └── toc_extractor.py    # Utilities for table of contents
├── config.json             # Course configuration
├── toc.json                # SICP table of contents data
├── plan.json               # Generated course plan (output)
├── plan.ics                # Calendar export (output)
├── course_repo/            # Generated student repository (output)
│   ├── homework/           # Weekly assignments
│   ├── exams/              # Midterm and final exams
│   ├── .github/            # CI/CD workflows
│   └── README.md           # Student instructions
├── pyproject.toml          # Project dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔄 How It Works

1. **📊 Planning Phase**: Groups SICP subsections into weekly sections based on configuration.
2. **🤖 AI Generation**: Sends prompts to Gemini AI to create lesson plans, homework, and exams.
3. **📝 Artifact Creation**: Generates LaTeX documents, Scheme test files, and repository structure.
4. **🖨️ Compilation**: Uses pdflatex to compile LaTeX documents into PDFs.
5. **📤 Export**: Saves plans as JSON, calendars as ICS, and builds the complete repository.

The AI ensures content is pedagogically sound and aligned with SICP's teaching philosophy.

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'feat: add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Setup

```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .
```

### Guidelines

- Use conventional commits
- Add tests for new features
- Update documentation
- Ensure backward compatibility

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Harold Abelson and Gerald Jay Sussman** for *Structure and Interpretation of Computer Programs*
- **Google** for the Gemini AI platform
- **The Scheme Community** for the programming language that makes SICP possible
- **Open Source Contributors** for the libraries used in this project

---

**Made with ❤️ for educators and students of computer science.**