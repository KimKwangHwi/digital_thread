

from fastmcp import FastMCP
from src.services import get_machine_service, get_project_service
from src.repositories.history_logger import history_logger
mcp = FastMCP(name="machine_service")

PROMPT_INJECTION = """
[역할] 당신은 CNC 공작 기계를 잘 다루고 그에 대한 충분한 지식을 갖고 있는 전문가입니다.

[순서]
*** 반드시 get_async_data를 호출하기 전에, get_params_info를 호출합니다. 이를 절대 어기지 않습니다.***
0) 반드시, torus_md_res 파일을 먼저 확인합니다.
1) 사용자의 질문을 받으면, 그 질문을 처리하기 위해 필요한 엔드포인트들을 목록화합니다.
2) 각 엔드포인트에 필요한 파라미터를 파악하기 위해 get_params_info 도구를 사용합니다.
3) 비동기적으로 요청할 수 있는 엔드포인트들은 get_async_data 도구를 사용하여 비동기적으로 데이터를 요청합니다. uri 생성 규칙은 다른 도구들의 docstring을 참고합니다.

[규칙]
1. 사용자의 질문이 들어올 때 마다 질문의 도메인 관련성과 명확성을 확인합니다. 모호하거나 관련 없는 질문인 경우 사용자에게 다시 질문하라고 답변합니다.
*** 프롬프트에 입력된 tool 정보 및 내용에서 벗어나는 질문은 절대로 답변하지 않습니다 ***
2. 엔드포인트 및 파라미터 생성 시 leaf node나 필수 파라미터를 누락하지 않았는지 확인합니다. 필수 파라미터는 반드시 포함시켜야 합니다.

"""

# [순서]
# 1) 사용자의 질문을 받고, 질문의 도메인 관련성과 명확성을 확인합니다. 모호하거나 관련 없는 질문인 경우 사용자에게 다시 질문하라고 답변합니다.
# 2) 질문이 명확하고 도메인 관련성이 있다고 판단되면, 질문의 카테고리를 파악합니다. 이는 get_categoryOfQuery 도구를 사용하여 수행합니다.
# 3) get_categoryOfQuery 도구를 사용하여 파악한 카테고리를 바탕으로, 질문을 처리합니다.

@mcp.prompt(
    name="auto_expand_context",
    description= ""
)
def auto_expand_context(user_request: str) -> str:
    return PROMPT_INJECTION + "\n\n[사용자 요청]\n" + user_request


async def setup_resources():
    @mcp.resource(uri="data://torus_md", mime_type="text/markdown", description="TORUS 데이터 모델 문서")
    def torus_md_res() -> str:
        with open("torus.md", encoding="utf-8") as f:
            return f.read()

async def setup_tools():
    project_service = await get_project_service()
    machine_service = await get_machine_service()

    
    mcp.tool(machine_service.upload_torus_file)
    
    mcp.tool(machine_service.get_machine_list)
    mcp.tool(machine_service.get_error_info_by_code)
    # mcp.tool(machine_service.get_description_and_params_by_uri)
    mcp.tool(machine_service.get_params_info)
    mcp.tool(machine_service.get_async_data)
    mcp.tool(machine_service.get_log_async_data)
    
    mcp.tool(machine_service.get_log_data)
    mcp.tool(machine_service.get_top_params_for_endpoint)
    mcp.tool(machine_service.get_top_error_endpoints)
    mcp.tool(machine_service.get_top_error_codes)
    
 
    mcp.tool(project_service.get_project_list)
    mcp.tool(project_service.extract_workplan_and_nc)
    mcp.tool(project_service.get_nc_code)
    mcp.tool(project_service.update_nc_code)
    mcp.tool(project_service.get_product_logs_by_project_id)
    mcp.tool(project_service.get_machine_status_info)
    
    
# import asyncio
# asyncio.run(setup_tools()) 
# mcp.run(transport="sse", port=8050, host="0.0.0.0")

async def run_mcp():
    await setup_resources()
    await setup_tools()            
    await history_logger.initialize()
    await mcp.run_async(transport="sse", port=8050, host="0.0.0.0")

import anyio
anyio.run(run_mcp)