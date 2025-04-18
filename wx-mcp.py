from mcp.server.fastmcp import FastMCP
from wxauto import WeChat

mcp = FastMCP("wxauto_mcp")
wx = WeChat()


@mcp.tool(name="send_message", description="send message to someone")
def send_message(msg: str, to: str, at: str | list[str] = None):
    try:
        wx.SendMsg(msg, to, clear="True", at=at)
    except Exception as e:
        return f"发送消息失败: {str(e)}"
    return "Message sent successfully"

@mcp.tool(name="send_file", description="send file to someone")
def send_files(files_path:str|list,nick_name:str):
    '''发送文件(包含图片等文件)给指定的群或者个人'''
    wx.SendFiles(files_path,nick_name)
    return "ok"


@mcp.tool(name="get_all_messages", description="get all messages from someone or group")
def get_all_messages(who: str, load_more: bool = False):
    try:
        wx.ChatWith(who)
        if load_more:
            wx.LoadMoreMessage()
        msgs = wx.GetAllMessage()
        if msgs:
            return [{'sender': msg.sender, 'content': msg.content} for msg in msgs if msg.type == 'friend']
        return []
    except Exception as e:
        return f"获取消息失败: {str(e)}"


import time

@mcp.tool(name="auto_friend_accept", description="auto accept friend invitation")
def auto_friend_accept():
    while True:
        friend_list = wx.GetNewFriends()
        ac_friend = []
        for friend in friend_list:
            if "AAA" in friend.msg:
                friend.Accept(remark=friend.name)
                ac_friend.append(friend)
        for friend in ac_friend:
            send_message("BBB", friend.name)
        if wx.CheckNewMessage():
            new_msgs = wx.GetNextNewMessage()
            for key, value in new_msgs.items():
                if key != "Self":
                    for new_msg in value:
                        if 'CCC' in new_msg[1]:
                            wx.SendMsg('DDD', key, clear="True")
        time.sleep(5) # 每隔 5 秒检查一次新消息





if __name__ == "__main__":
    mcp.run()




