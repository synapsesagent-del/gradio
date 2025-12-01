"""
Gradio Multi-Process Workflow System
Orchestrator manages multiple specialized Gradio apps via one workflow agent
"""

import gradio as gr
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from datetime import datetime
import google.generativeai as genai
import os

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ============================================================================
# PROCESS DEFINITIONS
# ============================================================================

class ProcessStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_APPROVAL = "waiting_approval"

@dataclass
class ProcessConfig:
    """Configuration for a single Gradio process"""
    id: str
    name: str
    description: str
    inputs: List[str]
    outputs: List[str]
    gemini_model: str = "gemini-2.0-flash-exp"
    system_prompt: str = ""
    requires_approval: bool = False
    auto_advance: bool = True

@dataclass
class WorkflowState:
    """Global workflow state shared across processes"""
    current_process: int = 0
    process_outputs: Dict[str, Any] = field(default_factory=dict)
    process_status: Dict[str, ProcessStatus] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    workflow_id: str = ""
    started_at: Optional[datetime] = None
    
# ============================================================================
# WORKFLOW ORCHESTRATOR
# ============================================================================

class WorkflowOrchestrator:
    """Manages workflow execution across multiple Gradio processes"""
    
    def __init__(self, processes: List[ProcessConfig]):
        self.processes = {p.id: p for p in processes}
        self.process_order = [p.id for p in processes]
        self.state = WorkflowState(
            workflow_id=f"wf_{int(time.time())}",
            process_status={p.id: ProcessStatus.PENDING for p in processes}
        )
        self.gemini_clients = {}
        
    def init_gemini_client(self, process_id: str) -> genai.GenerativeModel:
        """Initialize Gemini client for a process"""
        if process_id not in self.gemini_clients:
            proc = self.processes[process_id]
            self.gemini_clients[process_id] = genai.GenerativeModel(
                model_name=proc.gemini_model,
                system_instruction=proc.system_prompt
            )
        return self.gemini_clients[process_id]
    
    def execute_process(self, process_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single process with Gemini"""
        proc = self.processes[process_id]
        self.state.process_status[process_id] = ProcessStatus.RUNNING
        
        try:
            model = self.init_gemini_client(process_id)
            
            # Build prompt with context from previous processes
            context = self._build_context(process_id)
            prompt = self._format_prompt(proc, inputs, context)
            
            # Execute with Gemini
            response = model.generate_content(prompt)
            result = {
                "output": response.text,
                "process_id": process_id,
                "timestamp": datetime.now().isoformat(),
                "inputs": inputs
            }
            
            # Store output
            self.state.process_outputs[process_id] = result
            self.state.process_status[process_id] = (
                ProcessStatus.WAITING_APPROVAL if proc.requires_approval 
                else ProcessStatus.COMPLETED
            )
            
            # Log to history
            self.state.history.append({
                "process": process_id,
                "action": "executed",
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            self.state.process_status[process_id] = ProcessStatus.FAILED
            return {
                "error": str(e),
                "process_id": process_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_context(self, current_process_id: str) -> str:
        """Build context from previous process outputs"""
        current_idx = self.process_order.index(current_process_id)
        context_parts = []
        
        for proc_id in self.process_order[:current_idx]:
            if proc_id in self.state.process_outputs:
                output = self.state.process_outputs[proc_id]
                context_parts.append(
                    f"[{self.processes[proc_id].name}]\n{output.get('output', '')}"
                )
        
        return "\n\n---\n\n".join(context_parts) if context_parts else ""
    
    def _format_prompt(self, proc: ProcessConfig, inputs: Dict, context: str) -> str:
        """Format prompt with inputs and context"""
        prompt_parts = []
        
        if context:
            prompt_parts.append(f"CONTEXT FROM PREVIOUS PROCESSES:\n{context}\n")
        
        prompt_parts.append(f"CURRENT TASK: {proc.description}\n")
        prompt_parts.append("INPUTS:")
        for key, value in inputs.items():
            prompt_parts.append(f"- {key}: {value}")
        
        return "\n".join(prompt_parts)
    
    def approve_process(self, process_id: str, approved: bool) -> str:
        """Approve or reject a process waiting for approval"""
        if approved:
            self.state.process_status[process_id] = ProcessStatus.COMPLETED
            return f"✅ Process '{self.processes[process_id].name}' approved"
        else:
            self.state.process_status[process_id] = ProcessStatus.FAILED
            return f"❌ Process '{self.processes[process_id].name}' rejected"
    
    def get_next_process(self) -> Optional[str]:
        """Get next pending process"""
        for proc_id in self.process_order:
            if self.state.process_status[proc_id] == ProcessStatus.PENDING:
                return proc_id
        return None
    
    def get_workflow_status(self) -> str:
        """Get current workflow status summary"""
        status_counts = {}
        for status in ProcessStatus:
            status_counts[status.value] = sum(
                1 for s in self.state.process_status.values() if s == status
            )
        
        return f"""
**Workflow ID:** {self.state.workflow_id}
**Total Processes:** {len(self.processes)}
**Completed:** {status_counts['completed']}
**Running:** {status_counts['running']}
**Pending:** {status_counts['pending']}
**Failed:** {status_counts['failed']}
**Waiting Approval:** {status_counts['waiting_approval']}
"""

# ============================================================================
# EXAMPLE WORKFLOW: CODE GENERATION PIPELINE
# ============================================================================

# Define specialized processes
code_gen_workflow = [
    ProcessConfig(
        id="requirements_analyzer",
        name="Requirements Analyzer",
        description="Analyze user requirements and break down into specifications",
        inputs=["requirements"],
        outputs=["specifications"],
        system_prompt="You are a requirements analyst. Break down user requirements into clear technical specifications with acceptance criteria."
    ),
    ProcessConfig(
        id="architecture_designer",
        name="Architecture Designer",
        description="Design system architecture based on specifications",
        inputs=["specifications"],
        outputs=["architecture"],
        system_prompt="You are a software architect. Design scalable, maintainable system architecture. Output should include component diagram, data flow, and tech stack decisions.",
        requires_approval=True
    ),
    ProcessConfig(
        id="code_generator",
        name="Code Generator",
        description="Generate production-ready code based on architecture",
        inputs=["architecture"],
        outputs=["code"],
        gemini_model="gemini-2.0-flash-thinking-exp",
        system_prompt="You are an expert coder. Generate clean, well-documented, production-ready code following best practices. Include error handling and tests."
    ),
    ProcessConfig(
        id="code_reviewer",
        name="Code Reviewer",
        description="Review generated code for quality, security, and best practices",
        inputs=["code"],
        outputs=["review_report"],
        system_prompt="You are a senior code reviewer. Analyze code for security vulnerabilities, performance issues, code quality, and best practice violations. Provide actionable feedback."
    ),
    ProcessConfig(
        id="test_generator",
        name="Test Generator",
        description="Generate comprehensive test suite",
        inputs=["code"],
        outputs=["tests"],
        system_prompt="You are a test engineer. Generate comprehensive unit tests, integration tests, and edge case tests. Use pytest for Python, vitest for TypeScript."
    ),
    ProcessConfig(
        id="documentation_writer",
        name="Documentation Writer",
        description="Generate complete documentation",
        inputs=["code", "architecture"],
        outputs=["documentation"],
        system_prompt="You are a technical writer. Create comprehensive documentation including README, API docs, deployment guide, and usage examples.",
        requires_approval=True
    )
]

# Initialize orchestrator
orchestrator = WorkflowOrchestrator(code_gen_workflow)

# ============================================================================
# GRADIO UI
# ============================================================================

def create_workflow_ui():
    """Create the main Gradio interface"""
    
    with gr.Blocks(title="Agentic Workflow System", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🤖 Multi-Process Agentic Workflow System")
        gr.Markdown("Interconnected Gradio apps managed by workflow orchestrator agent")
        
        # Global state
        workflow_state = gr.State(orchestrator.state)
        
        with gr.Tabs() as tabs:
            # ========== TAB 1: WORKFLOW CONTROL ==========
            with gr.Tab("Workflow Control"):
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("## Start New Workflow")
                        initial_requirements = gr.Textbox(
                            label="Initial Requirements",
                            placeholder="Describe what you want to build...",
                            lines=5
                        )
                        start_btn = gr.Button("🚀 Start Workflow", variant="primary")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("## Workflow Status")
                        status_display = gr.Markdown(orchestrator.get_workflow_status())
                        refresh_status_btn = gr.Button("🔄 Refresh Status")
                
                workflow_log = gr.Textbox(
                    label="Workflow Log",
                    lines=10,
                    interactive=False
                )
            
            # ========== TAB 2: PROCESS EXECUTION ==========
            with gr.Tab("Process Execution"):
                process_selector = gr.Dropdown(
                    choices=[(p.name, p.id) for p in code_gen_workflow],
                    label="Select Process",
                    value=code_gen_workflow[0].id
                )
                
                with gr.Row():
                    process_input = gr.Textbox(
                        label="Process Input",
                        placeholder="Input for selected process...",
                        lines=8
                    )
                    process_output = gr.Textbox(
                        label="Process Output",
                        lines=8,
                        interactive=False
                    )
                
                with gr.Row():
                    execute_btn = gr.Button("▶️ Execute Process", variant="primary")
                    auto_advance_btn = gr.Button("⏭️ Auto-Advance Workflow")
                
                process_context = gr.Textbox(
                    label="Context from Previous Processes",
                    lines=6,
                    interactive=False
                )
            
            # ========== TAB 3: APPROVAL QUEUE ==========
            with gr.Tab("Approval Queue"):
                gr.Markdown("## Processes Waiting for Approval")
                
                approval_process_display = gr.Textbox(
                    label="Process Awaiting Approval",
                    lines=3,
                    interactive=False
                )
                
                approval_output_display = gr.Textbox(
                    label="Output to Review",
                    lines=15,
                    interactive=False
                )
                
                with gr.Row():
                    approve_btn = gr.Button("✅ Approve", variant="primary")
                    reject_btn = gr.Button("❌ Reject", variant="stop")
                
                approval_result = gr.Textbox(
                    label="Approval Result",
                    interactive=False
                )
            
            # ========== TAB 4: RESULTS ==========
            with gr.Tab("Results"):
                gr.Markdown("## Final Workflow Outputs")
                
                results_selector = gr.Dropdown(
                    choices=[(p.name, p.id) for p in code_gen_workflow],
                    label="Select Process Results"
                )
                
                results_display = gr.JSON(label="Process Results")
                
                with gr.Row():
                    export_json_btn = gr.Button("📥 Export as JSON")
                    export_markdown_btn = gr.Button("📝 Export as Markdown")
                
                export_output = gr.File(label="Download Results")
        
        # ========== EVENT HANDLERS ==========
        
        def start_workflow(requirements):
            """Start workflow with initial input"""
            orchestrator.state.started_at = datetime.now()
            result = orchestrator.execute_process(
                "requirements_analyzer",
                {"requirements": requirements}
            )
            
            log = f"[{datetime.now().strftime('%H:%M:%S')}] Workflow started\n"
            log += f"[{datetime.now().strftime('%H:%M:%S')}] Executed: {code_gen_workflow[0].name}\n"
            
            return (
                orchestrator.get_workflow_status(),
                log,
                json.dumps(result, indent=2)
            )
        
        def execute_single_process(process_id, user_input):
            """Execute a single process manually"""
            result = orchestrator.execute_process(process_id, {"input": user_input})
            context = orchestrator._build_context(process_id)
            
            return (
                result.get("output", str(result)),
                context,
                orchestrator.get_workflow_status()
            )
        
        def auto_advance_workflow():
            """Automatically execute next pending process"""
            next_proc = orchestrator.get_next_process()
            if not next_proc:
                return "No pending processes", "", orchestrator.get_workflow_status()
            
            # Use output from previous process as input
            prev_idx = orchestrator.process_order.index(next_proc) - 1
            if prev_idx >= 0:
                prev_proc = orchestrator.process_order[prev_idx]
                prev_output = orchestrator.state.process_outputs.get(prev_proc, {})
                input_data = {"input": prev_output.get("output", "")}
            else:
                input_data = {"input": ""}
            
            result = orchestrator.execute_process(next_proc, input_data)
            
            return (
                result.get("output", str(result)),
                orchestrator._build_context(next_proc),
                orchestrator.get_workflow_status()
            )
        
        def get_approval_queue():
            """Get first process waiting for approval"""
            for proc_id, status in orchestrator.state.process_status.items():
                if status == ProcessStatus.WAITING_APPROVAL:
                    proc = orchestrator.processes[proc_id]
                    output = orchestrator.state.process_outputs[proc_id]
                    return (
                        f"{proc.name} ({proc_id})",
                        output.get("output", ""),
                        proc_id
                    )
            return "No processes waiting for approval", "", None
        
        def approve_process_handler(approved):
            """Handle approval/rejection"""
            for proc_id, status in orchestrator.state.process_status.items():
                if status == ProcessStatus.WAITING_APPROVAL:
                    result = orchestrator.approve_process(proc_id, approved)
                    return result, orchestrator.get_workflow_status()
            return "No process to approve", orchestrator.get_workflow_status()
        
        def get_process_results(process_id):
            """Get results for a specific process"""
            if process_id in orchestrator.state.process_outputs:
                return orchestrator.state.process_outputs[process_id]
            return {"error": "No results for this process yet"}
        
        def export_as_json():
            """Export all results as JSON"""
            export_data = {
                "workflow_id": orchestrator.state.workflow_id,
                "started_at": orchestrator.state.started_at.isoformat() if orchestrator.state.started_at else None,
                "processes": orchestrator.state.process_outputs,
                "history": orchestrator.state.history
            }
            
            filename = f"workflow_{orchestrator.state.workflow_id}.json"
            with open(filename, "w") as f:
                json.dump(export_data, f, indent=2)
            
            return filename
        
        # Wire up events
        start_btn.click(
            start_workflow,
            inputs=[initial_requirements],
            outputs=[status_display, workflow_log, process_output]
        )
        
        execute_btn.click(
            execute_single_process,
            inputs=[process_selector, process_input],
            outputs=[process_output, process_context, status_display]
        )
        
        auto_advance_btn.click(
            auto_advance_workflow,
            outputs=[process_output, process_context, status_display]
        )
        
        refresh_status_btn.click(
            lambda: orchestrator.get_workflow_status(),
            outputs=[status_display]
        )
        
        approve_btn.click(
            lambda: approve_process_handler(True),
            outputs=[approval_result, status_display]
        )
        
        reject_btn.click(
            lambda: approve_process_handler(False),
            outputs=[approval_result, status_display]
        )
        
        results_selector.change(
            get_process_results,
            inputs=[results_selector],
            outputs=[results_display]
        )
        
        export_json_btn.click(
            export_as_json,
            outputs=[export_output]
        )
        
        # Auto-refresh approval queue on tab switch
        tabs.change(
            get_approval_queue,
            outputs=[approval_process_display, approval_output_display]
        )
    
    return demo

# ============================================================================
# LAUNCH
# ============================================================================

if __name__ == "__main__":
    demo = create_workflow_ui()
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )