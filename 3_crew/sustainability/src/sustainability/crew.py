from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, SerperDevTool
from pydantic import BaseModel, Field
from typing import List
import os
from datetime import datetime

# Add Panel callback imports
from .callbacks import print_task_output, get_panel_callback_handler

# Pydantic Models for Structured Outputs
class SustainabilityScenario(BaseModel):
    """A realistic business scenario for sustainability messaging training"""
    company_name: str = Field(description="Company name")
    industry: str = Field(description="Industry sector")
    company_size: str = Field(description="Company size (startup, SME, large corporation)")
    location: str = Field(description="Company location/market")
    product_service: str = Field(description="Main product or service offered")
    target_audience: str = Field(description="Primary target audience for marketing")
    marketing_objectives: List[str] = Field(description="Key marketing objectives")
    sustainability_context: str = Field(description="Current sustainability challenges and context")
    preliminary_claims: List[str] = Field(description="Initial sustainability claims the company wants to make")
    regulatory_context: str = Field(description="Relevant regulatory requirements (EU directives, etc.)")
    market_research_sources: List[str] = Field(description="Sources used to create this scenario")

class ProblematicMessage(BaseModel):
    """A problematic sustainability message with detailed analysis"""
    id: str = Field(description="Unique identifier for this message")
    message: str = Field(description="The problematic sustainability message")
    problems_identified: List[str] = Field(description="Specific problems with this message")
    regulatory_violations: List[str] = Field(description="Specific regulations this violates")
    greenwashing_patterns: List[str] = Field(description="Greenwashing patterns demonstrated")
    real_world_examples: List[str] = Field(description="Real companies/cases that made similar mistakes")
    why_problematic: str = Field(description="Detailed explanation of why this message is problematic")
    potential_consequences: List[str] = Field(description="Potential legal/reputational consequences")

class ProblematicMessageAnalysis(BaseModel):
    """Complete analysis of problematic sustainability messages"""
    scenario_reference: str = Field(description="Reference to the business scenario")
    problematic_messages: List[ProblematicMessage] = Field(description="List of problematic messages with analysis")
    general_patterns_found: List[str] = Field(description="Common greenwashing patterns identified")
    regulatory_landscape: str = Field(description="Current regulatory landscape overview")
    research_sources: List[str] = Field(description="Sources used for real-world examples")

class CorrectedMessage(BaseModel):
    """A corrected sustainability message with best practices"""
    original_message_id: str = Field(description="Reference to the original problematic message")
    corrected_message: str = Field(description="The improved, compliant message")
    changes_made: List[str] = Field(description="Specific changes made to fix the problems")
    compliance_notes: str = Field(description="How this message ensures regulatory compliance")
    best_practices_applied: List[str] = Field(description="Best practices applied in the correction")
    real_world_examples: List[str] = Field(description="Companies that use similar effective messaging")
    effectiveness_rationale: str = Field(description="Why this corrected message is effective")

class BestPracticeGuidance(BaseModel):
    """Complete best practice guidance for sustainability messaging"""
    scenario_reference: str = Field(description="Reference to the business scenario")
    corrected_messages: List[CorrectedMessage] = Field(description="List of corrected messages")
    general_guidelines: List[str] = Field(description="General guidelines for compliant messaging")
    key_principles: List[str] = Field(description="Key principles for effective sustainability communication")
    regulatory_compliance_tips: List[str] = Field(description="Tips for ensuring regulatory compliance")
    industry_specific_advice: str = Field(description="Advice specific to the industry in the scenario")
    research_sources: List[str] = Field(description="Sources for best practices and examples")

class AssessmentQuestion(BaseModel):
    """A training assessment question"""
    id: str = Field(description="Question identifier")
    type: str = Field(description="Question type (multiple_choice, scenario_analysis, identification)")
    question: str = Field(description="The assessment question")
    options: List[str] = Field(description="Answer options (for multiple choice questions)")
    correct_answer: str = Field(description="The correct answer")
    explanation: str = Field(description="Detailed explanation of the correct answer")
    difficulty_level: str = Field(description="beginner, intermediate, or advanced")
    learning_objective: str = Field(description="What this question tests")

