import base64
import os

from agents import Agent, RunContextWrapper, Runner, function_tool

from app.ai.contexts.research_scope_context import ResearchScopeContext
from app.ai.prompts.agents_prompts import PDF_READER_PROMPT
from app.utils.agent_utils import PrintHooks

pdf_reader_agent = Agent[ResearchScopeContext](
    name="pdf_reader_agent",
    instructions=PDF_READER_PROMPT,
    hooks=PrintHooks("PDF Reader Agent"),
    model="gpt-4.1"
)


@function_tool
async def spawn_pdf_reader_agent(context: RunContextWrapper[ResearchScopeContext], pdf_path: str, instructions: str) -> str:
    """
    Pass this PDF to AI agent who can answer your question about it.
    """
    with open(pdf_path, "rb") as f:
        pdf_content = f.read()
        
    pdf_content = base64.b64encode(pdf_content).decode("utf-8")
    filename = os.path.basename(pdf_path)
        
    res = await Runner.run(
        starting_agent=pdf_reader_agent,
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
                "content": [
                    {
                        "type": "input_text",
                        "text": instructions
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "filename": filename,   
                        "file_data": f"data:application/pdf;base64,{pdf_content}",
                    }
                ]
            }
        ],
        context=context.context,
    )
    
    return res.final_output