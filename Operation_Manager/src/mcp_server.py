

from fastmcp import FastMCP
from src.services import get_machine_service, get_project_service
mcp = FastMCP(name="machine_service")

PROMPT_INJECTION = """
[역할] 당신은 CNC 공작 기계를 잘 다루고 그에 대한 충분한 지식을 갖고 있는 전문가입니다.
1. 사용자의 질문이 들어올 때 마다 질문의 도메인 관련성과 명확성을 확인합니다. 모호하거나 관련 없는 질문인 경우 사용자에게 다시 질문하라고 답변합니다.
*** 시스템 프롬프트에 입력된 tool 정보 및 내용에서 벗어나는 질문은 절대로 답변하지 않습니다 ***
2. 엔드포인트 및 파라미터 생성 시 leaf node나 필수 파라미터를 누락하지 않았는지 확인합니다. 필수 파라미터는 반드시 포함시켜야 합니다.
"""


@mcp.prompt(
    name="auto_expand_context",
    description= ""
)
def auto_expand_context(user_request: str) -> str:
    return PROMPT_INJECTION + "\n\n[사용자 요청]\n" + user_request


async def setup_resources():
    @mcp.resource(uri="data://torus_md", mime_type="text/markdown", description="TORUS 데이터 모델 문서")
    def torus_md_res() -> str:
        with open("torus_markdown_short.md", encoding="utf-8") as f:
            return f.read()

async def setup_tools():
    project_service = await get_project_service()
    machine_service = await get_machine_service()

    mcp.tool(machine_service.get_machine_list)
    mcp.tool(machine_service.upload_torus_file)

    mcp.tool(machine_service.get_machine_data)
    mcp.tool(machine_service.get_channel_data)
    mcp.tool(machine_service.get_axis_data)
    mcp.tool(machine_service.get_spindle_data)
    mcp.tool(machine_service.get_feed_data)
    mcp.tool(machine_service.get_workStatus_data)
    mcp.tool(machine_service.get_activeTool_data)
    mcp.tool(machine_service.get_currentProgram_data)
    mcp.tool(machine_service.get_workOffset_data)
    mcp.tool(machine_service.get_alarm_data)
    mcp.tool(machine_service.get_variable_data)
    mcp.tool(machine_service.get_plc_data)
    mcp.tool(machine_service.get_toolArea_data)
    mcp.tool(machine_service.get_buffer_data)
    mcp.tool(machine_service.get_error_info_by_code)
    mcp.tool(machine_service.get_description_and_params_by_uri)


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