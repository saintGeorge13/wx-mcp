# wx-mcp
在https://github.com/barantt/wxauto-mcp的基础上添加了自动回复用户信息和自动通过好友申请的功能，可以根据自身需求修改回复和通过好友规则
- **auto_friend_accept_and_message_reply**: 自动回复用户信息和自动通过好友申请

## 使用方法

### 安装uv

参考[uv官方安装文档](https://docs.astral.sh/uv/getting-started/installation/)

### 配置wx-mcp

```bash
git clone https://github.com/saintGeorge13/wx-mcp.git
cd wx-mcp
uv sync
```

### Claude Desktop 配置

要在Claude Desktop中使用，请添加服务器配置：

在Windows上：`%APPDATA%/Claude/claude_desktop_config.json`


```json
"mcpServers": {
  "wx-mcp": {
    "command": "uv",
    "args": [
      "--directory",
      "path\\to\\wx-mcp",
      "run",
      "wx-mcp.py"
    ]
  }
}
```


### Cursor配置
在Cursor中使用，请在Cursor的MCP配置文件中添加以下内容：

在Windows上：`%USERPROFILE%\.cursor\mcp.json`  

```json
"mcpServers": {
  "wx-mcp": {
    "command": "uv",
    "args": [
      "--directory",
      "path\\to\\wx-mcp",
      "run",
      "wx-mcp.py"
    ]
  }
}
```
