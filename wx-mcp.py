# FastMCP是一个高层的API，能快速实现MCP
from mcp.server.fastmcp import FastMCP
from wxauto import WeChat
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
# 初始化 MCP 服务器，名字随意
mcp = FastMCP("wx-mcp")
wx = WeChat()


@mcp.tool(name="send_message", description="send message to someone")
def send_message(msg: str, to: str, at: str | list[str] = None):
    try:
        wx.SendMsg(msg, to, clear="True", at=at)
    except Exception as e:
        return f"发送消息失败: {str(e)}"
    return "Message sent successfully"


import time
# 通过 @mcp.tool() 装饰器注册为 MCP 服务器的工具，使其能够被客户端调用。
# 函数会转化成json schema的形式的说明。使用client调用server时，会把json schema添加到每次的对话中，
# 这样client就可以识别外部工具，server则作为client进程的子进程运行
@mcp.tool(name="auto_message_reply", description="auto reply friend\'s message")
def auto_message_reply():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))
    while True:
        try:
            new_msgs = wx.GetNextNewMessage()
            for key, value in new_msgs.items():
                if key == "居丽叶":
                    for new_msg in value:
                        if new_msg[0] == "居丽叶":
                            messages = [{"role": "system", "content": "请用 **1句短回复** 回应女友消息，要求：\
                                        1. 极简结构：直接回答+情感绑定，不加解释或复杂逻辑\
                                        2. 核心词复用：提取她消息中的关键词（如'小猪猪'点赞'）构建回应\
                                        3. 隐晦宠溺：'你的'+昵称（如你的小猪猪/你的指挥官）替代'我'，强化归属感\
                                         "}, {"role": "user", "content": new_msg[1]}]
                            response = client.chat.completions.create(
                                model=os.getenv("MODEL"),
                                messages=messages,
                            )
                            wx.SendMsg(response.choices[0].message.content, key, clear="True")
            # return "执行成功"
        except:
            pass
        finally:
            time.sleep(5) # 每隔 5 秒检查一次新消息
# auto_message_reply()
if __name__ == "__main__":
     # 以标准 I/O 方式运行 MCP 服务器，也就是本地进程间通信IPC，服务器作为子进程运行，并通过标准输入输出(stdin/stdout)进行数据交换
    mcp.run()




