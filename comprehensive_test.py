#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DeepSeek客户端综合测试
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from deepseek_client import DeepSeekWebClient
import time
from dotenv import load_dotenv

def comprehensive_test():
    """综合测试"""
    print("=== DeepSeek Web Chat 客户端综合测试 ===")
    print()
    
    # 创建测试报告
    test_results = {
        "环境初始化": False,
        "页面访问": False,
        "登录模式切换": False,
        "凭据填入": False,
        "登录检测": False,
        "消息发送": False,
        "响应接收": False
    }
    
    # 加载环境变量
    load_dotenv()
    email = os.getenv('DEEPSEEK_EMAIL')
    password = os.getenv('DEEPSEEK_PASSWORD')
    
    print(f"📋 测试配置:")
    print(f"   账号: {email}")
    print(f"   密码: {'*' * len(password) if password else 'None'}")
    print()
    
    # 创建客户端实例
    client = DeepSeekWebClient(headless=False, timeout=60)
    
    try:
        print("🔧 步骤 1: 环境初始化")
        print("-" * 40)
        
        if client.init_driver():
            print("✅ 浏览器驱动初始化成功")
            test_results["环境初始化"] = True
        else:
            print("❌ 浏览器驱动初始化失败")
            return test_results
        
        print("\n🌐 步骤 2: 页面访问")
        print("-" * 40)
        
        try:
            client.driver.get("https://chat.deepseek.com/sign_in")
            time.sleep(3)
            
            current_url = client.driver.current_url
            page_title = client.driver.title
            
            print(f"   访问URL: https://chat.deepseek.com/sign_in")
            print(f"   当前URL: {current_url}")
            print(f"   页面标题: {page_title}")
            
            if "deepseek.com" in current_url:
                print("✅ 页面访问成功")
                test_results["页面访问"] = True
            else:
                print("❌ 页面访问失败")
                
        except Exception as e:
            print(f"❌ 页面访问出错: {e}")
        
        print("\n🔄 步骤 3: 登录模式切换")
        print("-" * 40)
        
        try:
            # 查找密码登录切换按钮
            all_elements = client.driver.find_elements("css selector", "*")
            password_login_element = None
            
            for element in all_elements:
                try:
                    if element.text.strip() == "密码登录":
                        password_login_element = element
                        break
                except:
                    continue
            
            if password_login_element:
                client.driver.execute_script("arguments[0].scrollIntoView();", password_login_element)
                time.sleep(1)
                password_login_element.click()
                time.sleep(3)
                
                # 验证切换成功
                password_inputs = client.driver.find_elements("css selector", "input[type='password']")
                if password_inputs:
                    print("✅ 成功切换到密码登录模式")
                    test_results["登录模式切换"] = True
                else:
                    print("❌ 密码登录模式切换失败")
            else:
                print("❌ 未找到密码登录切换按钮")
                
        except Exception as e:
            print(f"❌ 登录模式切换出错: {e}")
        
        print("\n📝 步骤 4: 凭据填入")
        print("-" * 40)
        
        try:
            # 填入邮箱
            email_input = client.driver.find_element("css selector", "input[type='text']")
            email_input.clear()
            email_input.send_keys(email)
            print(f"✅ 邮箱填入成功: {email}")
            
            # 填入密码
            password_input = client.driver.find_element("css selector", "input[type='password']")
            password_input.clear()
            password_input.send_keys(password)
            print("✅ 密码填入成功")
            
            test_results["凭据填入"] = True
            
        except Exception as e:
            print(f"❌ 凭据填入出错: {e}")
        
        print("\n🔐 步骤 5: 执行登录")
        print("-" * 40)
        print("请在浏览器中手动点击登录按钮完成登录...")
        print("程序将自动检测登录状态变化...")
        
        # 截图当前状态
        client.take_screenshot("test_before_login.png")
        print("登录前截图: test_before_login.png")
        
        # 等待登录
        max_wait = 120  # 2分钟
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            current_url = client.driver.current_url
            
            if "sign_in" not in current_url and "chat.deepseek.com" in current_url:
                print("🎉 检测到登录成功！")
                print(f"   登录后URL: {current_url}")
                
                # 截图成功状态
                client.take_screenshot("test_login_success.png")
                print("   登录成功截图: test_login_success.png")
                
                test_results["登录检测"] = True
                break
            
            time.sleep(2)
            remaining = max_wait - (time.time() - start_time)
            print(f"\r   等待登录... 剩余时间: {int(remaining)}秒", end="", flush=True)
        
        print()
        
        if not test_results["登录检测"]:
            print("❌ 登录检测超时")
            return test_results
        
        print("\n💬 步骤 6: 消息发送测试")
        print("-" * 40)
        
        try:
            # 等待页面完全加载
            time.sleep(5)
            
            # 查找消息输入框
            input_selectors = [
                "textarea[placeholder*='输入']",
                "textarea[placeholder*='message']", 
                "textarea",
                "input[type='text']",
                "[contenteditable='true']"
            ]
            
            message_input = None
            for selector in input_selectors:
                try:
                    elements = client.driver.find_elements("css selector", selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # 检查是否是消息输入框
                            placeholder = element.get_attribute('placeholder') or ''
                            if any(keyword in placeholder.lower() for keyword in ['消息', 'message', '输入', 'chat']):
                                message_input = element
                                print(f"✅ 找到消息输入框: {selector}")
                                print(f"   placeholder: {placeholder}")
                                break
                    if message_input:
                        break
                except Exception as e:
                    print(f"   选择器 {selector} 查找失败: {e}")
                    continue
            
            if not message_input:
                print("❌ 未找到消息输入框")
                # 列出所有可见的输入元素供调试
                all_inputs = client.driver.find_elements("css selector", "input, textarea, [contenteditable='true']")
                print(f"   页面上找到 {len(all_inputs)} 个输入元素:")
                for i, inp in enumerate(all_inputs):
                    if inp.is_displayed():
                        tag = inp.tag_name
                        inp_type = inp.get_attribute('type') or '无'
                        placeholder = inp.get_attribute('placeholder') or '无'
                        print(f"     {i+1}. <{tag}> type='{inp_type}' placeholder='{placeholder}'")
                return test_results
            
            # 发送测试消息
            test_message = "你好，这是DeepSeek自动化客户端的测试消息。请简单回复确认收到。"
            print(f"📤 发送消息: {test_message}")
            
            message_input.clear()
            message_input.send_keys(test_message)
            
            # 查找发送按钮
            send_selectors = [
                "button[type='submit']",
                "button",
                "[role='button']"
            ]
            
            send_button = None
            for selector in send_selectors:
                try:
                    buttons = client.driver.find_elements("css selector", selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button_text = button.text.strip().lower()
                            if any(keyword in button_text for keyword in ['发送', 'send', '提交']):
                                send_button = button
                                print(f"✅ 找到发送按钮: '{button.text.strip()}'")
                                break
                    if send_button:
                        break
                except:
                    continue
            
            if send_button:
                send_button.click()
                print("✅ 消息发送成功")
                test_results["消息发送"] = True
            else:
                # 尝试按Enter发送
                from selenium.webdriver.common.keys import Keys
                message_input.send_keys(Keys.ENTER)
                print("✅ 通过Enter键发送消息")
                test_results["消息发送"] = True
            
        except Exception as e:
            print(f"❌ 消息发送出错: {e}")
        
        print("\n📨 步骤 7: 等待AI响应")
        print("-" * 40)
        
        if test_results["消息发送"]:
            print("⏳ 等待AI响应（最多60秒）...")
            
            response_start_time = time.time()
            response_timeout = 60
            
            while time.time() - response_start_time < response_timeout:
                try:
                    # 查找响应消息
                    message_selectors = [
                        ".message",
                        ".chat-message",
                        "[data-testid*='message']",
                        ".response",
                        ".ai-message"
                    ]
                    
                    for selector in message_selectors:
                        try:
                            messages = client.driver.find_elements("css selector", selector)
                            if len(messages) > 0:
                                last_message = messages[-1]
                                message_text = last_message.text.strip()
                                if message_text and len(message_text) > 10:  # 有实际内容
                                    print(f"📨 收到AI响应: {message_text[:100]}...")
                                    test_results["响应接收"] = True
                                    break
                        except:
                            continue
                    
                    if test_results["响应接收"]:
                        break
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"检查响应时出错: {e}")
                    break
            
            if not test_results["响应接收"]:
                print("⚠️  未检测到AI响应（可能响应较慢或选择器需要调整）")
        
        # 最终截图
        client.take_screenshot("test_final_state.png")
        print(f"\n📸 最终状态截图: test_final_state.png")
        
    except Exception as e:
        print(f"❌ 测试过程出现异常: {e}")
        client.take_screenshot("test_exception.png")
        
    finally:
        print("\n📊 测试结果总结")
        print("=" * 50)
        
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        
        for test_name, result in test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name}: {status}")
        
        print(f"\n🏆 总体结果: {passed_tests}/{total_tests} 项测试通过")
        
        if passed_tests >= 5:  # 核心功能通过
            print("🎉 DeepSeek客户端核心功能验证成功！")
        elif passed_tests >= 3:
            print("⚠️  DeepSeek客户端部分功能可用，需要调优")
        else:
            print("❌ DeepSeek客户端需要修复")
        
        print("\n⏰ 保持浏览器打开30秒供最终检查...")
        time.sleep(30)
        
        client.close()
        
    return test_results

if __name__ == "__main__":
    comprehensive_test()