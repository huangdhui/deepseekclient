#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from .logger_config import logger, get_screenshot_path

load_dotenv()


class DeepSeekWebClient:
    def __init__(self, headless=True, timeout=30):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
        
    def init_driver(self):
        """初始化Chrome浏览器驱动"""
        try:
            logger.info("正在初始化浏览器驱动...")
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--window-size=1280,720")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            logger.info("正在启动Chrome浏览器...")
            # 直接使用系统Chrome，不依赖WebDriverManager
            self.driver = webdriver.Chrome(options=chrome_options)
                
            self.wait = WebDriverWait(self.driver, self.timeout)
            
            logger.info("浏览器驱动初始化成功")
            return True
        except Exception as e:
            logger.error(f"浏览器驱动初始化失败: {e}")
            logger.error("请确保Chrome浏览器已安装，或手动下载ChromeDriver")
            return False
    
    def login(self, email=None, password=None):
        """登录DeepSeek"""
        if not self.driver:
            if not self.init_driver():
                return False
                
        email = email or os.getenv('DEEPSEEK_EMAIL')
        password = password or os.getenv('DEEPSEEK_PASSWORD')
        
        if not email or not password:
            logger.error("请提供邮箱和密码，或在.env文件中设置DEEPSEEK_EMAIL和DEEPSEEK_PASSWORD")
            return False
            
        try:
            logger.info("正在访问DeepSeek登录页面...")
            self.driver.get("https://chat.deepseek.com/sign_in")
            time.sleep(3)
            
            # 查找并点击"密码登录"切换
            logger.info("正在切换到密码登录模式...")
            try:
                # 查找只包含"密码登录"文本的tab元素
                all_elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
                password_login_element = None
                
                for element in all_elements:
                    try:
                        element_text = element.text.strip()
                        # 寻找只包含"密码登录"的元素（不包含其他文本）
                        if element_text == "密码登录":
                            password_login_element = element
                            logger.info("找到密码登录切换按钮")
                            break
                    except:
                        continue
                
                if password_login_element:
                    # 确保元素可见
                    self.driver.execute_script("arguments[0].scrollIntoView();", password_login_element)
                    time.sleep(1)
                    password_login_element.click()
                    logger.info("✅ 切换到密码登录模式")
                    time.sleep(3)  # 等待页面更新
                    
                    # 验证切换是否成功
                    password_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
                    if password_inputs:
                        logger.info("✅ 密码登录模式切换成功")
                    else:
                        logger.error("⚠️  密码登录模式切换可能失败")
                else:
                    logger.info("未找到密码登录切换选项，尝试继续...")
                    
            except Exception as e:
                logger.error(f"切换登录模式失败: {e}")
                
            # 等待邮箱输入框出现
            email_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], input[type='email'], input[placeholder*='邮箱'], input[placeholder*='email'], input[placeholder*='手机号']"))
            )
            email_input.clear()
            email_input.send_keys(email)
            logger.info("邮箱输入完成")
            
            # 等待页面响应
            time.sleep(2)
            
            # 重新查找密码输入框（页面可能有变化）
            try:
                password_input = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
                )
                password_input.clear()
                password_input.send_keys(password)
                logger.info("密码输入完成")
            except Exception as e:
                logger.error(f"找不到密码输入框: {e}")
                # 截图调试
                self.driver.save_screenshot(get_screenshot_path("login_error.png"))
                # 重新分析页面
                inputs = self.driver.find_elements(By.CSS_SELECTOR, "input")
                logger.info(f"当前页面输入框数量: {len(inputs)}")
                for i, inp in enumerate(inputs):
                    inp_type = inp.get_attribute('type')
                    placeholder = inp.get_attribute('placeholder')
                    logger.info(f"  输入框 {i+1}: type={inp_type}, placeholder={placeholder}")
                raise e
            
            # 等待页面完全加载
            time.sleep(2)
            
            # 查找登录按钮
            login_button = None
            logger.info("正在查找登录按钮...")
            
            # 等待一下让JavaScript加载完成
            time.sleep(3)
            
            # 专门查找div[role='button']中的登录按钮
            try:
                role_buttons = self.driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
                logger.info(f"找到 {len(role_buttons)} 个 div[role='button'] 元素")
                
                for i, button in enumerate(role_buttons):
                    button_text = button.text.strip()
                    logger.info(f"  按钮 {i+1}: '{button_text}'")
                    if button_text == '登录':
                        login_button = button
                        logger.info("✅ 找到登录按钮")
                        break
                        
            except Exception as e:
                logger.error(f"查找登录按钮失败: {e}")
            
            if not login_button:
                logger.info("未找到登录按钮，尝试按Enter键提交")
                from selenium.webdriver.common.keys import Keys
                password_input.send_keys(Keys.ENTER)
                logger.info("通过Enter键提交登录")
            else:
                try:
                    # 确保按钮可见和可点击
                    self.driver.execute_script("arguments[0].scrollIntoView();", login_button)
                    time.sleep(1)
                    login_button.click()
                    logger.info("登录按钮点击成功")
                except Exception as e:
                    logger.error(f"点击登录按钮失败: {e}，尝试JavaScript点击")
                    self.driver.execute_script("arguments[0].click();", login_button)
            
            # 等待页面跳转
            time.sleep(3)
            
            # 检查是否登录成功
            current_url = self.driver.current_url
            if "chat.deepseek.com" in current_url and "sign_in" not in current_url:
                logger.info("登录成功！")
                return True
            else:
                logger.error("登录失败，请检查凭据")
                return False
                
        except TimeoutException:
            logger.error("登录超时，请检查网络连接")
            return False
        except Exception as e:
            logger.error(f"登录过程中出现错误: {e}")
            return False
    
    def send_message(self, message):
        """发送消息到DeepSeek chat"""
        if not self.driver:
            logger.error("请先初始化驱动并登录")
            return None
            
        try:
            logger.info(f"正在发送消息: {message}")
            
            # 查找输入框
            message_selectors = [
                "textarea[placeholder*='输入']",
                "textarea[placeholder*='message']", 
                "input[type='text']",
                "textarea",
                ".input-area textarea",
                "[contenteditable='true']"
            ]
            
            message_input = None
            for selector in message_selectors:
                try:
                    message_input = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not message_input:
                logger.error("未找到消息输入框")
                return None
                
            # 清空并输入消息
            message_input.clear()
            message_input.send_keys(message)
            
            # 查找并点击发送按钮
            send_button = None
            
            # 先尝试常见的按钮选择器
            simple_selectors = [
                "button[type='submit']",
                ".send-button",
                "[data-testid='send-button']"
            ]
            
            for selector in simple_selectors:
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            # 如果没找到，尝试查找包含特定文本的按钮
            if not send_button:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
                    for button in buttons:
                        button_text = button.text.strip().lower()
                        if button_text in ['发送', 'send', '提交']:
                            send_button = button
                            break
                except:
                    pass
            
            if send_button:
                send_button.click()
                logger.info("消息已发送")
            else:
                # 尝试按Enter键发送
                from selenium.webdriver.common.keys import Keys
                message_input.send_keys(Keys.ENTER)
                logger.info("通过Enter键发送消息")
            
            # 等待响应
            response = self.wait_for_response()
            return response
            
        except Exception as e:
            logger.error(f"发送消息时出现错误: {e}")
            return None
    
    def wait_for_response(self, timeout=60):
        """等待AI响应"""
        logger.info("等待AI响应...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # 查找响应消息
                response_selectors = [
                    ".message-content",
                    ".chat-message", 
                    "[data-testid='message']",
                    ".response-text",
                    ".ai-message"
                ]
                
                for selector in response_selectors:
                    try:
                        messages = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if messages:
                            last_message = messages[-1].text.strip()
                            if last_message and not any(keyword in last_message.lower() for keyword in ['正在思考', 'thinking', 'typing', '...']):
                                logger.info("收到AI响应")
                                return last_message
                    except:
                        continue
                        
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"等待响应时出现错误: {e}")
                break
        
        logger.warning("等待响应超时")
        return None
    
    def get_conversation_history(self):
        """获取对话历史"""
        try:
            messages = []
            message_elements = self.driver.find_elements(By.CSS_SELECTOR, ".message, .chat-message, [data-testid='message']")
            
            for element in message_elements:
                content = element.text.strip()
                if content:
                    messages.append({
                        'content': content,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            return messages
        except Exception as e:
            logger.error(f"获取对话历史时出现错误: {e}")
            return []
    
    def start_new_chat(self):
        """开始新对话"""
        try:
            logger.info("正在开始新对话...")
            
            new_chat_selectors = [
                "button:contains('新对话')",
                "button:contains('New Chat')",
                ".new-chat-button",
                "[data-testid='new-chat']"
            ]
            
            for selector in new_chat_selectors:
                try:
                    new_chat_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    new_chat_button.click()
                    time.sleep(2)
                    logger.info("新对话已开始")
                    return True
                except NoSuchElementException:
                    continue
            
            logger.warning("未找到新对话按钮")
            return False
            
        except Exception as e:
            logger.error(f"开始新对话时出现错误: {e}")
            return False
    
    def take_screenshot(self, filename="screenshot.png"):
        """截图"""
        try:
            screenshot_path = get_screenshot_path(filename)
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"截图已保存: {screenshot_path}")
            return True
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("浏览器已关闭")


def main():
    """示例用法"""
    client = DeepSeekWebClient(headless=False)  # 设置为False以查看浏览器操作
    
    try:
        # 登录
        if client.login():
            # 发送消息
            response = client.send_message("你好，请介绍一下你自己")
            if response:
                logger.info(f"AI回复: {response}")
            
            # 再发送一个消息
            response = client.send_message("请用Python写一个简单的爬虫示例")
            if response:
                logger.info(f"AI回复: {response}")
            
            # 截图
            client.take_screenshot("deepseek_chat.png")
            
            # 获取对话历史
            history = client.get_conversation_history()
            logger.info(f"对话历史共{len(history)}条消息")
            
        else:
            logger.error("登录失败")
            
    finally:
        client.close()


if __name__ == "__main__":
    main()