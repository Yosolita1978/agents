import panel as pn
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import threading
import json
import io
from .callbacks import get_panel_callback_handler

class SustainabilityPanelApp:
    """Main Panel application for sustainability training"""
    
    def __init__(self):
        # Initialize Panel
        pn.extension('tabulator', 'modal')
        
        # Create main components
        self.chat_interface = pn.chat.ChatInterface(
            callback=self.on_user_message,
            show_send=True,
            show_rerun=False,
            height=600,
            sizing_mode="stretch_width"
        )
        
        # Session management
        self.current_session_id: Optional[str] = None
        self.session_active: bool = False
        self.latest_results: Optional[Any] = None
        
        # Connect callback handler to chat
        self.callback_handler = get_panel_callback_handler()
        self.callback_handler.register_chat_interface(self.chat_interface)
        
        # Create input forms
        self.setup_input_forms()
        
        # Create layout
        self.setup_layout()
    
    def setup_input_forms(self):
        """Setup user input forms"""
        self.industry_input = pn.widgets.TextInput(
            name="Industry", 
            value="Marketing Agency",
            placeholder="e.g., Marketing Agency, Tech Startup, Fashion Brand"
        )
        
        self.regulations_input = pn.widgets.TextInput(
            name="Regional Regulations",
            value="EU Green Claims Directive, CSRD",
            placeholder="e.g., EU Green Claims Directive, FTC Guidelines"
        )
        
        self.focus_areas = pn.widgets.MultiChoice(
            name="Training Focus Areas",
            value=["Greenwashing Prevention", "Compliance Messaging"],
            options=[
                "Greenwashing Prevention",
                "Compliance Messaging", 
                "Best Practices",
                "Risk Assessment",
                "Team Training",
                "Client Communication"
            ]
        )
        
        self.difficulty_level = pn.widgets.Select(
            name="Difficulty Level",
            value="Intermediate",
            options=["Beginner", "Intermediate", "Advanced"]
        )
        
        self.start_button = pn.widgets.Button(
            name="🚀 Start Training Session",
            button_type="primary",
            sizing_mode="stretch_width"
        )
        self.start_button.on_click(self.start_training_session)
        
        # Download buttons (initially hidden)
        self.download_md_button = pn.widgets.Button(
            name="📄 Download Report (Markdown)",
            button_type="success",
            sizing_mode="stretch_width",
            visible=False
        )
        self.download_md_button.on_click(self.download_markdown_report)
        
        self.download_pdf_button = pn.widgets.Button(
            name="📑 Download Report (PDF)",
            button_type="success", 
            sizing_mode="stretch_width",
            visible=False
        )
        self.download_pdf_button.on_click(self.download_pdf_report)
    
    def setup_layout(self):
        """Setup the main layout"""
        # Sidebar with inputs
        sidebar = pn.Column(
            "## 🌱 Sustainability Training Setup",
            self.industry_input,
            self.regulations_input,
            self.focus_areas,
            self.difficulty_level,
            "---",
            self.start_button,
            "---",
            "### 📥 Download Results",
            self.download_md_button,
            self.download_pdf_button,
            "---",
            "### 📋 Instructions",
            """
            1. **Configure** your training parameters
            2. **Click** 'Start Training Session'
            3. **Watch** AI agents work in real-time
            4. **Download** results when complete
            """,
            "---",
            "### 🎯 About This Training",
            """
            This AI-powered training creates:
            - Realistic business scenarios
            - Common greenwashing examples
            - Compliant message alternatives
            - Knowledge assessment
            """,
            width=350,
            margin=(10, 10)
        )
        
        # Main content area
        main_content = pn.Column(
            "# 🤖 Sustainability Messaging Training",
            "Watch your AI agents work together to create comprehensive sustainability training content.",
            self.chat_interface,
            sizing_mode="stretch_both"
        )
        
        # Simple Row layout
        self.layout = pn.Row(
            sidebar,
            main_content,
            sizing_mode="stretch_width",
            height=800
        )
    
    def on_user_message(self, contents: str, user: str, instance):
        """Handle user messages in chat"""
        if not self.session_active:
            response = "Please start a training session first using the 'Start Training Session' button."
            self.chat_interface.send(response, user="Assistant", respond=False)
            return
        
        # Handle user input during active session
        response = f"Received your input: {contents}"
        self.chat_interface.send(response, user="Assistant", respond=False)
    
    def start_training_session(self, event):
        """Start a new training session"""
        if self.session_active:
            self.chat_interface.send("Session already active! Please wait for the current session to complete.", user="System", respond=False)
            return
        
        # Hide download buttons during training
        self.download_md_button.visible = False
        self.download_pdf_button.visible = False
        
        # Generate session ID
        self.current_session_id = f"TRAIN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_active = True
        
        # Disable start button during session
        self.start_button.disabled = True
        self.start_button.name = "⏳ Training in Progress..."
        
        # Prepare session info
        session_info = {
            'session_id': self.current_session_id,
            'user_industry': self.industry_input.value,
            'regional_regulations': self.regulations_input.value,
            'focus_areas': self.focus_areas.value,
            'difficulty_level': self.difficulty_level.value,
            'current_year': str(datetime.now().year)
        }
        
        # Notify callback handler
        self.callback_handler.on_session_start(session_info)
        
        # Start CrewAI training in background thread
        threading.Thread(
            target=self.run_crewai_training, 
            args=(session_info,),
            daemon=True
        ).start()
    
    def run_crewai_training(self, session_info: Dict[str, Any]):
        """Run the CrewAI training in background"""
        try:
            # Import here to avoid circular imports
            from .crew import Sustainability
            
            # Create and run crew
            sustainability_crew = Sustainability()
            result = sustainability_crew.crew().kickoff(inputs=session_info)
            
            # Store results for download
            self.latest_results = result
            
            # Display formatted results
            self.display_training_results(result)
            
            # Notify completion
            self.callback_handler.on_session_complete(result)
            
        except Exception as e:
            self.callback_handler.on_error("System", str(e))
        finally:
            # Reset session state
            self.session_active = False
            self.start_button.disabled = False
            self.start_button.name = "🚀 Start Training Session"
            
            # Show download buttons if we have results
            if self.latest_results:
                self.download_md_button.visible = True
                self.download_pdf_button.visible = True
    
    def display_training_results(self, result):
        """Display the comprehensive training results in the chat"""
        try:
            # Get the structured data
            if hasattr(result, 'tasks_output') and result.tasks_output:
                final_task = result.tasks_output[-1]
                if hasattr(final_task, 'pydantic') and final_task.pydantic:
                    data = final_task.pydantic.dict()
                    markdown_report = self.format_results_as_markdown(data)
                    
                    # Send the formatted report to chat
                    self.chat_interface.send(
                        "📊 **Training Complete! Here's your comprehensive report:**", 
                        user="System", 
                        respond=False
                    )
                    
                    # Split the markdown into chunks to avoid UI issues
                    chunks = self.split_markdown_into_chunks(markdown_report)
                    for i, chunk in enumerate(chunks):
                        self.chat_interface.send(
                            chunk, 
                            user=f"Report Part {i+1}" if len(chunks) > 1 else "Training Report", 
                            respond=False
                        )
                else:
                    # Fallback to raw result
                    self.chat_interface.send(
                        f"Training completed! Raw results:\n```\n{str(result)[:2000]}...\n```", 
                        user="System", 
                        respond=False
                    )
        except Exception as e:
            self.chat_interface.send(
                f"Training completed but couldn't format results: {str(e)}", 
                user="System", 
                respond=False
            )
    
    def format_results_as_markdown(self, data: Dict[str, Any]) -> str:
        """Format the training results as professional markdown"""
        md = f"""# 🌱 Sustainability Messaging Training Report

**Session ID:** {data.get('session_id', 'N/A')}  
**Generated:** {data.get('timestamp', datetime.now().isoformat())}  
**Learner:** {data.get('learner_profile', 'Marketing Professional')}

---

## 📋 Executive Summary

This comprehensive training session analyzed sustainability messaging for the **{data.get('scenario', {}).get('industry', 'target industry')}** sector, identifying common greenwashing patterns and providing compliant alternatives in accordance with **{data.get('scenario', {}).get('regulatory_context', 'current regulations')}**.

---

## 🏢 Business Scenario

### Company Profile
**Name:** {data.get('scenario', {}).get('company_name', 'N/A')}  
**Industry:** {data.get('scenario', {}).get('industry', 'N/A')}  
**Size:** {data.get('scenario', {}).get('company_size', 'N/A')}  
**Location:** {data.get('scenario', {}).get('location', 'N/A')}

### Services & Audience
**Services:** {data.get('scenario', {}).get('product_service', 'N/A')}

**Target Audience:** {data.get('scenario', {}).get('target_audience', 'N/A')}

### Marketing Objectives
"""
        
        # Add marketing objectives
        objectives = data.get('scenario', {}).get('marketing_objectives', [])
        for obj in objectives:
            md += f"- {obj}\n"
        
        md += f"""
### Sustainability Context
{data.get('scenario', {}).get('sustainability_context', 'N/A')}

---

## ⚠️ Problematic Messaging Analysis

**Common Patterns Identified:** {', '.join(data.get('problematic_analysis', {}).get('general_patterns_found', []))}

### Examples of Problematic Messages

"""
        
        # Add problematic messages
        problems = data.get('problematic_analysis', {}).get('problematic_messages', [])
        for problem in problems:
            md += f"""
#### ❌ Example {problem.get('id', 'N/A')}
**Problematic Message:** "{problem.get('message', 'N/A')}"

**Issues Identified:**
{self.format_list(problem.get('problems_identified', []))}

**Regulatory Violations:**
{self.format_list(problem.get('regulatory_violations', []))}

**Why This Is Problematic:**
{problem.get('why_problematic', 'N/A')}

**Potential Consequences:**
{self.format_list(problem.get('potential_consequences', []))}

---
"""
        
        md += """
## ✅ Best Practice Corrections

### Corrected Messages
"""
        
        # Add corrected messages
        corrections = data.get('best_practices', {}).get('corrected_messages', [])
        for correction in corrections:
            md += f"""
#### ✅ Correction for Example {correction.get('original_message_id', 'N/A')}
**Improved Message:** "{correction.get('corrected_message', 'N/A')}"

**Changes Made:**
{self.format_list(correction.get('changes_made', []))}

**Compliance Notes:** {correction.get('compliance_notes', 'N/A')}

**Best Practices Applied:**
{self.format_list(correction.get('best_practices_applied', []))}

---
"""
        
        md += """
### General Guidelines
"""
        guidelines = data.get('best_practices', {}).get('general_guidelines', [])
        for guideline in guidelines:
            md += f"- {guideline}\n"
        
        md += """
### Key Principles
"""
        principles = data.get('best_practices', {}).get('key_principles', [])
        for principle in principles:
            md += f"- {principle}\n"
        
        md += """
---

## 📝 Knowledge Assessment

"""
        # Add assessment questions
        questions = data.get('assessment_questions', [])
        for q in questions:
            md += f"""
### Question {q.get('id', 'N/A')} ({q.get('difficulty_level', 'N/A').title()})
**{q.get('question', 'N/A')}**

"""
            if q.get('options'):
                for option in q.get('options', []):
                    md += f"- {option}\n"
            
            md += f"""
**Correct Answer:** {q.get('correct_answer', 'N/A')}

**Explanation:** {q.get('explanation', 'N/A')}

---
"""
        
        md += """
## 🎯 Personalized Feedback

### Role-Specific Tips (Marketing Director)
"""
        tips = data.get('personalized_feedback', {}).get('role_specific_tips', [])
        for tip in tips:
            md += f"- {tip}\n"
        
        md += """
### Team Training Recommendations
"""
        recommendations = data.get('personalized_feedback', {}).get('team_training_recommendations', [])
        for rec in recommendations:
            md += f"- {rec}\n"
        
        md += """
### Implementation Strategies
"""
        strategies = data.get('personalized_feedback', {}).get('implementation_strategies', [])
        for strategy in strategies:
            md += f"- {strategy}\n"
        
        md += """
### Next Steps
"""
        next_steps = data.get('personalized_feedback', {}).get('next_steps', [])
        for step in next_steps:
            md += f"- {step}\n"
        
        md += """
---

## 🔑 Key Takeaways

"""
        takeaways = data.get('key_takeaways', [])
        for takeaway in takeaways:
            md += f"- {takeaway}\n"
        
        md += """
---

## ✅ Compliance Checklist

"""
        checklist = data.get('compliance_checklist', [])
        for item in checklist:
            md += f"- [ ] {item}\n"
        
        md += f"""
---

## 📚 Additional Resources

### Research Sources Used
"""
        sources = data.get('best_practices', {}).get('research_sources', [])
        for source in sources:
            md += f"- {source}\n"
        
        md += f"""
---

*Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')} using AI-powered sustainability training agents.*
"""
        
        return md
    
    def format_list(self, items):
        """Format a list of items as markdown"""
        if not items:
            return "- None specified\n"
        return "\n".join([f"- {item}" for item in items]) + "\n"
    
    def split_markdown_into_chunks(self, markdown, max_length=8000):
        """Split markdown into smaller chunks for display"""
        if len(markdown) <= max_length:
            return [markdown]
        
        chunks = []
        lines = markdown.split('\n')
        current_chunk = ""
        
        for line in lines:
            if len(current_chunk + line + '\n') > max_length and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def download_markdown_report(self, event):
        """Download the training report as markdown"""
        if not self.latest_results:
            self.chat_interface.send("No results available for download.", user="System", respond=False)
            return
        
        try:
            # Get the structured data
            if hasattr(self.latest_results, 'tasks_output') and self.latest_results.tasks_output:
                final_task = self.latest_results.tasks_output[-1]
                if hasattr(final_task, 'pydantic') and final_task.pydantic:
                    data = final_task.pydantic.dict()
                    markdown_content = self.format_results_as_markdown(data)
                    
                    # Create download
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"sustainability_training_report_{timestamp}.md"
                    
                    # Create a file download
                    file_download = pn.pane.HTML(f"""
                    <a href="data:text/markdown;charset=utf-8,{markdown_content.replace('#', '%23')}" 
                       download="{filename}" 
                       style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                       📄 Download {filename}
                    </a>
                    """)
                    
                    self.chat_interface.send("📄 Markdown report ready for download!", user="System", respond=False)
                    
        except Exception as e:
            self.chat_interface.send(f"Error preparing download: {str(e)}", user="System", respond=False)
    
    def download_pdf_report(self, event):
        """Download the training report as PDF"""
        # For now, show instructions for PDF conversion
        self.chat_interface.send(
            """📑 **PDF Download Instructions:**
            
1. First download the Markdown report using the button above
2. Use any of these methods to convert to PDF:
   - **Online:** Upload the .md file to pandoc.org/try or markdown-pdf.com
   - **Local:** Install pandoc and run: `pandoc report.md -o report.pdf`
   - **VS Code:** Install "Markdown PDF" extension and export

Full PDF generation will be added in a future update!""", 
            user="System", 
            respond=False
        )
        
    def servable(self):
        """Return the servable Panel application"""
        return self.layout

def create_sustainability_app():
    """Factory function to create the Panel app"""
    return SustainabilityPanelApp()