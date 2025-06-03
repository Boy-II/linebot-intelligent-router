"""
Dialogflow 整合模組
提供真正的 Google Dialogflow 客戶端整合
"""

import os
import json
from typing import Dict, Any, Optional
from google.cloud import dialogflow


class DialogflowClient:
    def __init__(self, project_id: str = None, language_code: str = 'zh-TW'):
        self.project_id = project_id or os.environ.get('DIALOGFLOW_PROJECT_ID')
        self.language_code = language_code
        self.session_client = None
        
        if self.project_id:
            try:
                self.session_client = dialogflow.SessionsClient()
                print(f"Dialogflow 客戶端初始化成功，項目ID: {self.project_id}")
            except Exception as e:
                print(f"Dialogflow 初始化失敗: {e}")
                self.session_client = None
        else:
            print("未設定 DIALOGFLOW_PROJECT_ID，將使用模擬模式")
    
    async def detect_intent(self, text: str, session_id: str, context: Dict = None) -> Dict[str, Any]:
        """檢測用戶意圖"""
        if not self.session_client or not self.project_id:
            # 回退到模擬模式
            return await self._simulate_intent_detection(text)
        
        try:
            # 構建會話路徑
            session = self.session_client.session_path(self.project_id, session_id)
            
            # 構建文本輸入
            text_input = dialogflow.TextInput(text=text, language_code=self.language_code)
            query_input = dialogflow.QueryInput(text=text_input)
            
            # 添加上下文（如果有）
            query_params = None
            if context:
                query_params = dialogflow.QueryParameters()
                contexts = []
                for ctx_name, ctx_data in context.items():
                    context_obj = dialogflow.Context(
                        name=self.session_client.context_path(
                            self.project_id, session_id, ctx_name
                        ),
                        lifespan_count=ctx_data.get('lifespan', 5),
                        parameters=ctx_data.get('parameters', {})
                    )
                    contexts.append(context_obj)
                query_params.contexts = contexts
            
            # 發送請求
            response = self.session_client.detect_intent(
                request={
                    "session": session,
                    "query_input": query_input,
                    "query_params": query_params
                }
            )
            
            return self._format_response(response.query_result)
            
        except Exception as e:
            print(f"Dialogflow API 調用失敗: {e}")
            # 回退到模擬模式
            return await self._simulate_intent_detection(text)
    
    def _format_response(self, query_result) -> Dict[str, Any]:
        """格式化 Dialogflow 回應"""
        parameters = {}
        if query_result.parameters:
            for key, value in query_result.parameters.items():
                parameters[key] = value
        
        return {
            'intent': query_result.intent.display_name,
            'confidence': query_result.intent_detection_confidence,
            'parameters': parameters,
            'fulfillment_text': query_result.fulfillment_text,
            'contexts': [ctx.name for ctx in query_result.output_contexts]
        }
    
    async def _simulate_intent_detection(self, text: str) -> Dict[str, Any]:
        """模擬意圖檢測（當 Dialogflow 不可用時）"""
        text_lower = text.lower()
        
        # 基本關鍵字匹配
        intent_patterns = {
            'form_filling_intent': {
                'keywords': ['填表', '表單', 'form', '填寫'],
                'confidence': 0.9
            },
            'image_generation_intent': {
                'keywords': ['畫圖', '繪圖', '圖片', 'draw', 'image', '生成圖'],
                'confidence': 0.85
            },
            'rss_analysis_intent': {
                'keywords': ['rss', '分析', '訂閱', 'feed', '網址'],
                'confidence': 0.8
            },
            'status_query_intent': {
                'keywords': ['狀態', '進度', 'status', '查詢', '怎麼樣了'],
                'confidence': 0.9
            },
            'help_intent': {
                'keywords': ['幫助', '說明', 'help', '怎麼用', '功能'],
                'confidence': 0.95
            },
            'greeting_intent': {
                'keywords': ['你好', 'hello', 'hi', '嗨', '早安', '晚安'],
                'confidence': 0.8
            },
            'cancel_intent': {
                'keywords': ['取消', '停止', 'cancel', '不要', '算了'],
                'confidence': 0.9
            }
        }
        
        best_match = {'intent': 'unknown', 'confidence': 0.0, 'parameters': {}}
        
        for intent_name, pattern in intent_patterns.items():
            for keyword in pattern['keywords']:
                if keyword in text_lower:
                    if pattern['confidence'] > best_match['confidence']:
                        best_match = {
                            'intent': intent_name,
                            'confidence': pattern['confidence'],
                            'parameters': self._extract_parameters(text, intent_name),
                            'fulfillment_text': self._get_default_response(intent_name),
                            'contexts': []
                        }
                    break
        
        return best_match
    
    def _extract_parameters(self, text: str, intent: str) -> Dict[str, Any]:
        """從文本中提取參數"""
        parameters = {}
        
        if intent == 'image_generation_intent':
            # 提取繪圖描述
            if '畫' in text or 'draw' in text.lower():
                # 簡單提取：去掉觸發詞後的內容作為描述
                for trigger in ['畫圖', '畫', '繪圖', 'draw']:
                    if trigger in text:
                        desc = text.split(trigger, 1)[1].strip()
                        if desc:
                            parameters['prompt'] = desc
                        break
        
        elif intent == 'rss_analysis_intent':
            # 提取 URL
            import re
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
            if urls:
                parameters['url'] = urls[0]
        
        return parameters
    
    def _get_default_response(self, intent: str) -> str:
        """獲取預設回應"""
        responses = {
            'form_filling_intent': '請選擇要填寫的表單類型',
            'image_generation_intent': '請提供圖片描述',
            'rss_analysis_intent': '請提供要分析的 RSS 網址',
            'status_query_intent': '正在查詢您的任務狀態',
            'help_intent': '以下是可用的功能列表',
            'greeting_intent': '您好！我是您的智能助手',
            'cancel_intent': '操作已取消',
            'unknown': '抱歉，我不太理解您的需求'
        }
        return responses.get(intent, '我會盡力協助您')


class DialogflowContextManager:
    """管理 Dialogflow 對話上下文"""
    
    def __init__(self):
        self.user_contexts = {}
    
    def set_context(self, user_id: str, context_name: str, parameters: Dict = None, lifespan: int = 5):
        """設置用戶上下文"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {}
        
        self.user_contexts[user_id][context_name] = {
            'parameters': parameters or {},
            'lifespan': lifespan,
            'created_at': self._get_timestamp()
        }
    
    def get_context(self, user_id: str, context_name: str = None) -> Dict:
        """獲取用戶上下文"""
        if user_id not in self.user_contexts:
            return {}
        
        if context_name:
            return self.user_contexts[user_id].get(context_name, {})
        
        return self.user_contexts[user_id]
    
    def clear_context(self, user_id: str, context_name: str = None):
        """清除用戶上下文"""
        if user_id not in self.user_contexts:
            return
        
        if context_name:
            self.user_contexts[user_id].pop(context_name, None)
        else:
            self.user_contexts[user_id] = {}
    
    def update_context_lifespan(self, user_id: str):
        """更新上下文生命週期"""
        if user_id not in self.user_contexts:
            return
        
        contexts_to_remove = []
        for context_name, context_data in self.user_contexts[user_id].items():
            context_data['lifespan'] -= 1
            if context_data['lifespan'] <= 0:
                contexts_to_remove.append(context_name)
        
        for context_name in contexts_to_remove:
            del self.user_contexts[user_id][context_name]
    
    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()


# 全局實例
dialogflow_client = DialogflowClient()
context_manager = DialogflowContextManager()
