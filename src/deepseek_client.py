#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
from dataclasses import dataclass
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


@dataclass
class ResponseState:
    """响应状态数据类"""
    content: str = ""  # 内容
    last_update_time: float = 0  # 最后更新时间
    stable_count: int = 0  # 稳定计数
    element_selector: str = ""  # 元素选择器
    is_complete: bool = False  # 是否完成


class DeepSeekWebClient:
    # 流式状态管理配置常量 - 平衡性能和准确性
    STABILITY_CHECKS = 4  # 连续稳定检查的次数（减少以提高速度）
    STABILITY_INTERVAL = 0.8  # 稳定性检查之间的秒数（减少间隔）
    MIN_RESPONSE_LENGTH = 50  # 有效响应的最小字符数（确保有意义的内容）
    
    # 响应选择器配置常量 - 基于实际页面结构优化
    RESPONSE_SELECTORS = [
        # DeepSeek实际使用的选择器（最高优先级）
        "p.ds-markdown-paragraph",
        ".ds-markdown-paragraph", 
        "div.ds-markdown.ds-markdown--block",
        "[class*='ds-markdown']",
        
        # 通用markdown选择器
        "[class*='markdown']",
        ".markdown-body",
        
        # 通用AI响应选择器
        "[role='assistant']",
        "[data-role='assistant']",
        "div[data-testid*='assistant-message']",
        "div[class*='assistant-message']",
        
        # 回退消息选择器
        ".message-content",
        ".chat-message:last-child",
        "div[class*='message']:last-child",
        
        # 更广泛的回退选择器
        "div[class*='response']",
        "div[class*='ai']",
        ".response-message",
        ".ai-message"
    ]
    
    def __init__(self, headless=True, timeout=30):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
        # 优化：初始化缓存
        self._cached_message_input = None
        self._cache_timestamp = 0
        
    def clear_cache(self):
        """清理元素缓存"""
        self._cached_message_input = None
        self._cache_timestamp = 0
        logger.debug("已清理元素缓存")
    
    def _get_response_selectors(self):
        """返回优先级排序的DeepSeek响应选择器列表"""
        return self.RESPONSE_SELECTORS.copy()
    
    def _find_response_elements(self):
        """使用多种策略查找响应元素 - 带回退机制"""
        selectors = self._get_response_selectors()
        found_elements = []
        successful_selectors = []
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.debug(f"选择器 '{selector}' 找到 {len(elements)} 个元素")
                    successful_selectors.append(selector)
                    for element in elements:
                        try:
                            if element.is_displayed():
                                content = element.text.strip()
                                if content:  # 只添加有内容的元素
                                    found_elements.append({
                                        'element': element,
                                        'selector': selector,
                                        'content': content
                                    })
                        except Exception as element_error:
                            logger.debug(f"处理元素时出错: {element_error}")
                            continue
                else:
                    logger.debug(f"选择器 '{selector}' 未找到元素")
            except Exception as e:
                logger.debug(f"选择器 '{selector}' 查找失败: {e}")
                continue
        
        # 如果没有找到任何元素，尝试动态发现
        if not found_elements:
            logger.warning("所有预定义选择器都失败，尝试动态发现...")
            found_elements = self._dynamic_selector_discovery()
        
        logger.debug(f"总共找到 {len(found_elements)} 个可见响应元素，"
                    f"成功的选择器: {len(successful_selectors)}")
        return found_elements
    
    def _dynamic_selector_discovery(self):
        """动态发现可能的响应选择器"""
        try:
            # 查找所有包含较长文本的元素
            all_elements = self.driver.find_elements(By.CSS_SELECTOR, "div, p, span, article, section")
            candidates = []
            
            for element in all_elements:
                try:
                    if element.is_displayed():
                        text = element.text.strip()
                        if len(text) > 30:  # 有足够长的文本
                            candidates.append({
                                'element': element,
                                'selector': 'dynamic_discovery',
                                'content': text
                            })
                except:
                    continue
            
            logger.debug(f"动态发现找到 {len(candidates)} 个候选元素")
            return candidates[:10]  # 限制数量避免过多
            
        except Exception as e:
            logger.error(f"动态选择器发现失败: {e}")
            return []
    
    def _validate_response_element(self, element_info):
        """验证元素是否包含实际的AI内容"""
        content = element_info['content']
        
        # 基本验证
        if not content or len(content.strip()) < 3:
            return False
        
        # 跳过明显的用户输入
        user_patterns = ['我', '请', '帮', '如何', '什么', '为什么', '能否', '可以']
        if any(content.startswith(pattern) for pattern in user_patterns):
            return False
        
        # 跳过系统状态消息
        status_keywords = ['正在思考', 'thinking', 'typing', '...', '正在生成', 'generating', '请稍等']
        if any(keyword in content.lower() for keyword in status_keywords):
            return False
        
        # 跳过导航或UI文本
        ui_keywords = ['登录', '注册', '设置', '菜单', '首页', '返回']
        if any(keyword in content for keyword in ui_keywords) and len(content) < 20:
            return False
        
        return True
    
    def _is_ai_content(self, content):
        """判断内容是来自AI还是用户或系统"""
        if not content or len(content.strip()) < 3:
            return False
        
        content = content.strip()
        
        # 明显的用户输入模式
        user_indicators = [
            '我想', '我需要', '我希望', '请帮我', '请告诉我', '请问',
            '能不能', '可不可以', '怎么样', '如何做', '为什么会'
        ]
        
        if any(content.startswith(indicator) for indicator in user_indicators):
            return False
        
        # 系统状态消息
        system_indicators = [
            '正在思考', '正在生成', '正在处理', 'thinking', 'generating', 
            'processing', '请稍等', '加载中', 'loading'
        ]
        
        if any(indicator in content.lower() for indicator in system_indicators):
            return False
        
        # AI响应的积极指标
        ai_indicators = [
            '根据', '基于', '可以看出', '分析显示', '建议', '推荐',
            '总结', '综上', '因此', '所以', '首先', '其次', '最后'
        ]
        
        # 如果包含AI指标，更可能是AI内容
        if any(indicator in content for indicator in ai_indicators):
            return True
        
        # 长度较长且不是明显的用户输入，可能是AI内容
        return len(content) > 20
    
    def _filter_system_messages(self, content):
        """移除状态消息"""
        if not content:
            return content
        
        # 需要过滤的状态消息模式
        status_patterns = [
            r'正在思考\.{3,}',
            r'正在生成\.{3,}',
            r'thinking\.{3,}',
            r'typing\.{3,}',
            r'请稍等\.{3,}',
            r'loading\.{3,}'
        ]
        
        import re
        filtered_content = content
        for pattern in status_patterns:
            filtered_content = re.sub(pattern, '', filtered_content, flags=re.IGNORECASE)
        
        return filtered_content.strip()
    
    def _get_latest_ai_response(self, element_candidates):
        """从多个元素中提取最新的AI响应 - 支持多段落组合"""
        if not element_candidates:
            return None
        
        # 特殊处理：如果找到ds-markdown段落，尝试组合它们
        markdown_paragraphs = []
        other_candidates = []
        
        for candidate in element_candidates:
            if 'ds-markdown-paragraph' in candidate.get('selector', ''):
                content = self._filter_system_messages(candidate['content'])
                if content and len(content.strip()) > 0:
                    markdown_paragraphs.append({
                        'content': content,
                        'element': candidate['element']
                    })
            else:
                other_candidates.append(candidate)
        
        # 如果找到markdown段落，尝试组合它们
        if markdown_paragraphs:
            # 按页面位置排序（通过元素的位置）
            try:
                markdown_paragraphs.sort(key=lambda x: (
                    x['element'].location['y'], 
                    x['element'].location['x']
                ))
            except:
                pass  # 如果无法获取位置，保持原顺序
            
            # 找到最新的AI响应组 - 通过查找最后一组连续的AI内容
            # 首先识别哪些段落属于同一个响应
            response_groups = []
            current_group = []
            last_y_position = None
            
            for para in markdown_paragraphs:
                try:
                    current_y = para['element'].location['y']
                    # 如果Y位置差距较大（超过100像素），认为是新的响应组
                    if last_y_position is not None and abs(current_y - last_y_position) > 100:
                        if current_group:
                            response_groups.append(current_group)
                            current_group = []
                    
                    current_group.append(para)
                    last_y_position = current_y
                except:
                    # 如果无法获取位置，添加到当前组
                    current_group.append(para)
            
            # 添加最后一组
            if current_group:
                response_groups.append(current_group)
            
            # 选择最后一组（最新的响应）
            if response_groups:
                latest_group = response_groups[-1]
                combined_content = '\n'.join([p['content'] for p in latest_group])
                
                # 验证组合内容是否是AI响应
                if self._is_ai_content(combined_content) and len(combined_content.strip()) > 10:
                    logger.debug(f"选择最新响应组，包含 {len(latest_group)} 个段落，总长度: {len(combined_content)}")
                    return combined_content
        
        # 如果markdown段落组合失败，回退到原有逻辑
        valid_candidates = []
        for candidate in other_candidates:
            content = self._filter_system_messages(candidate['content'])
            if self._is_ai_content(content):
                candidate['filtered_content'] = content
                candidate['content_length'] = len(content)
                valid_candidates.append(candidate)
        
        if not valid_candidates:
            logger.debug("未找到有效的AI内容候选")
            return None
        
        # 按内容长度和选择器优先级排序
        def score_candidate(candidate):
            # 选择器优先级分数（索引越小分数越高）
            try:
                selector_priority = self.RESPONSE_SELECTORS.index(candidate['selector'])
                priority_score = len(self.RESPONSE_SELECTORS) - selector_priority
            except ValueError:
                priority_score = 0
            
            # 内容长度分数
            length_score = min(candidate['content_length'] / 100, 10)  # 最高10分
            
            return priority_score + length_score
        
        # 选择得分最高的候选
        best_candidate = max(valid_candidates, key=score_candidate)
        
        logger.debug(f"选择最佳AI响应候选: 选择器='{best_candidate['selector']}', "
                    f"长度={best_candidate['content_length']}")
        
        return best_candidate['filtered_content']
    
    def _monitor_content_changes(self, response_state):
        """跟踪内容随时间的更新 - 带错误恢复"""
        current_time = time.time()
        
        try:
            # 查找当前响应元素
            element_candidates = self._find_response_elements()
            current_content = self._get_latest_ai_response(element_candidates)
            
            if current_content is None:
                # 如果没有找到内容，但之前有内容，可能是临时问题
                if response_state.content:
                    logger.debug("暂时未找到响应内容，保持当前状态")
                return response_state
            
            # 检查内容是否有变化
            if current_content != response_state.content:
                # 内容有更新
                response_state.content = current_content
                response_state.last_update_time = current_time
                response_state.stable_count = 0
                logger.debug(f"检测到内容更新: {len(current_content)} 字符")
            else:
                # 内容稳定
                response_state.stable_count += 1
                logger.debug(f"内容稳定计数: {response_state.stable_count}/{self.STABILITY_CHECKS}")
            
        except Exception as e:
            logger.warning(f"监控内容变化时出错: {e}")
            # 错误恢复：如果已有内容，继续使用；否则尝试基本检测
            if not response_state.content:
                try:
                    # 尝试使用最基本的选择器
                    basic_elements = self.driver.find_elements(By.CSS_SELECTOR, "div, p, span")
                    for element in basic_elements:
                        text = element.text.strip()
                        if len(text) > 50 and self._is_ai_content(text):
                            response_state.content = text
                            response_state.last_update_time = current_time
                            logger.info(f"错误恢复：使用基本选择器找到内容 {len(text)} 字符")
                            break
                except Exception as recovery_error:
                    logger.error(f"错误恢复失败: {recovery_error}")
        
        return response_state
    
    def _detect_completion(self, response_state):
        """确定流式传输何时完成 - 增强版本"""
        current_time = time.time()
        
        # 检查稳定性
        if response_state.stable_count >= self.STABILITY_CHECKS:
            # 检查最小长度要求
            if len(response_state.content) >= self.MIN_RESPONSE_LENGTH:
                # 额外检查：确保响应看起来完整
                if self._is_response_complete(response_state.content):
                    response_state.is_complete = True
                    logger.debug(f"流式响应完成检测: 内容稳定 {response_state.stable_count} 次，长度 {len(response_state.content)}，内容完整")
                else:
                    logger.debug(f"内容稳定但可能不完整，继续等待...")
                    response_state.stable_count = max(0, response_state.stable_count - 2)  # 减少稳定计数，继续等待
            else:
                logger.debug(f"内容稳定但长度不足: {len(response_state.content)} < {self.MIN_RESPONSE_LENGTH}")
        
        # 超长时间无变化也认为完成（防止无限等待）
        if current_time - response_state.last_update_time > 15:  # 15秒无更新
            if len(response_state.content) > 0:
                response_state.is_complete = True
                logger.debug(f"响应超时完成: 15秒无更新，返回现有内容")
        
        return response_state
    
    def _is_response_complete(self, content):
        """判断响应内容是否看起来完整 - 更宽松的检测"""
        if not content:
            return False
        
        # 如果内容长度合理，大多数情况下认为完整
        if len(content) > 100:
            return True
        
        # 检查内容是否以完整的句子结尾
        complete_endings = ['。', '！', '？', '.', '!', '?', '~', '😊', '👍', '✨', '🎉', '：']
        if any(content.strip().endswith(ending) for ending in complete_endings):
            return True
        
        # 如果内容包含关键信息，也认为完整
        if len(content) > 50 and any(keyword in content for keyword in ['分析', '建议', '总结', '综合', '基于']):
            return True
        
        # 默认认为完整（避免过度等待）
        return True
    
    def _wait_for_response_stability(self, timeout=30):
        """等待响应完全稳定（确保不再有更新）"""
        logger.info("等待响应完全稳定...")
        start_time = time.time()
        last_content = ""
        stable_duration = 0
        required_stable_duration = 3  # 需要3秒完全无变化
        
        while time.time() - start_time < timeout:
            try:
                # 获取当前响应内容
                element_candidates = self._find_response_elements()
                current_content = self._get_latest_ai_response(element_candidates)
                
                if current_content == last_content:
                    stable_duration += 1
                    if stable_duration >= required_stable_duration:
                        logger.info(f"响应已完全稳定 {stable_duration} 秒")
                        return True
                else:
                    stable_duration = 0
                    last_content = current_content
                    logger.debug(f"检测到内容变化，重置稳定计时器")
                
                time.sleep(1)
                
            except Exception as e:
                logger.debug(f"稳定性检测出错: {e}")
                time.sleep(1)
        
        logger.warning("响应稳定性检测超时")
        return False
    
    def _handle_timeout(self, response_state, elapsed_time, timeout):
        """优雅地管理超时场景"""
        if response_state.content and len(response_state.content) >= self.MIN_RESPONSE_LENGTH:
            logger.warning(f"响应超时但有有效内容，返回部分响应: {len(response_state.content)} 字符")
            response_state.is_complete = True
            return response_state
        
        logger.warning(f"响应超时且无有效内容，耗时: {elapsed_time:.2f}秒")
        return response_state
    
    def _log_response_progress(self, response_state, elapsed_time):
        """记录流式进度更新"""
        content_length = len(response_state.content)
        logger.info(f"流式响应进度: {content_length} 字符, "
                   f"稳定计数: {response_state.stable_count}/{self.STABILITY_CHECKS}, "
                   f"耗时: {elapsed_time:.1f}秒")
    
    def _debug_page_elements(self):
        """分析页面结构以进行故障排除"""
        logger.info("开始调试页面元素结构...")
        
        try:
            # 分析所有可能的消息容器
            all_elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
            
            message_candidates = []
            for element in all_elements:
                try:
                    tag_name = element.tag_name
                    class_name = element.get_attribute('class') or ''
                    data_testid = element.get_attribute('data-testid') or ''
                    role = element.get_attribute('role') or ''
                    text = element.text.strip()
                    
                    # 查找可能的消息元素
                    if (any(keyword in class_name.lower() for keyword in ['message', 'chat', 'response', 'assistant']) or
                        any(keyword in data_testid.lower() for keyword in ['message', 'chat', 'response', 'assistant']) or
                        role in ['assistant', 'user'] or
                        (len(text) > 10 and len(text) < 2000)):  # 合理的文本长度
                        
                        message_candidates.append({
                            'tag': tag_name,
                            'class': class_name[:50] + '...' if len(class_name) > 50 else class_name,
                            'testid': data_testid[:30] + '...' if len(data_testid) > 30 else data_testid,
                            'role': role,
                            'text_length': len(text),
                            'text_preview': text[:100] + '...' if len(text) > 100 else text,
                            'is_visible': element.is_displayed()
                        })
                except:
                    continue
            
            logger.info(f"找到 {len(message_candidates)} 个可能的消息元素:")
            for i, candidate in enumerate(message_candidates[:15]):  # 只显示前15个
                logger.info(f"  {i+1}. <{candidate['tag']}> "
                           f"class='{candidate['class']}' "
                           f"testid='{candidate['testid']}' "
                           f"role='{candidate['role']}' "
                           f"visible={candidate['is_visible']} "
                           f"text_len={candidate['text_length']}")
                if candidate['text_preview'] and candidate['is_visible']:
                    logger.info(f"     预览: {candidate['text_preview']}")
                    
        except Exception as e:
            logger.error(f"调试页面元素时出错: {e}")
    
    def _capture_debug_screenshot(self, filename_suffix="debug"):
        """截图进行可视化调试"""
        try:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"{filename_suffix}_{timestamp}.png"
            screenshot_path = get_screenshot_path(filename)
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"调试截图已保存: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"调试截图失败: {e}")
            return None
    
    def _handle_response_errors(self, error, context="unknown"):
        """统一的响应错误处理"""
        error_msg = str(error)
        
        # 记录详细错误信息
        logger.error(f"响应处理错误 [{context}]: {error_msg}")
        
        # 根据错误类型采取不同的恢复策略
        if "stale element reference" in error_msg.lower():
            logger.info("检测到过期元素引用，清理缓存并重试")
            self.clear_cache()
            return "retry"
        
        elif "no such element" in error_msg.lower():
            logger.info("元素未找到，尝试动态发现")
            return "dynamic_discovery"
        
        elif "timeout" in error_msg.lower():
            logger.info("超时错误，尝试延长等待时间")
            return "extend_timeout"
        
        elif "javascript error" in error_msg.lower():
            logger.info("JavaScript错误，尝试刷新页面状态")
            return "refresh_page"
        
        else:
            logger.warning("未知错误类型，使用默认恢复策略")
            return "default_recovery"

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
            # 优化：页面导航时清理缓存
            self.clear_cache()
            self.driver.get("https://chat.deepseek.com/sign_in")
            time.sleep(2)
            
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
            time.sleep(1)
            
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
            time.sleep(1)
            
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
            time.sleep(1)
            
            # 检查是否登录成功
            current_url = self.driver.current_url
            if "chat.deepseek.com" in current_url and "sign_in" not in current_url:
                logger.info("登录成功！")
                
                # 登录成功后，立即选中功能按钮
                time.sleep(2)  # 等待聊天页面完全加载
                self.select_feature_buttons()
                
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
    
    def select_feature_buttons(self):
        """选中功能按钮：深度思考(R1)和联网搜索"""
        try:
            logger.info("正在配置功能按钮...")
            
            # 查找所有按钮
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
            
            selected_buttons = []
            
            for button in buttons:
                try:
                    button_text = button.text.strip()
                    
                    # 选中"深度思考 (R1)"按钮
                    if "深度思考" in button_text and "R1" in button_text:
                        # 检查按钮是否已经被选中
                        button_classes = button.get_attribute("class") or ""
                        is_selected = any(keyword in button_classes.lower() for keyword in ["selected", "active", "checked"])
                        
                        if not is_selected:
                            self.driver.execute_script("arguments[0].scrollIntoView();", button)
                            time.sleep(0.5)
                            button.click()
                            logger.info("✅ 已选中'深度思考 (R1)'按钮")
                            selected_buttons.append("深度思考 (R1)")
                            time.sleep(1)
                        else:
                            logger.info("ℹ️ '深度思考 (R1)'按钮已经是选中状态")
                            selected_buttons.append("深度思考 (R1)")
                    
                    # 选中"联网搜索"按钮
                    elif "联网搜索" in button_text:
                        # 检查按钮是否已经被选中
                        button_classes = button.get_attribute("class") or ""
                        is_selected = any(keyword in button_classes.lower() for keyword in ["selected", "active", "checked"])
                        
                        if not is_selected:
                            self.driver.execute_script("arguments[0].scrollIntoView();", button)
                            time.sleep(0.5)
                            button.click()
                            logger.info("✅ 已选中'联网搜索'按钮")
                            selected_buttons.append("联网搜索")
                            time.sleep(1)
                        else:
                            logger.info("ℹ️ '联网搜索'按钮已经是选中状态")
                            selected_buttons.append("联网搜索")
                            
                except Exception as e:
                    logger.debug(f"处理按钮时出错: {e}")
                    continue
            
            if selected_buttons:
                logger.info(f"✅ 功能按钮配置完成，已选中: {', '.join(selected_buttons)}")
            else:
                logger.warning("⚠️ 未找到或选中任何功能按钮")
            
        except Exception as e:
            logger.warning(f"配置功能按钮时出现错误: {e}")
            # 不抛出异常，继续执行
    
    def send_message(self, message):
        """发送消息到DeepSeek chat"""
        if not self.driver:
            logger.error("请先初始化驱动并登录")
            return None
            
        try:
            logger.info(f"正在发送消息: {message}")
            
            # 优化：使用缓存检查是否已有输入框
            if hasattr(self, '_cached_message_input') and self._cached_message_input:
                try:
                    # 验证缓存的元素是否仍然有效
                    self._cached_message_input.is_displayed()
                    message_input = self._cached_message_input
                    logger.debug("使用缓存的输入框")
                except:
                    self._cached_message_input = None
            
            if not hasattr(self, '_cached_message_input') or not self._cached_message_input:
                # 优化：使用DeepSeek页面的正确选择器
                message_selectors = [
                    "textarea#chat-input",  # 使用ID选择器，最精确
                    "textarea[placeholder*='给 DeepSeek 发送消息']",  # 使用placeholder选择器
                    "textarea"  # 备用通用选择器
                ]
                
                # 优化：使用更短的超时时间和并行查找策略
                message_input = self._find_message_input_optimized(message_selectors)
                
                if message_input:
                    # 缓存找到的输入框
                    self._cached_message_input = message_input
                else:
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
            
            # 记录发送前的页面状态和时间戳
            pre_send_content = self._get_current_page_content_snapshot()
            send_timestamp = time.time()
            
            # 等待响应 - 使用增强版本
            response = self.wait_for_response_enhanced(pre_send_content, send_timestamp)
            return response
            
        except Exception as e:
            logger.error(f"发送消息时出现错误: {e}")
            return None

    def _find_message_input_optimized(self, selectors, max_timeout=10):
        """
        优化的消息输入框查找方法
        使用更短的超时时间和更高效的查找策略
        """
        import threading
        import queue
        import time
        
        result_queue = queue.Queue()
        start_time = time.time()
        
        def find_element_with_timeout(selector, timeout):
            """在指定超时时间内查找元素"""
            try:
                # 优化：先尝试快速查找，再使用等待
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed() and element.is_enabled():
                        result_queue.put((selector, element))
                        return True
                except NoSuchElementException:
                    pass
                
                # 如果快速查找失败，使用等待
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                result_queue.put((selector, element))
                return True
            except (TimeoutException, NoSuchElementException):
                return False
        
        # 优化：使用递减的超时时间，优先选择器使用更长时间
        threads = []
        
        for i, selector in enumerate(selectors):
            # 根据优先级设置递减的超时时间
            timeout = max(1, max_timeout - i * 0.5)  # 从max_timeout递减到1秒
            
            thread = threading.Thread(
                target=find_element_with_timeout,
                args=(selector, timeout)
            )
            thread.daemon = True
            threads.append(thread)
            thread.start()
        
        # 等待第一个成功的线程或所有线程完成
        try:
            # 等待第一个结果，最多等待max_timeout秒
            selector, element = result_queue.get(timeout=max_timeout)
            elapsed_time = time.time() - start_time
            logger.debug(f"找到输入框，使用选择器: {selector}，耗时: {elapsed_time:.2f}秒")
            return element
        except queue.Empty:
            elapsed_time = time.time() - start_time
            logger.debug(f"所有选择器查找超时，总耗时: {elapsed_time:.2f}秒")
            return None
        finally:
            # 确保所有线程都已启动
            for thread in threads:
                if thread.is_alive():
                    thread.join(timeout=0.1)
    
    def wait_for_response(self, timeout=120):
        """等待AI流式响应完成 - 增强版本"""
        logger.info("开始等待AI流式响应...")
        start_time = time.time()
        
        # 初始化响应状态
        response_state = ResponseState()
        
        # 初始等待，让页面有时间开始加载响应
        time.sleep(1)
        
        while time.time() - start_time < timeout:
            try:
                elapsed_time = time.time() - start_time
                
                # 监控内容变化
                response_state = self._monitor_content_changes(response_state)
                
                # 检测是否完成
                response_state = self._detect_completion(response_state)
                
                # 记录进度（每5秒记录一次）
                if int(elapsed_time) % 5 == 0 and elapsed_time > 0:
                    self._log_response_progress(response_state, elapsed_time)
                
                # 如果检测到完成，返回结果
                if response_state.is_complete:
                    logger.info(f"✅ AI流式响应完成! 最终长度: {len(response_state.content)} 字符, "
                               f"耗时: {elapsed_time:.2f}秒")
                    return response_state.content
                
                # 等待下一次检查
                time.sleep(self.STABILITY_INTERVAL)
                
            except Exception as e:
                logger.error(f"等待响应时出现错误: {e}")
                # 调试页面结构
                self._debug_page_elements()
                # 截图调试
                self._capture_debug_screenshot("response_error")
                break
        
        # 处理超时情况
        elapsed_time = time.time() - start_time
        response_state = self._handle_timeout(response_state, elapsed_time, timeout)
        
        if response_state.content:
            logger.warning(f"⚠️ 响应超时但返回部分内容: {len(response_state.content)} 字符")
            return response_state.content
        else:
            logger.error("❌ 响应超时且未收到任何有效内容")
            # 调试页面结构以帮助排查问题
            self._debug_page_elements()
            self._capture_debug_screenshot("response_timeout")
            return None
    
    def _get_current_page_content_snapshot(self):
        """获取当前页面内容快照，用于识别新响应"""
        try:
            # 获取所有可能的响应元素
            element_candidates = self._find_response_elements()
            
            # 提取所有现有内容
            existing_content = []
            for candidate in element_candidates:
                content = candidate.get('content', '').strip()
                if content and len(content) > 10:
                    existing_content.append(content)
            
            return {
                'timestamp': time.time(),
                'content_hashes': [hash(content) for content in existing_content],
                'total_elements': len(element_candidates)
            }
        except Exception as e:
            logger.debug(f"获取页面快照失败: {e}")
            return {'timestamp': time.time(), 'content_hashes': [], 'total_elements': 0}
    
    def wait_for_response_enhanced(self, pre_send_snapshot, send_timestamp, timeout=120):
        """增强的响应等待方法 - 确保获取新响应"""
        logger.info("开始等待AI流式响应...")
        start_time = time.time()
        
        # 初始化响应状态
        response_state = ResponseState()
        
        # 等待页面开始响应（新内容出现）
        new_content_detected = False
        initial_wait_timeout = 30  # 最多等待30秒检测到新内容
        
        logger.info("等待新响应内容出现...")
        while time.time() - start_time < initial_wait_timeout and not new_content_detected:
            try:
                current_snapshot = self._get_current_page_content_snapshot()
                
                # 检查是否有新内容
                if (current_snapshot['total_elements'] > pre_send_snapshot['total_elements'] or
                    len(current_snapshot['content_hashes']) > len(pre_send_snapshot['content_hashes'])):
                    
                    # 检查是否有新的内容哈希
                    new_hashes = set(current_snapshot['content_hashes']) - set(pre_send_snapshot['content_hashes'])
                    if new_hashes:
                        new_content_detected = True
                        logger.info(f"检测到新响应内容! 新增 {len(new_hashes)} 个内容块")
                        break
                
                time.sleep(1)  # 每秒检查一次
                
            except Exception as e:
                logger.debug(f"检测新内容时出错: {e}")
                time.sleep(1)
        
        if not new_content_detected:
            logger.warning("未检测到新响应内容，使用标准等待模式")
        
        # 开始标准的流式响应等待
        while time.time() - start_time < timeout:
            try:
                elapsed_time = time.time() - start_time
                
                # 监控内容变化 - 只获取发送时间戳之后的内容
                response_state = self._monitor_content_changes_enhanced(response_state, send_timestamp)
                
                # 检测是否完成
                response_state = self._detect_completion(response_state)
                
                # 记录进度（每5秒记录一次）
                if int(elapsed_time) % 5 == 0 and elapsed_time > 0:
                    self._log_response_progress(response_state, elapsed_time)
                
                # 如果检测到完成，返回结果
                if response_state.is_complete:
                    logger.info(f"✅ AI流式响应完成! 最终长度: {len(response_state.content)} 字符, "
                               f"耗时: {elapsed_time:.2f}秒")
                    return response_state.content
                
                # 等待下一次检查
                time.sleep(self.STABILITY_INTERVAL)
                
            except Exception as e:
                logger.error(f"等待响应时出现错误: {e}")
                break
        
        # 处理超时情况
        elapsed_time = time.time() - start_time
        response_state = self._handle_timeout(response_state, elapsed_time, timeout)
        
        if response_state.content:
            logger.warning(f"⚠️ 响应超时但返回部分内容: {len(response_state.content)} 字符")
        else:
            logger.error("❌ 响应超时且未获取到内容")
        
        return response_state.content if response_state.content else None
    
    def _monitor_content_changes_enhanced(self, response_state, send_timestamp):
        """增强的内容变化监控 - 只关注新响应"""
        current_time = time.time()
        
        try:
            # 查找当前响应元素
            element_candidates = self._find_response_elements()
            
            # 过滤出可能的新响应（基于时间戳和内容特征）
            new_response_candidates = []
            for candidate in element_candidates:
                content = candidate.get('content', '').strip()
                if content and len(content) > 10:
                    # 简单的启发式：如果内容看起来是新的AI响应
                    if self._is_likely_new_response(content, send_timestamp):
                        new_response_candidates.append(candidate)
            
            # 获取最新的AI响应
            current_content = self._get_latest_ai_response(new_response_candidates)
            
            if current_content is None:
                # 如果没有找到新内容，但之前有内容，可能是临时问题
                if response_state.content:
                    logger.debug("暂时未找到新响应内容，保持当前状态")
                return response_state
            
            # 检查内容是否有变化
            if current_content != response_state.content:
                # 内容有更新
                response_state.content = current_content
                response_state.last_update_time = current_time
                response_state.stable_count = 0
                logger.debug(f"检测到新响应内容更新: {len(current_content)} 字符")
            else:
                # 内容稳定
                response_state.stable_count += 1
            
            return response_state
            
        except Exception as e:
            logger.error(f"监控内容变化时出错: {e}")
            return response_state
    
    def _is_likely_new_response(self, content, send_timestamp):
        """判断内容是否可能是新的AI响应"""
        # 基本的启发式规则
        
        # 1. 内容不应该是明显的用户输入
        if content.startswith(('你好，请', '分析一下', '用Python写', '我想', '请帮')):
            return False
        
        # 2. 内容应该看起来像AI响应
        ai_indicators = [
            '你好', '我是', '我可以', '根据', '基于', '分析', '建议', 
            '总结', '首先', '其次', '最后', '因此', '所以', '简单来说',
            'DeepSeek', '深度求索', '很高兴', '认识你'
        ]
        
        has_ai_indicators = any(indicator in content for indicator in ai_indicators)
        
        # 3. 内容长度合理
        reasonable_length = 20 <= len(content) <= 5000
        
        return has_ai_indicators and reasonable_length
    
    # def debug_page_elements(self):
    #     """调试页面元素，帮助识别正确的选择器"""
    #     logger.info("开始调试页面元素...")
        
    #     try:
    #         # 查找所有可能的消息容器
    #         all_elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
            
    #         message_candidates = []
    #         for element in all_elements:
    #             try:
    #                 tag_name = element.tag_name
    #                 class_name = element.get_attribute('class') or ''
    #                 data_testid = element.get_attribute('data-testid') or ''
    #                 role = element.get_attribute('role') or ''
    #                 text = element.text.strip()
                    
    #                 # 查找可能的消息元素
    #                 if (any(keyword in class_name.lower() for keyword in ['message', 'chat', 'response']) or
    #                     any(keyword in data_testid.lower() for keyword in ['message', 'chat', 'response']) or
    #                     role in ['assistant', 'user'] or
    #                     (len(text) > 10 and len(text) < 2000)):  # 合理的文本长度
                        
    #                     message_candidates.append({
    #                         'tag': tag_name,
    #                         'class': class_name,
    #                         'testid': data_testid,
    #                         'role': role,
    #                         'text_length': len(text),
    #                         'text_preview': text[:100] + '...' if len(text) > 100 else text
    #                     })
    #             except:
    #                 continue
            
    #         logger.info(f"找到 {len(message_candidates)} 个可能的消息元素:")
    #         for i, candidate in enumerate(message_candidates[:10]):  # 只显示前10个
    #             logger.info(f"  {i+1}. <{candidate['tag']}> class='{candidate['class']}' "
    #                        f"testid='{candidate['testid']}' role='{candidate['role']}' "
    #                        f"text_len={candidate['text_length']}")
    #             if candidate['text_preview']:
    #                 logger.info(f"     text: {candidate['text_preview']}")
                    
    #     except Exception as e:
    #         logger.error(f"调试页面元素时出错: {e}")
    
    # def get_conversation_history(self):
    #     """获取对话历史"""
    #     try:
    #         messages = []
    #         message_elements = self.driver.find_elements(By.CSS_SELECTOR, ".message, .chat-message, [data-testid='message']")
            
    #         for element in message_elements:
    #             content = element.text.strip()
    #             if content:
    #                 messages.append({
    #                     'content': content,
    #                     'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    #                 })
            
    #         return messages
    #     except Exception as e:
    #         logger.error(f"获取对话历史时出现错误: {e}")
    #         return []
    
    def start_new_chat(self):
        """开始新对话"""
        try:
            logger.info("正在开始新对话...")
            
            # 清理缓存，因为页面可能会变化
            self.clear_cache()
            
            # 更全面的新对话按钮选择器
            new_chat_selectors = [
                # DeepSeek特定选择器
                "button[data-testid='new-chat']",
                "button[class*='new-chat']",
                "[data-testid*='new-chat']",
                "[class*='new-chat']",
                
                # 通用按钮选择器
                "button:contains('新对话')",
                "button:contains('New Chat')",
                "button:contains('新建对话')",
                "button:contains('开始新对话')",
                
                # 图标按钮
                "button[title*='新对话']",
                "button[aria-label*='新对话']",
                "button[title*='New Chat']",
                "button[aria-label*='New Chat']"
            ]
            
            # 首先尝试CSS选择器
            for selector in new_chat_selectors:
                try:
                    if ":contains(" in selector:
                        continue  # 跳过contains选择器，稍后处理
                    
                    new_chat_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if new_chat_button.is_displayed() and new_chat_button.is_enabled():
                        self.driver.execute_script("arguments[0].scrollIntoView();", new_chat_button)
                        time.sleep(0.5)
                        new_chat_button.click()
                        time.sleep(3)  # 等待页面响应
                        logger.info("新对话已开始")
                        return True
                except (NoSuchElementException, Exception):
                    continue
            
            # 尝试通过文本查找按钮（基于实际界面）
            try:
                # 查找所有可点击元素，包括button、div等
                clickable_elements = self.driver.find_elements(By.CSS_SELECTOR, "button, div[role='button'], a, span")
                logger.info(f"找到 {len(clickable_elements)} 个可点击元素")
                
                for element in clickable_elements:
                    try:
                        element_text = element.text.strip()
                        
                        # 检查是否包含"开启新对话"文本（基于界面截图）
                        if any(keyword in element_text for keyword in ['开启新对话', '新对话', 'New Chat']):
                            if element.is_displayed() and element.is_enabled():
                                logger.info(f"找到新对话按钮: '{element_text}'")
                                
                                # 滚动到元素位置
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                time.sleep(1)
                                
                                # 尝试点击
                                try:
                                    element.click()
                                    logger.info("✅ 新对话按钮点击成功")
                                except:
                                    # 如果普通点击失败，尝试JavaScript点击
                                    self.driver.execute_script("arguments[0].click();", element)
                                    logger.info("✅ 通过JavaScript点击新对话按钮")
                                
                                # 等待页面响应
                                time.sleep(3)
                                logger.info("✅ 新对话已开始")
                                return True
                                
                    except Exception as e:
                        logger.debug(f"检查元素时出错: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"通过文本查找新对话按钮失败: {e}")
            
            # 最后尝试：查找可能的加号按钮或其他新建按钮
            try:
                plus_selectors = [
                    "button[class*='plus']",
                    "button[class*='add']",
                    "button[class*='create']",
                    "[class*='icon-plus']",
                    "[class*='icon-add']"
                ]
                
                for selector in plus_selectors:
                    try:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if button.is_displayed() and button.is_enabled():
                            logger.info(f"尝试点击可能的新建按钮: {selector}")
                            button.click()
                            time.sleep(3)
                            logger.info("可能已开始新对话")
                            return True
                    except:
                        continue
                        
            except Exception as e:
                logger.debug(f"查找加号按钮失败: {e}")
            
            logger.warning("未找到新对话按钮，将继续使用当前对话")
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