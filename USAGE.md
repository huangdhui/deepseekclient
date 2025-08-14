# DeepSeek Web Chat 客户端使用指南

## ✅ 环境验证

通过测试确认：
- ✅ Python 3.9.2 环境正常
- ✅ Chrome浏览器已安装
- ✅ Selenium 4.15.2 已安装
- ✅ WebDriver正常工作
- ✅ 可以访问DeepSeek网站
- ✅ 能够定位页面元素

## 🚀 快速开始

### 1. 环境检查
```bash
python test_setup.py
```

### 2. 页面访问测试
```bash
python test_page_access.py
```

### 3. 配置登录凭据

复制配置文件：
```bash
cp .env.example .env
```

编辑`.env`文件：
```env
DEEPSEEK_EMAIL=your_email@example.com
DEEPSEEK_PASSWORD=your_password
HEADLESS=false
TIMEOUT=30
```

### 4. 运行完整演示

**交互式模式（推荐首次使用）：**
```bash
python3 -c "
from src.deepseek_client import DeepSeekWebClient
client = DeepSeekWebClient(headless=False)
if client.login():
    response = client.send_message('你好')
    print(f'AI回复: {response}')
client.close()
"
```

**批量测试模式：**
```bash
python demo.py
```

## 📝 使用示例

### 基本用法
```python
from src.deepseek_client import DeepSeekWebClient

# 创建客户端（非无头模式，方便调试）
client = DeepSeekWebClient(headless=False, timeout=30)

try:
    # 登录
    if client.login("your_email", "your_password"):
        print("登录成功！")
        
        # 发送消息
        response = client.send_message("请介绍一下Python的特点")
        if response:
            print(f"AI回复: {response}")
        
        # 开始新对话
        client.start_new_chat()
        
        # 获取对话历史
        history = client.get_conversation_history()
        print(f"对话历史: {len(history)} 条消息")
        
        # 截图
        client.take_screenshot("my_chat.png")
        
finally:
    client.close()
```

### 批量问答
```python
questions = [
    "什么是人工智能？",
    "请用Python写一个斐波那契数列",
    "解释一下机器学习的基本概念"
]

client = DeepSeekWebClient(headless=True)  # 批量处理使用无头模式
try:
    if client.login():
        for i, question in enumerate(questions, 1):
            print(f"问题 {i}: {question}")
            response = client.send_message(question)
            print(f"回答: {response[:100]}...")
            print("-" * 50)
finally:
    client.close()
```

## 🔧 高级配置

### 客户端参数
```python
client = DeepSeekWebClient(
    headless=True,      # 无头模式
    timeout=60          # 超时时间（秒）
)
```

### Chrome浏览器选项
客户端默认配置了以下Chrome选项：
- `--no-sandbox`: 禁用沙箱
- `--disable-dev-shm-usage`: 禁用dev-shm
- `--disable-gpu`: 禁用GPU
- `--disable-web-security`: 允许跨域
- `--window-size=1280,720`: 设置窗口大小

## 🐛 故障排除

### 1. 浏览器启动失败
```bash
# 检查Chrome是否正确安装
python test_setup.py
```

### 2. 登录失败
- 确认邮箱密码正确
- 检查网络连接
- 尝试手动登录确认账号状态

### 3. 元素定位失败
- DeepSeek页面可能更新了结构
- 检查截图文件分析页面变化
- 可能需要更新选择器

### 4. 响应超时
- 增加timeout参数
- 检查网络延迟
- 确认DeepSeek服务状态

## 📊 测试结果

最新测试结果（2024年测试）：
- ✅ 页面标题: "DeepSeek - 探索未至之境"
- ✅ 自动重定向到登录页面
- ✅ 找到1个邮箱输入框
- ✅ 找到1个密码输入框
- ✅ 截图功能正常

## 🔒 安全注意事项

1. **凭据保护**: 不要将`.env`文件提交到版本控制
2. **使用限制**: 遵守DeepSeek的使用条款
3. **频率控制**: 避免过于频繁的请求
4. **数据隐私**: 注意保护敏感信息

## 📚 API参考

### DeepSeekWebClient类方法

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `__init__(headless, timeout)` | 初始化客户端 | headless: bool, timeout: int | None |
| `init_driver()` | 初始化浏览器驱动 | 无 | bool |
| `login(email, password)` | 登录DeepSeek | email: str, password: str | bool |
| `send_message(message)` | 发送消息 | message: str | str or None |
| `wait_for_response(timeout)` | 等待AI响应 | timeout: int | str or None |
| `get_conversation_history()` | 获取对话历史 | 无 | list |
| `start_new_chat()` | 开始新对话 | 无 | bool |
| `take_screenshot(filename)` | 截图 | filename: str | bool |
| `close()` | 关闭浏览器 | 无 | None |

## 🎯 最佳实践

1. **首次使用**: 用`headless=False`观察自动化过程
2. **生产使用**: 用`headless=True`提高效率
3. **错误处理**: 始终使用try-finally确保浏览器关闭
4. **资源管理**: 及时调用`close()`方法
5. **日志记录**: 关注控制台输出信息

## 🔄 更新维护

如果DeepSeek网站更新导致脚本失效：

1. 运行`python test_page_access.py`检查页面
2. 查看生成的截图文件
3. 更新CSS选择器
4. 测试新的选择器是否有效

---

**项目状态**: ✅ 可用  
**最后测试**: 2025年1月  
**兼容性**: Python 3.8+ | Chrome 120+