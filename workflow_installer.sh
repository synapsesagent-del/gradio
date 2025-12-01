#!/bin/bash
# Gradio Multi-Process Workflow System - Installer
# Automated setup for complete workflow orchestration

set -e  # Exit on error

echo "=================================================="
echo "  GRADIO WORKFLOW ORCHESTRATOR - INSTALLER"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo -e "${RED}Error: Python 3.10+ required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Create project directory
PROJECT_DIR="gradio-workflow-system"
echo ""
echo "Creating project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Create requirements.txt
echo ""
echo "Generating requirements.txt..."
cat > requirements.txt << 'EOF'
# Core Dependencies
gradio>=4.44.0
google-generativeai>=0.8.0
python-dotenv>=1.0.0

# Type Checking & Validation
pydantic>=2.9.0
typing-extensions>=4.12.0

# Utilities
python-dateutil>=2.9.0

# Development
pytest>=8.3.0
black>=24.8.0
ruff>=0.7.0
mypy>=1.11.0
EOF

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env template
echo ""
echo "Creating .env configuration file..."
cat > .env << 'EOF'
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
GRADIO_SHARE=False

# Workflow Settings
DEFAULT_MODEL=gemini-2.0-flash-exp
THINKING_MODEL=gemini-2.0-flash-thinking-exp
ENABLE_LOGGING=True
LOG_LEVEL=INFO
EOF

# Create directory structure
echo ""
echo "Creating project structure..."
mkdir -p src/{processes,workflows,utils}
mkdir -p data/{exports,logs}
mkdir -p tests

# Copy main application
echo ""
echo "Setting up main application..."
# (The main Python code would be copied here - already created in artifact above)

# Create example custom process
cat > src/processes/custom_process.py << 'EOF'
"""
Example: Create your own custom process

Add this process to workflow by importing and adding to process list
"""

from dataclasses import dataclass
from typing import Dict, Any
import google.generativeai as genai

@dataclass
class CustomProcessConfig:
    """Define your process configuration"""
    id: str = "my_custom_process"
    name: str = "My Custom Process"
    description: str = "Describe what this process does"
    gemini_model: str = "gemini-2.0-flash-exp"
    system_prompt: str = "You are a specialized agent for..."
    requires_approval: bool = False

