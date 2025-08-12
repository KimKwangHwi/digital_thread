from fastmcp import FastMCP
from src.services import get_machine_service, get_project_service
mcp = FastMCP(name="machine_service")

PROMPT_INJECTION = """
[규칙]

요청 URI 생성 및 파라미터값을 전달할 때는 Torus_res 내용의 데이터 모델 구조 내에서만 탐색합니다.
MCP는 상위 루트 노드만 포함된 URI로 요청하지 않고, 항상 leaf node 경로를 통해서만 URI를 요청합니다.

[지시]
0. [지시]를 따르지 않으면 페널티를 가할 것입니다. 반드시 [지시]를 지켜야 합니다.
1. 모호하거나 추상적인 요청을 하면, 더 정확히 답변할 수 있도록 사용자의 요청과 의미적으로 일치하는 데이터 속성들을 파악하고 이를 사용자에게 제시하여 재질문합니다. 
2. 활성화된 속성에 대한 조회를 하기 전에, 반드시 속성의 활성화 여부 파악이 선행되어야 합니다. 활성화된 공구가 없는 경우, 활성화된 공구에 대한 조회는 진행하지 않습니다
4. leaf node를 누락하는 경우, 데이터 반환에 실패합니다. MCP는 항상 leaf node 경로를 통해서만 데이터를 반환합니다. URI 경로는 반드시 leaf node를 포함시켜야 합니다.
5. 조회하기 전, 그 파라미터 정보가 유효한지 먼저 검증합니다 
[예시] 7번 장비 8번 채널에 대한 질문의 경우, 실제로 7번 장비가 존재하는지, 있다면 그 장비에 8번 채널이 존재하는지 먼저 검증합니다.
6. 에러가 발생한 경우, error status에 대응하는 원인을 파악합니다. 답변 시 에러 원인도 보태서 답변합니다.
7. 구조적인 문제(사용자가 해결할 수 없는 문제)로 발생한 에러의 경우, 문제의 원인을 "구조적인 원인"으로 기억하고, 이후 "구조적인 원인"을 갖는 질문은 절대 하지 않습니다.
"""

@mcp.prompt(
    name="auto_expand_context",
    description="불명확 요청에 대해 TORUS 데이터 모델 전체 하위 항목 확장" 
)
def auto_expand_context(user_request: str) -> str:
    return PROMPT_INJECTION + "\n\n[사용자 요청]\n" + user_request


async def setup_resources():
    @mcp.resource(uri="data://torus_md", mime_type="text/markdown", description="TORUS 데이터 모델 문서")
    def torus_md_res() -> str:
        with open("torus_markdown.md", encoding="utf-8") as f:
            return f.read()

async def setup_tools():
    project_service = await get_project_service()
    machine_service = await get_machine_service()

    mcp.tool(machine_service.get_machine_list)
    mcp.tool(machine_service.get_machine_data)
    mcp.tool(machine_service.upload_torus_file)
    mcp.tool(machine_service.get_machine_status)

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
    await mcp.run_async(transport="sse", port=8050, host="0.0.0.0")

import anyio
anyio.run(run_mcp)