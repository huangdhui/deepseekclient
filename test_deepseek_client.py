#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试流式响应处理 - 增强版本
"""

from src.deepseek_client import DeepSeekWebClient
import time
import os

def _is_response_complete_test(content):
    """测试用的响应完整性检测"""
    if not content:
        return False
    
    # 检查内容是否以完整的句子结尾
    complete_endings = ['。', '！', '？', '.', '!', '?', '~', '😊', '👍', '✨', '🎉']
    if any(content.strip().endswith(ending) for ending in complete_endings):
        return True
    
    # 检查是否包含完整的段落结构
    if len(content) > 100 and ('\n' in content or '：' in content):
        return True
    
    # 如果内容较短但包含关键信息，也认为完整
    if len(content) > 50 and any(keyword in content for keyword in ['我是', '可以', '帮助', '建议', '总结']):
        return True
    
    return False

def test_login_and_setup():
    """测试登录和基本设置"""
    print("🔐 测试登录功能...")
    client = DeepSeekWebClient(headless=False, timeout=30)
    
    try:
        # 检查环境变量
        if not os.getenv('DEEPSEEK_EMAIL') or not os.getenv('DEEPSEEK_PASSWORD'):
            print("❌ 请在.env文件中设置DEEPSEEK_EMAIL和DEEPSEEK_PASSWORD")
            return None
        
        # 尝试登录
        login_success = client.login()
        if login_success:
            print("✅ 登录成功")
            # 等待页面完全加载
            time.sleep(3)
            return client
        else:
            print("❌ 登录失败")
            client.take_screenshot("login_failed.png")
            return None
            
    except Exception as e:
        print(f"❌ 登录过程出错: {e}")
        client.take_screenshot("login_error.png")
        return None

def test_streaming_response_enhanced():
    """测试增强的流式响应功能"""
    print("\n=== 测试增强的DeepSeek流式响应处理 ===")
    
    # 首先测试登录
    client = test_login_and_setup()
    if not client:
        print("❌ 无法继续测试，登录失败")
        return
    
    try:
        # 测试不同类型的消息
        test_cases = [
            {
                "name": "300122",
                "message": "检索巨潮资讯、交易所官网、同花顺财经、新浪财经、财联社，涉及300122近六个月内是否涉及减持、解禁、配股、业绩下滑、证监会或证券管理部门严肃处理等负面消息以及该股所属行业负面消息，响应内容使用Markdown格式，只需包含消息维度、消息时间、关建内容、影响评估四个维度",
                "expected_min_length": 50
            },
            {
                "name": "002241",
                "message": "检索巨潮资讯、交易所官网、同花顺财经、新浪财经、财联社，涉及002241近六个月内是否涉及减持、解禁、配股、业绩下滑、证监会或证券管理部门严肃处理等负面消息以及该股所属行业负面消息，响应内容使用Markdown格式，只需包含消息维度、消息时间、关建内容、影响评估四个维度",
                "expected_min_length": 200
            },
            {
                "name": "300433",
                "message": "检索巨潮资讯、交易所官网、同花顺财经、新浪财经、财联社，涉及300433近六个月内是否涉及减持、解禁、配股、业绩下滑、证监会或证券管理部门严肃处理等负面消息以及该股所属行业负面消息，响应内容使用Markdown格式，只需包含消息维度、消息时间、关建内容、影响评估四个维度",
                "expected_min_length": 100
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 测试用例 {i}: {test_case['name']}")
            print(f"💬 发送消息: {test_case['message']}")
            
            # 每个测试用例都开始新对话（确保独立性）
            print("🔄 开始新对话...")
            new_chat_success = client.start_new_chat()
            if new_chat_success:
                print("✅ 新对话已开始")
                time.sleep(3)  # 等待页面稳定
            else:
                print("⚠️ 开始新对话失败，继续使用当前对话")
            
            start_time = time.time()
            print("📤 发送消息并等待完整响应...")
            response = client.send_message(test_case['message'])
            end_time = time.time()
            
            if response:
                response_length = len(response)
                elapsed_time = end_time - start_time
                
                print(f"✅ 成功接收到完整响应:")
                print(f"📝 响应长度: {response_length} 字符")
                print(f"⏱️ 响应时间: {elapsed_time:.2f} 秒")
                print(f"📄 响应预览: {response[:200]}...")
                
                # 验证响应质量
                if response_length >= test_case['expected_min_length']:
                    print(f"✅ 响应长度符合预期 (>= {test_case['expected_min_length']} 字符)")
                else:
                    print(f"⚠️ 响应长度可能不足 (< {test_case['expected_min_length']} 字符)")
                
                # 验证响应完整性
                if _is_response_complete_test(response):
                    print("✅ 响应内容看起来完整")
                else:
                    print("⚠️ 响应内容可能不完整")
                
                # 截图保存结果
                client.take_screenshot(f"test_case_{i}_{test_case['name']}.png")
                
                # 确保响应完全处理完毕后再进行下一个测试
                if i < len(test_cases):
                    print("⏳ 响应接收完成，等待5秒后进行下一个测试...")
                    time.sleep(5)  # 增加等待时间确保页面稳定
                
            else:
                print(f"❌ 未接收到响应")
                client.take_screenshot(f"test_case_{i}_failed.png")
                
                # 调试页面结构
                print("🔍 调试页面结构...")
                if hasattr(client, '_debug_page_elements'):
                    client._debug_page_elements()
                break
        
        print(f"\n🎉 测试完成! 共测试了 {len(test_cases)} 个用例")
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        client.take_screenshot("streaming_test_error.png")
        
    finally:
        print("⏱️ 保持浏览器打开30秒以便观察...")
        time.sleep(30)
        client.close()
        print("🔧 测试完成")



if __name__ == "__main__":
    # 运行主要的流式响应测试
    test_streaming_response_enhanced()
    