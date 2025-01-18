from typing import Dict, List, Callable
from langgraph.graph import StateGraph, END
from dataclasses import dataclass
from langgraph.prebuilt.tool_executor import ToolExecutor
from src.supervisor import supervisor_node, AgentSupervisor

@dataclass
class WorkflowState:
    messages: List[Dict]
    current_agent: str
    context: Dict = None

class WorkflowManager:
    def __init__(self, config: dict):
        self.workflow = StateGraph(WorkflowState)
        self.supervisor = AgentSupervisor(config)
        
    def create_workflow(self) -> StateGraph:
        # Add supervisor node
        self.workflow.add_node("supervisor", supervisor_node)
        
        # Add agent nodes
        for agent_name in ["course_guidance", "rag", "academic_integrity", "study_plan"]:
            self.workflow.add_node(
                agent_name, 
                self._create_agent_node(agent_name)
            )
        
        # Set entry point
        self.workflow.set_entry_point("supervisor")
        
        # Add edges from supervisor to agents
        for agent_name in ["course_guidance", "rag", "academic_integrity", "study_plan"]:
            self.workflow.add_edge("supervisor", agent_name)
            # Add edge back to supervisor
            self.workflow.add_edge(agent_name, "supervisor")
        
        # Add edge to END
        self.workflow.add_edge("supervisor", END)
        
        return self.workflow.compile()
    
    def _create_agent_node(self, agent_name: str) -> Callable:
        def run_agent(state: WorkflowState):
            agent = self.supervisor.agents[agent_name]
            last_message = state.messages[-1]["content"]
            response = agent.process_query(last_message)
            
            state.messages.append({
                "role": "assistant",
                "content": response,
                "agent": agent_name
            })
            return state
        return run_agent