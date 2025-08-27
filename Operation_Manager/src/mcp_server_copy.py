# from fastmcp import FastMCP
# from src.services import get_machine_service, get_project_service, get_machine_service_tool
# mcp = FastMCP(name="machine_service")

# PROMPT_INJECTION = """


# """


# @mcp.prompt(
#     name="auto_expand_context",
#     description= ""
# )
# def auto_expand_context(user_request: str) -> str:
#     return PROMPT_INJECTION + "\n\n[사용자 요청]\n" + user_request


# async def setup_resources():
#     @mcp.resource(uri="data://torus_md", mime_type="text/markdown", description="TORUS 데이터 모델 문서")
#     def torus_md_res() -> str:
#         with open("torus_markdown_short.md", encoding="utf-8") as f:
#             return f.read()

# async def setup_tools():
#     project_service = await get_project_service()
#     machine_service = await get_machine_service_tool()

#     mcp.tool(machine_service.get_machine_list)
#     mcp.tool(machine_service.upload_torus_file)

#     mcp.tool(machine_service.get_machine_data)
#     mcp.tool(machine_service.get_channel_data)
#     mcp.tool(machine_service.get_axis_data)
#     mcp.tool(machine_service.get_spindle_data)
#     mcp.tool(machine_service.get_feed_data)
#     mcp.tool(machine_service.get_workStatus_data)
#     mcp.tool(machine_service.get_activeTool_data)
#     mcp.tool(machine_service.get_currentProgram_data)
#     mcp.tool(machine_service.get_workOffset_data)
#     mcp.tool(machine_service.get_alarmORVariable_data)
#     mcp.tool(machine_service.get_plc_data)
#     mcp.tool(machine_service.get_toolArea_data)
#     mcp.tool(machine_service.get_buffer_data)



#     mcp.tool(project_service.get_project_list)
#     mcp.tool(project_service.extract_workplan_and_nc)
#     mcp.tool(project_service.get_nc_code)
#     mcp.tool(project_service.update_nc_code)
#     mcp.tool(project_service.get_product_logs_by_project_id)
#     mcp.tool(project_service.get_machine_status_info)
    
# # import asyncio
# # asyncio.run(setup_tools()) 
# # mcp.run(transport="sse", port=8050, host="0.0.0.0")

# async def run_mcp():
#     await setup_resources()
#     await setup_tools()            
#     await mcp.run_async(transport="sse", port=8050, host="0.0.0.0")

# import anyio
# anyio.run(run_mcp)