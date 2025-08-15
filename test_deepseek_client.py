#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试流式响应处理
"""

from src.deepseek_client import DeepSeekWebClient
import time

def test_streaming_response():
    """测试流式响应功能"""
    print("=== 测试DeepSeek流式响应处理 ===")
    
    # 创建客户端（非无头模式便于观察）
    client = DeepSeekWebClient(headless=False, timeout=30)
    
    try:
        print("🔐 正在登录...")
        if client.login():
            print("✅ 登录成功")
            
            # 等待页面稳定
            time.sleep(5)
            
            print("🔍 调试页面元素...")
            client.debug_page_elements()
            
            print("💬 发送测试消息...")
            test_message = "请简单介绍一下你自己，大概100字左右"
            
            response = client.send_message(test_message)
            
            if response:
                print(f"✅ 成功接收到流式响应:")
                print(f"📝 响应长度: {len(response)} 字符")
                print(f"📄 响应内容: {response[:200]}...")
                
                # 截图保存结果
                client.take_screenshot("streaming_response_test.png")
                
            else:
                print("❌ 未接收到响应")
                client.take_screenshot("streaming_response_failed.png")
                
        else:
            print("❌ 登录失败")
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        client.take_screenshot("streaming_test_error.png")
        
    finally:
        print("⏱️ 保持浏览器打开30秒以便观察...")
        time.sleep(30)
        client.close()
        print("🔧 测试完成")

if __name__ == "__main__":
    test_streaming_response()