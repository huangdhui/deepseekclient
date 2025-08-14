#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
手动验证登录 - 允许用户在自动化填入凭据后手动操作
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from deepseek_client import DeepSeekWebClient
import time
from dotenv import load_dotenv

def manual_verify():
    """手动验证登录"""
    print("=== 手动验证登录 ===")
    print("程序会自动填入凭据，然后你可以:")
    print("1. 检查输入的内容是否正确")
    print("2. 手动点击登录按钮")
    print("3. 处理任何额外的验证步骤")
    print("4. 如果登录成功，可以测试发送消息")
    print()
    
    # 加载环境变量
    load_dotenv()
    
    email = os.getenv('DEEPSEEK_EMAIL')
    password = os.getenv('DEEPSEEK_PASSWORD')
    
    print(f"将要使用的凭据:")
    print(f"  账号: {email}")
    print(f"  密码: {'*' * len(password) if password else 'None'}")
    print()
    
    # 使用非无头模式
    client = DeepSeekWebClient(headless=False, timeout=120)
    
    try:
        print("1. 启动浏览器并访问登录页面...")
        if not client.init_driver():
            return False
        
        client.driver.get("https://chat.deepseek.com/sign_in")
        time.sleep(3)
        
        print("2. 自动切换到密码登录模式...")
        # 切换到密码登录
        all_elements = client.driver.find_elements("css selector", "*")
        for element in all_elements:
            try:
                if element.text.strip() == "密码登录":
                    element.click()
                    time.sleep(3)
                    print("✅ 已切换到密码登录模式")
                    break
            except:
                continue
        
        print("3. 自动填入凭据...")
        
        # 填入邮箱
        try:
            email_input = client.driver.find_element("css selector", "input[type='text']")
            email_input.clear()
            email_input.send_keys(email)
            print("✅ 邮箱已填入")
        except Exception as e:
            print(f"❌ 填入邮箱失败: {e}")
        
        # 填入密码
        try:
            password_input = client.driver.find_element("css selector", "input[type='password']")
            password_input.clear()
            password_input.send_keys(password)
            print("✅ 密码已填入")
        except Exception as e:
            print(f"❌ 填入密码失败: {e}")
        
        print("\n" + "="*60)
        print("🖱️  现在请在浏览器中手动操作：")
        print()
        print("1. 检查邮箱/手机号是否正确输入")
        print("2. 检查密码是否正确输入")
        print("3. 手动点击'登录'按钮")
        print()
        print("如果出现验证码、滑块验证等，请手动完成")
        print()
        print("登录成功后，程序会自动检测并继续...")
        print("="*60)
        print()
        
        # 等待用户手动登录
        max_wait_time = 300  # 5分钟
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            current_url = client.driver.current_url
            
            # 检查是否登录成功（不在登录页面）
            if "sign_in" not in current_url and "chat.deepseek.com" in current_url:
                print("🎉 检测到登录成功！")
                print(f"当前页面: {current_url}")
                
                # 截图保存成功状态
                client.take_screenshot("manual_login_success.png")
                
                print("\n4. 测试发送消息...")
                test_message = "你好，这是一个自动化测试"
                
                try:
                    response = client.send_message(test_message)
                    if response:
                        print(f"✅ AI回复: {response[:200]}...")
                        print("\n🎊 验证完全成功！DeepSeek客户端完全可用！")
                        
                        # 最终截图
                        client.take_screenshot("full_verification_success.png")
                        
                        print("\n继续保持浏览器打开60秒供进一步测试...")
                        time.sleep(60)
                        return True
                    else:
                        print("❌ 未收到AI回复")
                        
                except Exception as e:
                    print(f"发送消息时出错: {e}")
                
                break
            
            time.sleep(3)  # 每3秒检查一次
            remaining = max_wait_time - (time.time() - start_time)
            if remaining > 0:
                print(f"\r等待手动登录... 剩余时间: {int(remaining)}秒", end="", flush=True)
        
        print("\n")
        
        # 检查最终状态
        final_url = client.driver.current_url
        if "sign_in" in final_url:
            print("❌ 仍在登录页面，登录未成功")
            print("可能的原因:")
            print("  1. 凭据确实不正确")
            print("  2. 需要额外的验证步骤")
            print("  3. 账号状态异常")
            print("  4. 地区限制或其他策略限制")
            
            # 检查错误信息
            try:
                error_elements = client.driver.find_elements("css selector", 
                    ".error, .alert, .warning, [class*='error'], [class*='alert']")
                for elem in error_elements:
                    error_text = elem.text.strip()
                    if error_text:
                        print(f"  页面错误: {error_text}")
            except:
                pass
                
        else:
            print(f"当前页面: {final_url}")
            
        return False
        
    except Exception as e:
        print(f"验证过程出错: {e}")
        client.take_screenshot("manual_verify_error.png")
        return False
        
    finally:
        print("\n按任意键关闭浏览器...")
        try:
            input()
        except:
            time.sleep(10)
        client.close()

if __name__ == "__main__":
    manual_verify()