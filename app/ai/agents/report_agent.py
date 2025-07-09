import base64

import requests
from agents import Agent, RunContextWrapper, Runner, function_tool

from app.ai.agents.law_agent import law_agent
from app.ai.contexts.research_scope_context import ResearchScopeContext
from app.ai.prompts.agents_prompts import REPORT_AGENT_PROMPT
from app.config.core import API_URL
from app.models.research_model import Research
from app.models.research_trace_model import ResearchTrace
from app.utils.agent_utils import PrintHooks
from app.utils.research_utils import research_event

report_agent = Agent[ResearchScopeContext](
    name="report_agent",
    instructions=REPORT_AGENT_PROMPT,
    hooks=PrintHooks("Report Agent"),
    tools=[
        law_agent.as_tool(
            tool_name="law_agent",
            tool_description="A tool to lookup Slovak laws and legal provisions.",
        ),
    ],
    model="o4-mini"
)


@function_tool
async def spawn_report_agent(context: RunContextWrapper[ResearchScopeContext], instructions: str) -> str:
    """
    Spawn a report agent that can write a report based on the research results.
    """
    research_event(context.context.research_id, "writing_report")
    
    research_results = ResearchTrace.find({'research_id': context.context.research_id})
    research_results = [
        {
            'metadata': doc.get('metadata'),
            'pdf_file_name': doc.get('pdf_file_name'),
        }
        for doc in research_results
    ] 
    
    input_data = []
    for doc in research_results:
        response = requests.get(
            f"{API_URL}/pdf/{doc.get('pdf_file_name')}",
            proxies={'http': None, 'https': None}, 
            timeout=30
        )
        response.raise_for_status()
        pdf_content = response.content
        pdf_content = base64.b64encode(pdf_content).decode("utf-8")
        filename = doc.get('pdf_file_name')
        
        input_data.append({
            "type": "input_file",
            "filename": filename,
            "file_data": f"data:application/pdf;base64,{pdf_content}",
        })
        
    append_input_data = input_data if input_data else [
        {
            "type": "input_text",
            "text": "No relevant results found. Respond with error message."
        }
    ]
        
    res = await Runner.run(
        starting_agent=report_agent,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": context.context.model_dump_json(exclude={'research_id'})
                    }
                ]
            },
            {
                "role": "user",
                "content": append_input_data
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": instructions
                    }
                ]
            }
        ],
        context=context.context,
        max_turns=20,
    )
    
    # Set report as research result
    if research := Research.find_by_id(context.context.research_id):
        research.update({
            'report': res.final_output
        })
    
    return res.final_output