#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cloudflare感知的DeepSeek客户端
处理反自动化机制
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from dotenv import load_dotenv

class CloudflareAwareDeepSeekClient:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.wait = None
        
    def init_driver(self):
        """初始化抗检测的Chrome驱动"""
        try:
            print("正在初始化抗检测浏览器...")
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless=new")
            
            # 抗检测选项
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # 更真实的User-Agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # 移除webdriver属性
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 30)
            
            print("✅ 浏览器初始化成功")
            return True
            
        except Exception as e:
            print(f"❌ 浏览器初始化失败: {e}")
            return False
    
    def human_like_wait(self, min_seconds=1, max_seconds=3):
        """人类行为模拟等待"""
        wait_time = random.uniform(min_seconds, max_seconds)
        time.sleep(wait_time)
    
    def human_like_type(self, element, text):
        """人类行为模拟输入"""
        element.clear()
        self.human_like_wait(0.5, 1)
        
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        self.human_like_wait(0.5, 1)
    
    def detect_cloudflare(self):
        """检测Cloudflare挑战"""
        try:
            # 检查Cloudflare相关元素
            cf_indicators = [
                "Checking your browser before accessing",
                "Please wait while your request is being verified",
                "This process is automatic",
                "DDoS protection by Cloudflare",
                "cf-browser-verification",
                "cf-challenge-running"
            ]
            
            page_source = self.driver.page_source.lower()
            for indicator in cf_indicators:
                if indicator.lower() in page_source:
                    print(f"🛡️  检测到Cloudflare保护: {indicator}")
                    return True
            
            # 检查特定元素
            cf_selectors = [
                "[data-cf-beacon]",
                ".cf-browser-verification",
                "#cf-challenge-running",
                ".cf-challenge-running"
            ]
            
            for selector in cf_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"🛡️  检测到Cloudflare元素: {selector}")
                        return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            print(f"检测Cloudflare时出错: {e}")
            return False
    
    def wait_for_cloudflare(self, timeout=60):
        """等待Cloudflare挑战完成"""
        print("⏳ 等待Cloudflare验证完成...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.detect_cloudflare():
                print("✅ Cloudflare验证完成")
                return True
            
            print(".", end="", flush=True)
            time.sleep(2)
        
        print("\n⚠️  Cloudflare验证超时")
        return False
    
    def smart_login_check(self):
        """智能登录状态检查"""
        try:
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            print(f"当前URL: {current_url}")
            print(f"页面标题: {page_title}")
            
            # 多种登录成功的判断条件
            success_indicators = [
                "sign_in" not in current_url and "chat.deepseek.com" in current_url,
                "dashboard" in current_url,
                "conversation" in current_url,
                page_title and "登录" not in page_title and "sign" not in page_title.lower()
            ]
            
            # 检查页面元素
            try:
                # 查找聊天相关元素
                chat_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "textarea, input[placeholder*='消息'], input[placeholder*='message'], .chat, .conversation")
                
                if chat_elements:
                    print("✅ 检测到聊天界面元素")
                    return True
                    
            except:
                pass
            
            # 检查是否有用户信息或设置按钮
            try:
                user_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    ".user, .profile, .avatar, .settings, [data-testid*='user']")
                
                if user_elements:
                    print("✅ 检测到用户界面元素")
                    return True
                    
            except:
                pass
            
            if any(success_indicators):
                print("✅ 检测到登录成功指示")
                return True
            
            return False
            
        except Exception as e:
            print(f"登录状态检查出错: {e}")
            return False
    
    def test_send_message(self, message="你好，这是一个测试消息"):
        """测试发送消息"""
        try:
            print(f"🧪 测试发送消息: {message}")
            
            # 多种消息输入框选择器
            input_selectors = [
                "textarea[placeholder*='输入']",
                "textarea[placeholder*='message']",
                "input[type='text'][placeholder*='消息']",
                "textarea",
                ".message-input textarea",
                "[contenteditable='true']"
            ]
            
            message_input = None
            for selector in input_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            message_input = element
                            print(f"✅ 找到消息输入框: {selector}")
                            break
                    if message_input:
                        break
                except:
                    continue
            
            if not message_input:
                print("❌ 未找到消息输入框")
                return False
            
            # 人类行为模拟输入
            self.human_like_type(message_input, message)
            
            # 查找发送按钮
            send_selectors = [
                "button[type='submit']",
                "button:contains('发送')",
                "button:contains('Send')",
                ".send-button",
                "[data-testid*='send']"
            ]
            
            send_button = None
            for selector in send_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            text = element.text.strip()
                            if any(keyword in text for keyword in ['发送', 'Send', '提交']):
                                send_button = element
                                break
                    if send_button:
                        break
                except:
                    continue
            
            if send_button:
                send_button.click()
                print("✅ 消息已发送")
            else:
                # 尝试按Enter发送
                from selenium.webdriver.common.keys import Keys
                message_input.send_keys(Keys.ENTER)
                print("✅ 通过Enter键发送消息")
            
            # 等待响应
            print("⏳ 等待AI响应...")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ 发送消息失败: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("🔒 浏览器已关闭")

def main():
    """主函数"""
    print("=== Cloudflare感知的DeepSeek客户端测试 ===")
    
    client = CloudflareAwareDeepSeekClient(headless=False)
    
    try:
        if not client.init_driver():
            return
        
        print("\n1. 访问DeepSeek...")
        client.driver.get("https://chat.deepseek.com")
        client.human_like_wait(2, 4)
        
        # 检测并等待Cloudflare
        if client.detect_cloudflare():
            if not client.wait_for_cloudflare():
                print("❌ Cloudflare验证失败")
                return
        
        print("\n2. 检查当前状态...")
        if client.smart_login_check():
            print("🎉 检测到已登录状态！")
            
            # 截图
            client.driver.save_screenshot("logged_in_state.png")
            
            # 测试发送消息
            if client.test_send_message():
                print("🎊 消息发送测试成功！")
                
                # 等待响应并截图
                time.sleep(10)
                client.driver.save_screenshot("message_sent.png")
                
                print("🏆 DeepSeek客户端完全验证成功！")
            else:
                print("⚠️  消息发送测试失败")
        else:
            print("ℹ️  当前未登录，需要手动登录")
            print("请在浏览器中完成登录...")
            
        print("\n继续观察60秒...")
        time.sleep(60)
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        client.driver.save_screenshot("test_error.png")
        
    finally:
        client.close()

if __name__ == "__main__":
    main()