class PersonalizedFeedback(BaseModel):
    """Personalized feedback for the learner"""
    role_specific_tips: List[str] = Field(description="Tips specific to Marketing Director role")
    team_training_recommendations: List[str] = Field(description="Recommendations for training the team")
    implementation_strategies: List[str] = Field(description="Strategies for implementing learnings")
    next_steps: List[str] = Field(description="Recommended next steps for continued learning")
    additional_resources: List[str] = Field(description="Additional resources for further learning")

class ComprehensiveTrainingReport(BaseModel):
    """Complete sustainability training session report"""
    session_id: str = Field(description="Training session identifier")
    timestamp: str = Field(description="Session timestamp")
    learner_profile: str = Field(description="Learner profile summary")
    scenario: SustainabilityScenario = Field(description="Business scenario used in training")
    problematic_analysis: ProblematicMessageAnalysis = Field(description="Analysis of problematic messages")
    best_practices: BestPracticeGuidance = Field(description="Best practice guidance and corrections")
    assessment_questions: List[AssessmentQuestion] = Field(description="Assessment questions for knowledge testing")
    personalized_feedback: PersonalizedFeedback = Field(description="Personalized feedback and recommendations")
    key_takeaways: List[str] = Field(description="Key takeaways from the training session")
    compliance_checklist: List[str] = Field(description="Checklist for ensuring message compliance")

@CrewBase
class Sustainability():
    """Sustainability Messaging Training Crew"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self) -> None:
        self.user_preferences = self._load_user_preferences()
        self._ensure_output_directory()
        # Initialize search tool
        self.search_tool = SerperDevTool()
        
    def _load_user_preferences(self):
        """Load user preferences from knowledge folder"""
        try:
            with open('knowledge/user_preference.txt', 'r') as file:
                return file.read()
        except FileNotFoundError:
            return "No user preferences found"
    
    def _ensure_output_directory(self):
        """Create outputs directory if it doesn't exist"""
        if not os.path.exists('outputs'):
            os.makedirs('outputs')
    
    @agent
    def scenario_builder(self) -> Agent:
        return Agent(
            config=self.agents_config['scenario_builder'],
            tools=[
                FileReadTool(file_path='knowledge/user_preference.txt'),
                self.search_tool
            ],
            verbose=True
        )
    
    @agent
    def mistake_illustrator(self) -> Agent:
        return Agent(
            config=self.agents_config['mistake_illustrator'],
            tools=[self.search_tool],
            verbose=True
        )
    
    @agent
    def best_practice_coach(self) -> Agent:
        return Agent(
            config=self.agents_config['best_practice_coach'],
            tools=[self.search_tool],
            verbose=True
        )
    
    @agent
    def assessment_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['assessment_agent'],
            tools=[self.search_tool],
            verbose=True
        )
    
    @task
    def scenario_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['scenario_creation_task'],
            agent=self.scenario_builder(),
            output_pydantic=SustainabilityScenario,
            callback=print_task_output
        )
    
    @task
    def mistake_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['mistake_generation_task'],
            agent=self.mistake_illustrator(),
            output_pydantic=ProblematicMessageAnalysis,
            callback=print_task_output
        )
    
    @task
    def best_practice_transformation_task(self) -> Task:
        return Task(
            config=self.tasks_config['best_practice_transformation_task'],
            agent=self.best_practice_coach(),
            output_pydantic=BestPracticeGuidance,
            callback=print_task_output
        )
    
    @task
    def assessment_and_feedback_task(self) -> Task:
        return Task(
            config=self.tasks_config['assessment_and_feedback_task'],
            agent=self.assessment_agent(),
            output_pydantic=ComprehensiveTrainingReport,
            output_file='outputs/sustainability_training_session.json',
            callback=print_task_output
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Sustainability Training crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,  # Disabled to avoid ChromaDB warnings for MVP
            output_log_file="outputs/training_session.log"
        )