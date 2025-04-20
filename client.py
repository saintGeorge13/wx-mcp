import asyncio
import os
import json
import sys
from typing import Optional
from contextlib import AsyncExitStack

from openai import OpenAI
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 加载环境变量
load_dotenv()

class MCPClient:
    def __init__(self):
        """初始化 MCP 客户端"""
        self.exit_stack = AsyncExitStack()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("BASE_URL")
        self.model = os.getenv("MODEL")
        
        if not self.openai_api_key:
            raise ValueError("✕ 未找到 OpenAI API Key，请在 .env 文件中设置 OPENAI_API_KEY")
        
        self.client = OpenAI(api_key=self.openai_api_key, base_url=self.base_url)
        self.session: Optional[ClientSession] = None

    async def connect_to_server(self, server_script_path: str):
        """连接到 MCP 服务器并列出可用工具"""
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')

        if not (is_python or is_js):
            raise ValueError("服务器脚本必须是 .py 或 .js 文件")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        # 启动服务器连接
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        # 列出可用工具
        response = await self.session.list_tools()
        print("\n已连接到服务器，支持以下工具:", [tool.name for tool in response.tools])

    async def process_query(self, query: str) -> str:
        """使用大模型处理查询并调用工具"""
        messages = [{"role": "user", "content": query}]
        response = await self.session.list_tools()

        # 构建可用工具列表
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name, # 工具的名字
                    "description": tool.description, # 外部函数的描述
                    "parameters": tool.inputSchema  # 如果要调用这个函数，需要的json——schema说明
                }
            } for tool in response.tools
        ]

        # 第一次模型调用
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=available_tools
        )

        content = response.choices[0]
        # 如何是需要使用工具，就解析工具
        if content.finish_reason == "tool_calls":
            tool_call = content.message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # 执行工具调用
            print(f"\n\n[调用工具 {tool_name}，参数 {tool_args}]\n")
            result = await self.session.call_tool(tool_name, tool_args)
            
            # 将模型返回的调用哪个工具数据和工具执行完成后的数据都存入messages中
            messages.append(content.message.model_dump())
            messages.append({
                "role": "tool",
                "content": result.content[0].text,
                "tool_call_id": tool_call.id
            })
            # 将工具调用的结果再返回给大模型用于生产最终的结果
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        
        return content.message.content

    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\n客户端已启动！输入 'quit' 退出")

        while True:
            try:
                query = input("\n你: ").strip()
                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print(f"\nopenAI: {response}")

            except Exception as e:
                print(f"\n发生错误: {str(e)}")

    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("用法: python client.py <服务端脚本路径>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
