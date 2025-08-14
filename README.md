# DeepSeek Web Chat 客户端

一个使用Python和Selenium实现DeepSeek自动化登录和对话的轻量级客户端。

## 🚀 功能特性

- 🤖 **自动化登录** - 无需人工干预的登录流程
- 🔄 **智能模式切换** - 自动切换到密码登录模式  
- 🛡️ **Cloudflare处理** - 自动处理安全验证
- 💬 **消息发送** - 发送消息并获取AI响应
- 📝 **对话管理** - 获取对话历史和开始新对话
- 📸 **截图功能** - 支持页面截图保存
- 🛠️ **简洁设计** - 轻量级模块化架构

## 环境要求

- Python 3.11+
- Chrome浏览器
- DeepSeek账号

## 🔧 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <项目地址>
cd deepseekclient

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置登录凭据
创建 `.env` 文件并填入DeepSeek登录信息：
```env
DEEPSEEK_EMAIL=your_email@example.com
DEEPSEEK_PASSWORD=your_password
```

### 3. 运行示例
```bash
# 运行主程序示例
python -c "
from src.deepseek_client import DeepSeekWebClient
client = DeepSeekWebClient(headless=False)
if client.login():
    response = client.send_message('你好')
    print(f'AI回复: {response}')
    client.close()
"
```

## 📚 使用方法

### 直接使用客户端类
```python
from src.deepseek_client import DeepSeekWebClient

# 创建客户端实例
client = DeepSeekWebClient(headless=False)

# 登录
if client.login():  # 自动从.env读取凭据
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

## 📁 项目结构

```
deepseekclient/
├── src/
│   ├── deepseek_client.py    # 核心客户端类
│   └── logger_config.py      # 日志配置模块
├── logs/                     # 日志和截图目录（自动创建）
│   ├── deepseek_client_YYYYMMDD.log  # 统一日志文件
│   └── *.png                # 截图文件
├── requirements.txt          # 依赖包列表
├── .env                     # 环境变量配置（需要创建）
└── README.md                # 项目说明文档
```

## 🎯 核心功能

### DeepSeekWebClient 类

这是项目的核心类，提供完整的DeepSeek自动化操作功能：

#### 主要特性
- ✅ **自动登录**: 支持邮箱密码登录，自动处理页面元素识别
- ✅ **智能重试**: 登录失败时自动重试机制
- ✅ **消息交互**: 发送消息并获取AI回复
- ✅ **会话管理**: 支持新建对话和获取历史记录
- ✅ **截图功能**: 支持页面截图保存到logs目录
- ✅ **统一日志**: 所有操作日志统一输出到控制台和文件
- ✅ **错误处理**: 完善的异常处理和日志记录

#### 使用示例
```python
from src.deepseek_client import DeepSeekWebClient

# 创建客户端
client = DeepSeekWebClient(headless=False, timeout=30)

# 登录并使用
if client.login():
    # 发送消息
    response = client.send_message("请介绍一下你自己")
    print(f"AI回复: {response}")
    
    # 截图
    client.take_screenshot("chat_screenshot.png")
    
    # 开始新对话
    client.start_new_chat()
    
    # 关闭浏览器
    client.close()
```

## 📝 日志系统

### 日志特性
- **控制台输出**: 实时显示操作状态和结果
- **文件记录**: 所有日志保存到 `logs/deepseek_client_YYYYMMDD.log`
- **统一管理**: INFO、WARNING、ERROR级别日志统一记录
- **时间戳**: 每条日志包含详细的时间信息
- **中文支持**: 完全支持中文日志内容

### 日志位置
- **日志文件**: `logs/deepseek_client_20250814.log`
- **截图文件**: `logs/*.png`
- **自动创建**: logs目录在首次使用时自动创建



## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 免责声明

本项目仅用于学习和研究目的，请遵守DeepSeek的使用条款。