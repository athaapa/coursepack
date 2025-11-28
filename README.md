# coursepack

AI-powered course planning and artifact generation for **Structure and Interpretation of Computer Programs (SICP)**.

`coursepack` is a Python-based tool that leverages Google's Gemini AI to automatically generate comprehensive course materials for teaching SICP. It creates weekly lesson plans, homework assignments, exams, and even compiles them into PDFs using LaTeX.

## Features

- **AI-Generated Course Plans**: Automatically generates weekly lesson plans based on SICP subsections.
- **LaTeX & PDF Generation**: Creates homework assignments and exams as LaTeX documents, compiled to PDF.
- **Calendar Export**: Exports course schedules to iCalendar (.ics) format for easy import into calendar apps.
- **Automated Testing**: Generates Scheme test files for homework verification.
- **GitHub Integration**: Includes CI/CD workflows for automated homework grading using Guile Scheme.
- **Complete Repository Generation**: Builds a full student-facing repository with assignments, solutions, and instructions.

## Installation

### Prerequisites

- Python 3.8+
- A Google Gemini API key (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))
- LaTeX distribution for PDF compilation

### System Dependencies

Install LaTeX (pdflatex):

- **macOS** (with Homebrew): `brew install mactex`
- **Ubuntu/Debian**: `sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-extra-utils texlive-latex-recommended`
- **Windows**: Install [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)

### Python Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/coursepack.git
   cd coursepack
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # or using Poetry
   poetry install
   ```

3. Set up your API key in `config.json`:
   ```json
   {
     "gemini_api_key": "your-api-key-here"
   }
   ```

## Usage

### Basic Usage

Run the planner to generate a complete course:

```bash
python -m coursepack.planner
```

This will:
- Generate a course plan in `plan.json`
- Export a calendar to `plan.ics`
- Create a full course repository in `course_repo/` with:
  - Weekly homework assignments (PDFs)
  - Scheme test files
  - Midterm and final exams (PDFs)
  - GitHub Actions workflow for autograding
  - Student README with instructions

### Configuration

Edit `config.json` to customize:

- **Book Subsections**: List of SICP subsections to cover
- **Quarter Details**: Start date, lectures per week, etc.
- **API Key**: Your Gemini API key

Example `config.json`:
```json
{
  "book": {
    "title": "SICP",
    "subsections": [
      "1.1.1 Expressions",
      "1.1.2 Naming and the Environment"
    ]
  },
  "quarter": {
    "start": "2024-09-01",
    "lectures_per_week": 3
  },
  "gemini_api_key": "your-key"
}
```

### Advanced Usage

- **Custom Models**: Modify `coursepack/planner.py` to use different Gemini models
- **LaTeX Templates**: Edit the template strings in the code for custom formatting
- **Scheme Testing**: The generated tests use Guile Scheme; ensure it's installed for local testing

## Project Structure

```
coursepack/
├── coursepack/
│   ├── __init__.py
│   ├── planner.py          # Main planning logic
│   └── toc_extractor.py    # Table of contents utilities
├── config.json             # Configuration file
├── toc.json                # SICP table of contents
├── plan.json               # Generated course plan
├── plan.ics                # Calendar export
├── course_repo/            # Generated student repository
├── README.md
├── pyproject.toml
└── .gitignore
```

## How It Works

1. **Planning**: Groups SICP subsections into weekly sections
2. **AI Generation**: Uses Gemini to create lesson plans, homework, and exams
3. **Artifact Creation**: Generates LaTeX documents and Scheme tests
4. **Compilation**: Compiles LaTeX to PDF using pdflatex
5. **Export**: Saves plans as JSON and calendars as ICS

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Based on **Structure and Interpretation of Computer Programs** by Harold Abelson and Gerald Jay Sussman
- Powered by Google Gemini AI
- LaTeX compilation via pdflatex