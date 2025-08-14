#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速测试已登录状态
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def quick_test():
    """快速测试"""
    print("=== 快速登录状态测试 ===")
    
    # 非无头模式，连接到现有会话
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("1. 访问DeepSeek...")
        driver.get("https://chat.deepseek.com")
        time.sleep(5)
        
        current_url = driver.current_url
        page_title = driver.title
        
        print(f"当前URL: {current_url}")
        print(f"页面标题: {page_title}")
        
        # 截图保存当前状态
        driver.save_screenshot("current_state.png")
        print("截图已保存: current_state.png")
        
        # 检查登录状态
        if "sign_in" not in current_url:
            print("✅ 不在登录页面，可能已登录")
            
            # 查找聊天输入框
            try:
                inputs = driver.find_elements(By.CSS_SELECTOR, "textarea, input[type='text']")
                print(f"找到 {len(inputs)} 个输入框:")
                
                for i, inp in enumerate(inputs):
                    placeholder = inp.get_attribute('placeholder') or '无'
                    if inp.is_displayed():
                        print(f"  {i+1}. placeholder='{placeholder}' (可见)")
                        
                        # 如果是聊天输入框，尝试发送测试消息
                        if any(keyword in placeholder.lower() for keyword in ['消息', 'message', '输入']):
                            print("🧪 尝试发送测试消息...")
                            
                            test_message = "你好，这是自动化测试消息"
                            inp.clear()
                            inp.send_keys(test_message)
                            
                            # 查找发送按钮
                            buttons = driver.find_elements(By.CSS_SELECTOR, "button")
                            for btn in buttons:
                                btn_text = btn.text.strip()
                                if btn_text in ['发送', 'Send', '提交'] and btn.is_displayed():
                                    print(f"找到发送按钮: {btn_text}")
                                    btn.click()
                                    print("✅ 消息已发送！")
                                    
                                    # 等待响应
                                    print("⏳ 等待AI响应...")
                                    time.sleep(10)
                                    
                                    # 截图保存结果
                                    driver.save_screenshot("message_test_result.png")
                                    print("测试结果截图: message_test_result.png")
                                    
                                    print("🎉 DeepSeek聊天测试成功！")
                                    return True
                    else:
                        print(f"  {i+1}. placeholder='{placeholder}' (隐藏)")
                        
            except Exception as e:
                print(f"查找输入框时出错: {e}")
                
        else:
            print("❌ 仍在登录页面")
            
        print("\n保持浏览器打开30秒供观察...")
        time.sleep(30)
        
        return False
        
    except Exception as e:
        print(f"测试出错: {e}")
        driver.save_screenshot("quick_test_error.png")
        return False
        
    finally:
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    quick_test()