def execute_custom_logic(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Implement custom process logic here
    
    Args:
        inputs: Dictionary of input data from previous processes
        
    Returns:
        Dictionary with process results
    """
    # Your custom logic
    result = inputs.get("input", "")
    
    # Call Gemini if needed
    # model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
    # response = model.generate_content(result)
    
    return {
        "output": result,
        "status": "success"
    }

# Export configuration
PROCESS_CONFIG = CustomProcessConfig()
EOF

# Create utilities
cat > src/utils/export_utils.py << 'EOF'
"""Utilities for exporting workflow results"""

import json
from typing import Dict, Any
from datetime import datetime

def export_to_json(data: Dict[str, Any], filename: str = None) -> str:
    """Export workflow data to JSON file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/exports/workflow_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return filename

def export_to_markdown(data: Dict[str, Any], filename: str = None) -> str:
    """Export workflow results to Markdown report"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/exports/workflow_{timestamp}.md"
    
    with open(filename, 'w') as f:
        f.write(f"# Workflow Report\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
        
        for process_id, output in data.get('processes', {}).items():
            f.write(f"## {process_id}\n\n")
            f.write(f"```\n{output.get('output', '')}\n```\n\n")
    
    return filename
EOF

# Create README
cat > README.md << 'EOF'
# Gradio Multi-Process Workflow Orchestrator

Interconnected Gradio applications managed by a single workflow orchestration agent.

## Architecture

```
┌──────────────────────────────────────────────────┐
│         Workflow Orchestrator (Agent)            │
│  - Manages process execution                     │
│  - Handles state & context                       │
│  - Routes data between processes                 │
└────────────────┬─────────────────────────────────┘
                 │
    ┌────────────┴────────────┬──────────────┐
    │                         │              │
┌───▼────┐  ┌────────┐  ┌────▼────┐  ┌──────▼──┐
│Process │  │Process │  │Process  │  │Process  │
│   1    │→ │   2    │→ │   3     │→ │   N     │
│(Gradio)│  │(Gradio)│  │(Gradio) │  │(Gradio) │
└────────┘  └────────┘  └─────────┘  └─────────┘
```

## Features

- **Multi-Process Execution**: Chain multiple Gradio apps together
- **Intelligent Orchestration**: AI agent manages workflow & data flow
- **Human-in-Loop**: Approval checkpoints for critical decisions
- **Context Awareness**: Each process receives outputs from previous steps
- **Gemini Integration**: Powered by Google Gemini 2.0 models
- **Export Results**: JSON/Markdown export of complete workflow

## Quick Start

### 1. Configure API Key

Edit `.env` and add your Gemini API key:
```bash
GEMINI_API_KEY=your_actual_api_key_here
```

Get API key: https://aistudio.google.com/apikey

### 2. Run Application

```bash
source venv/bin/activate
python app.py
```

Access at: http://localhost:7860

### 3. Start Workflow

1. Go to "Workflow Control" tab
2. Enter requirements in textbox
3. Click "🚀 Start Workflow"
4. Monitor progress in real-time
5. Approve processes when needed

## Default Workflow

The example implements a **code generation pipeline**:

1. **Requirements Analyzer** - Breaks down requirements
2. **Architecture Designer** - Designs system (requires approval)
3. **Code Generator** - Generates code
4. **Code Reviewer** - Reviews for quality/security
5. **Test Generator** - Creates test suite
6. **Documentation Writer** - Writes docs (requires approval)

## Creating Custom Workflows

### Define New Process

```python
from src.processes.custom_process import ProcessConfig

my_process = ProcessConfig(
    id="my_processor",
    name="My Processor",
    description="What this process does",
    inputs=["previous_output"],
    outputs=["processed_result"],
    gemini_model="gemini-2.0-flash-exp",
    system_prompt="You are a specialized agent for...",
    requires_approval=False
)
```

### Create Workflow

```python
my_workflow = [
    process_1,
    process_2,
    my_process,  # Your custom process
    process_n
]

orchestrator = WorkflowOrchestrator(my_workflow)
```

## Project Structure

```
gradio-workflow-system/
├── app.py                    # Main application
├── requirements.txt          # Python dependencies
├── .env                      # Configuration
├── README.md                 # This file
├── src/
│   ├── processes/           # Custom process definitions
│   ├── workflows/           # Workflow configurations
│   └── utils/               # Utility functions
├── data/
│   ├── exports/             # Exported results
│   └── logs/                # Application logs
└── tests/                   # Unit tests
```

## Advanced Usage

### Manual Process Execution

Execute individual processes via "Process Execution" tab:

1. Select process from dropdown
2. Enter input data
3. Click "▶️ Execute Process"
4. View output & context

### Auto-Advance Mode

Let orchestrator automatically execute all pending processes:

1. Start workflow with initial input
2. Click "⏭️ Auto-Advance Workflow"
3. Orchestrator executes processes sequentially
4. Pauses at approval checkpoints

### Export Results

After workflow completion:

1. Go to "Results" tab
2. Select process to view
3. Click "📥 Export as JSON" or "📝 Export as Markdown"
4. Download generated file

## Configuration

### Environment Variables

```bash
# API Configuration
GEMINI_API_KEY=xxx              # Required

# Server Settings
GRADIO_SERVER_NAME=0.0.0.0      # Bind address
GRADIO_SERVER_PORT=7860         # Port
GRADIO_SHARE=False              # Public sharing

# Model Selection
DEFAULT_MODEL=gemini-2.0-flash-exp
THINKING_MODEL=gemini-2.0-flash-thinking-exp

# Logging
ENABLE_LOGGING=True
LOG_LEVEL=INFO
```

### Model Selection

Available Gemini models:

- `gemini-2.0-flash-exp` - Fast, efficient (default)
- `gemini-2.0-flash-thinking-exp` - Deep reasoning
- `gemini-1.5-pro` - High capability
- `gemini-1.5-flash` - Speed optimized

## Troubleshooting

### API Key Issues

```bash
# Verify API key is set
echo $GEMINI_API_KEY

# Test API access
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('OK')"
```

### Port Already in Use

Change port in `.env`:
```bash
GRADIO_SERVER_PORT=8080
```

### Import Errors

Reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

## Cost Management

Gemini API pricing (as of Nov 2024):

- Flash models: $0.075 per 1M input tokens
- Pro models: $1.25 per 1M input tokens

Estimate costs:
- Simple workflow (6 processes): ~$0.01-0.05
- Complex workflow with code gen: ~$0.10-0.50

## Security Notes

- **Never commit `.env` to version control**
- Use separate API keys for dev/prod
- Implement rate limiting for production
- Validate all user inputs
- Review generated code before execution

## Contributing

To add new process types:

1. Create process config in `src/processes/`
2. Define system prompts
3. Add to workflow list
4. Test with sample inputs
5. Document usage

## License

MIT License - See LICENSE file

## Support

Issues: https://github.com/your-repo/issues
Docs: https://gradio.app/docs
Gemini: https://ai.google.dev/docs

EOF

# Create run script
cat > run.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python app.py
EOF
chmod +x run.sh

# Create test file
cat > tests/test_orchestrator.py << 'EOF'
"""Basic tests for workflow orchestrator"""

import pytest
from src.processes.custom_process import PROCESS_CONFIG

def test_process_config():
    """Test process configuration"""
    assert PROCESS_CONFIG.id == "my_custom_process"
    assert PROCESS_CONFIG.gemini_model == "gemini-2.0-flash-exp"

def test_workflow_initialization():
    """Test workflow orchestrator initialization"""
    # Add your tests here
    pass
EOF

# Final setup
echo ""
echo -e "${GREEN}=================================================="
echo -e "  INSTALLATION COMPLETE!"
echo -e "==================================================${NC}"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo "1. Configure API Key:"
echo -e "   ${GREEN}nano .env${NC}"
echo "   Add your Gemini API key"
echo ""
echo "2. Run application:"
echo -e "   ${GREEN}source venv/bin/activate${NC}"
echo -e "   ${GREEN}python app.py${NC}"
echo ""
echo "3. Access UI:"
echo -e "   ${GREEN}http://localhost:7860${NC}"
echo ""
echo -e "${YELLOW}PROJECT LOCATION:${NC}"
echo -e "   $(pwd)"
echo ""
echo -e "${YELLOW}DOCUMENTATION:${NC}"
echo -e "   cat README.md"
echo ""
echo "=================================================="