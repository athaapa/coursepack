# Coursepack Architecture

## Overview

Coursepack is a Python-based CLI tool for generating academic course plans, including syllabi and calendar events, from a book's table of contents (TOC). It supports both manual configuration and automated TOC extraction from PDFs. The tool is designed for educators planning courses around textbooks like SICP (Structure and Interpretation of Computer Programs).

Key features:
- Interactive TOC selection with hierarchical checkboxes.
- Automatic syllabus and iCalendar generation.
- Type-safe, validated inputs.
- Extensible for different books and systems.

## Components

### Core Modules

#### `coursepack/planner.py`
- **Purpose**: Main entry point for generating course plans.
- **Functionality**:
  - Loads TOC from JSON (extracted or provided).
  - Filters extraneous content (e.g., prefaces, indices).
  - Interactive CLI for user inputs: book title, system (semester/quarter), chapter/section/subsection selection, term details, dates.
  - Builds hierarchical config from selections.
  - Generates `syllabus.md` (Markdown table with weeks, lectures, homework, due dates).
  - Generates `plan.ics` (iCalendar file with lecture, homework, midterm, and final events).
- **Key Classes/Functions**:
  - `TocItem` (TypedDict): Represents TOC items with title, page, children.
  - `LectureItem` (TypedDict): Represents lectures with code, title, weight, level.
  - `filter_main_chapters()`: Removes non-content TOC items.
  - `parse_toc()`: Converts config TOC to lecture list with weights.
  - Main logic: Handles scheduling, HW assignment, calendar creation.
- **Dependencies**: Click (CLI), Questionary (interactive prompts), Pandas (Markdown table), iCalendar (ICS generation).

#### `coursepack/toc_extractor.py`
- **Purpose**: Extracts TOC from PDF outlines.
- **Functionality**:
  - Reads PDF using pypdf.
  - Parses outlines into nested JSON structure.
  - Outputs `toc.json` with titles, page numbers, and hierarchy.
- **Key Functions**:
  - `parse_outline()`: Recursively builds TOC from PDF outlines.
- **Dependencies**: pypdf (PDF reading).

### Configuration and Data

#### `config.json` (Example)
- JSON structure for manual config:
  ```json
  {
    "book": {"title": "SICP", "toc": {"1": {"title": "Ch1", "1": {"title": "Sec1", "subsections": [...]}}}},
    "quarter": {"start": "2026-01-05", "lectures_per_week": 3},
    "assessments": {"homeworks": 8, "midterm_week": 6}
  }
  ```
- TOC is hierarchical: chapters > sections > subsections.

#### `toc.json` (Generated)
- Flat list of TOC items from PDF extraction.
- Used as input for interactive selection.

### Outputs

#### `syllabus.md`
- Markdown table summarizing the course schedule.

#### `plan.ics`
- iCalendar file for importing into calendar apps (e.g., Google Calendar).

## Data Flow

1. **TOC Acquisition**:
   - Run `toc_extractor` on PDF to generate `toc.json`.
   - Alternatively, provide manual `config.json`.

2. **Interactive Configuration**:
   - `planner` loads TOC, filters main chapters.
   - User selects chapters/sections/subsections via nested checkboxes.
   - Collects term details (weeks, lectures/week, HW, dates).

3. **Config Building**:
   - Constructs hierarchical TOC dict from selections.
   - Applies weights: chapters (3 lectures), sections (2), subsections (1).

4. **Scheduling**:
   - Distributes lectures across weeks (round-robin).
   - Assigns HW to sections with exercises.
   - Sets midterm/final dates.

5. **Output Generation**:
   - Creates syllabus table with lectures, HW, due dates.
   - Generates ICS events for all items.

## Dependencies

- **Core**: Python 3.12+
- **Libraries** (from `pyproject.toml`):
  - `click`: CLI framework.
  - `questionary`: Interactive prompts with colors.
  - `pandas`: Data manipulation for syllabus.
  - `icalendar`: ICS file creation.
  - `pypdf`: PDF TOC extraction.
  - Others: `tabulate`, `uvicorn` (unused in core).

Install via Poetry: `poetry install`.

## Usage

### Extract TOC
```bash
toc_extractor book.pdf  # Outputs toc.json
```

### Generate Plan
```bash
coursepack --contents toc.json  # Interactive mode
```

### Manual Config
```bash
coursepack config.json  # Old mode (deprecated)
```

## Design Principles

- **Type Safety**: Full type hints with TypedDict for data structures.
- **Modularity**: Separate extraction and planning.
- **User-Friendly**: Interactive, validated inputs with colors.
- **Extensibility**: Easy to add new books or systems.
- **Validation**: Input ranges, date formats enforced.

## Future Improvements

- Support for multiple books in one plan.
- Custom weight assignment.
- Integration with LMS (e.g., Canvas API).
- Web UI using Uvicorn/FastAPI.
- Better PDF parsing for non-outline TOCs.
- Unit tests for core functions.

## Contributing

- Follow type hints and add tests.
- Update this doc for new features.
- Use Poetry for dependency management.