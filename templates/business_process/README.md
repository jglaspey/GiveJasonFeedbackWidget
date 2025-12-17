# [Process Name]

[Brief description of what this business process does]

## Setup

1. **Copy template**
   ```bash
   # From agent_dev_harness root
   cp -r templates/business_process projects/my_process
   cd projects/my_process
   ```

2. **Customize configuration**
   - Edit `.claude/CLAUDE.md` with process-specific instructions
   - Edit `.claude/settings.json` if you need different permissions
   - Edit `project-progress.json` and replace `{{PROJECT_NAME}}` with your project name
   - Copy `.env.example` to `.env` and add your configuration

3. **Add your functional code**
   - Scripts go in `functional/scripts/`
   - Prompts go in `functional/prompts/`
   - Configuration files go in `functional/config/`

4. **Run Claude Code**
   ```bash
   # Make sure you're in the project directory
   claude-code
   ```

## Directory Structure

```
project/
├── .claude/
│   ├── CLAUDE.md           # Process-specific instructions
│   └── settings.json       # Restrictive permissions
├── functional/
│   ├── scripts/            # Your Python scripts
│   ├── prompts/            # Isolated prompt files
│   ├── workers/            # Parallel processing workers (if needed)
│   └── config/             # Configuration files
├── outputs/                # Gitignored - run-specific results
│   └── run_YYYY-MM-DD_HHMMSS/
│       ├── logs/
│       ├── results/
│       └── errors/
├── test_scripts/           # Testing and validation
├── project-progress.json   # Session progress tracking
├── .env.example            # Template for environment variables
├── .env                    # Your local config (gitignored)
├── .gitignore
└── README.md
```

## Usage

[Add specific usage instructions for this process]

Example:
```bash
# Run the main process
python functional/scripts/main.py

# Check results
ls outputs/run_*/results/

# Review errors
cat outputs/run_*/errors/*.json
```

## Input Format

[Describe expected input format]

## Output Format

[Describe output format]

## Error Handling

[Describe how errors are handled]

## Resumability

This process supports resuming from failures:
- Progress is logged to `outputs/run_XXX/logs/progress.jsonl`
- Already-completed items are skipped on restart
- Each run is isolated in its own timestamp directory

## Development

[Add development notes]

Example:
- To test: Run scripts in `test_scripts/`
- To refine prompts: Edit files in `functional/prompts/`
- To debug: Check `outputs/run_XXX/logs/` and `outputs/run_XXX/errors/`
