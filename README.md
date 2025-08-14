# DeepSeek Web Chat 客户端

一个使用Python和Selenium自动化登录DeepSeek并进行web chat对话的演示项目。

## 功能特性

- 🤖 自动登录DeepSeek chat
- 💬 发送消息并获取AI响应
- 📝 获取对话历史
- 🆕 开始新对话
- 📸 截图保存
- 🎮 交互式和批量测试模式

## 环境要求

- Python 3.11+
- Chrome浏览器
- DeepSeek账号

## 安装步骤

1. 克隆项目
```bash
git clone <项目地址>
cd deepseek_client
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入你的DeepSeek登录凭据
```

## 使用方法

### 方式一：运行演示程序
```bash
python demo.py
```

程序会提供两种模式：
- 交互式对话演示：可以实时与DeepSeek对话
- 批量测试演示：自动测试预设的问题

### 方式二：直接使用客户端类
```python
from src.deepseek_client import DeepSeekWebClient

# 创建客户端实例
client = DeepSeekWebClient(headless=False)

# 登录
if client.login("your_email@example.com", "your_password"):
    # 发送消息
    response = client.send_message("你好")
    print(f"AI回复: {response}")
    
    # 关闭浏览器
    client.close()
```

## 配置说明

### 环境变量 (.env文件)
```env
DEEPSEEK_EMAIL=your_email@example.com
DEEPSEEK_PASSWORD=your_password
HEADLESS=true
TIMEOUT=30
```

### 客户端参数
- `headless`: 是否使用无头模式 (默认: True)
- `timeout`: 操作超时时间，秒 (默认: 30)

## API文档

### DeepSeekWebClient类

#### 初始化
```python
client = DeepSeekWebClient(headless=True, timeout=30)
```

#### 主要方法

- `init_driver()`: 初始化Chrome驱动
- `login(email, password)`: 登录DeepSeek
- `send_message(message)`: 发送消息并获取响应
- `wait_for_response(timeout)`: 等待AI响应
- `get_conversation_history()`: 获取对话历史
- `start_new_chat()`: 开始新对话
- `take_screenshot(filename)`: 截图
- `close()`: 关闭浏览器

## 注意事项

1. 首次运行时会自动下载ChromeDriver
2. 请确保Chrome浏览器已安装
3. 登录凭据请妥善保管，建议使用环境变量
4. 网络不稳定时可能需要增加timeout值
5. DeepSeek网站更新可能导致选择器失效，需要相应更新代码

## 故障排除

### 常见问题

1. **ChromeDriver下载失败**
   - 检查网络连接
   - 手动下载ChromeDriver并设置PATH

2. **登录失败**
   - 检查邮箱密码是否正确
   - 确认DeepSeek账号状态正常

3. **元素定位失败**
   - DeepSeek页面可能已更新
   - 检查控制台输出的错误信息

4. **响应超时**
   - 增加timeout参数值
   - 检查网络连接

## 开发说明

项目结构：
```
deepseek_client/
├── src/
│   └── deepseek_client.py    # 主要客户端类
├── demo.py                   # 演示程序
├── requirements.txt          # 依赖包
├── .env.example             # 环境变量示例
└── README.md                # 说明文档
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 免责声明

本项目仅用于学习和研究目的，请遵守DeepSeek的使用条款。