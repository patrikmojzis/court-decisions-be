import base64
from typing import Any

import requests
from agents import RunContextWrapper, Runner, function_tool

from app.ai.agents.pdf_analyser_agent import PDFAnalyserResult, pdf_analyser_agent
from app.ai.agents.results_analyser_agent import results_analyser_agent
from app.ai.contexts.research_scope_context import ResearchScopeContext
from app.config.core import API_URL
from app.models.keyword_model import Keyword
from app.models.research_trace_model import ResearchTrace
from app.utils.research_utils import research_event


async def analyse_pdf(context: RunContextWrapper[ResearchScopeContext], pdf_file_name: str, *, search_keyword: str = None) -> PDFAnalyserResult:
    """
    Analyse a PDF file and return a PDFAnalyserResult.
    
    Args:
        pdf_path: Local path to the PDF file
    
    Returns:
        PDFAnalyserResult
    """
    if research_trace := ResearchTrace.find_one({'research_id': context.context.research_id, 'pdf_file_name': pdf_file_name}):
        return PDFAnalyserResult(
            is_relevant=research_trace.is_relevant,
            metadata=research_trace.metadata,
            summary=research_trace.summary,
            relevant_parts=research_trace.relevant_parts,
            legal_provisions=research_trace.legal_provisions,
        )
    
    # Fetch PDF from API endpoint
    try:
        response = requests.get(
            f"{API_URL}/pdf/{pdf_file_name}",
            proxies={'http': None, 'https': None}, 
            timeout=30
        )
        response.raise_for_status()
        pdf_content = response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PDF {pdf_file_name}: {e}")
        return PDFAnalyserResult(
            is_relevant=False,
            metadata=f"Error: Could not fetch PDF {pdf_file_name}",
            summary="PDF could not be retrieved from server",
            relevant_parts=None,
            legal_provisions=None,
        )
        
    pdf_content = base64.b64encode(pdf_content).decode("utf-8")
    filename = pdf_file_name
    
    print(f"### Analyse pdf: \033[91m{pdf_file_name} {search_keyword}\033[0m\n")
    research_event(context.context.research_id, "analysing_pdf", {"pdf_file_name": pdf_file_name})
    
    res = await Runner.run(
        starting_agent=pdf_analyser_agent,
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
                        "type": "input_file",
                        "filename": filename,
                        "file_data": f"data:application/pdf;base64,{pdf_content}",
                    }
                ]
             }
        ],
        context=context.context
    )
    
    if res.final_output.is_relevant:
        ResearchTrace.create({
            'research_id': context.context.research_id, 
            'search_keyword': search_keyword,
            'metadata': res.final_output.metadata,
            'pdf_file_name': pdf_file_name,
            'summary': res.final_output.summary,
            'problem_description': context.context.problem_description,
            'question': context.context.question,
            'relevant_parts': res.final_output.relevant_parts,
            'legal_provisions': res.final_output.legal_provisions,
        })
    
    return res.final_output

async def analyse_scraping_results(context: RunContextWrapper[ResearchScopeContext], scraping_results: dict, *, search_keyword: str) -> dict[str, Any]:
    if scraping_results.get('error'):
        return f"Error: {scraping_results.get('error')}"
    
    analysis_result = {
        "search_keyword": search_keyword,
        "analysed_results": len(scraping_results.get('results', [])),
        "relevant_results": 0,
    }
    
    if scraping_results.get('results', []):
        research_event(context.context.research_id, "analysing_results")
        scraping_results_analyser_agent_res = await Runner.run(
            starting_agent=results_analyser_agent,
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
                            "text": str(scraping_results.get('results', []))    
                        }
                    ]
                }
            ],
            context=context.context
        )
        pdf_file_names = scraping_results_analyser_agent_res.final_output.pdf_file_names
    
        if pdf_file_names:
            for file_name in pdf_file_names:
                analysis_res = await analyse_pdf(context, file_name, search_keyword=search_keyword)
                if analysis_res.is_relevant:
                    analysis_result['relevant_results'] += 1
                
    # update keyword history
    if keyword := Keyword.find_one({'research_id': context.context.research_id, 'search_keyword': search_keyword}):
        keyword.update(
            {
                'analysed_results': (keyword.analysed_results or 0) + analysis_result['analysed_results'],
                'relevant_results': (keyword.relevant_results or 0) + analysis_result['relevant_results'],
            }
        )
    else:
        Keyword.create({
            'research_id': context.context.research_id,
            'search_keyword': search_keyword,
            'analysed_results': analysis_result['analysed_results'],
            'relevant_results': analysis_result['relevant_results'],
        })
        
    return analysis_result


def get_search_results(query: str, limit: int = 50) -> dict[str, Any]:
    """
    Search the vector database for court cases using the provided query.
    
    Args:
        query: Search term for court decisions
        limit: Maximum number of results to return (default 50)
    
    Returns:
        Dict containing search results and metadata
    """
    try:
        # Make API call to the vector database
        response = requests.get(
            f"{API_URL}/search",
            params={
                "query": query,
                "n_results": limit
            },
            proxies={'http': None, 'https': None},  # Disable proxy usage
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return {
            "results": [],
            "total_results": 0,
            "error": f"API request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "results": [],
            "total_results": 0,
            "error": f"Unexpected error: {str(e)}"
        }
    
@function_tool
async def search_results(context: RunContextWrapper[ResearchScopeContext], search_keyword: str, limit: int = 50) -> dict[str, Any]:
    """
    Search court cases in the vector database across all Slovak courts.
    
    Args:
        search_keyword: Search term for court decisions
        limit: Maximum number of results to analyse
    
    Returns:
        Dict with results, total count, page info, and PDFs
    """
    research_event(context.context.research_id, "searching", {"search_keyword": search_keyword, "limit": limit})
    res = get_search_results(search_keyword, limit)
    return await analyse_scraping_results(context, res, search_keyword=search_keyword)
