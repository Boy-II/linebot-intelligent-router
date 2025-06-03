"""
OpenAI LLM 客戶端模組
提供 LLM 回退處理功能
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional


class OpenAIClient:
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
        if not self.api_key:
            print("警告: 未設定 OPENAI_API_KEY，LLM 回退功能將無法使用")
    
    async def analyze_intent(self, message_text: str) -> Dict[str, Any]:
        """使用 LLM 分析用戶意圖"""
        if not self.api_key:
            return self._get_fallback_analysis(message_text)
        
        prompt = self._build_analysis_prompt(message_text)
        
        try:
            response = await self._call_openai_api(prompt)
            return self._parse_llm_response(response, message_text)
        except Exception as e:
            print(f"OpenAI API 調用失敗: {e}")
            return self._get_fallback_analysis(message_text)
    
    def _build_analysis_prompt(self, message_text: str) -> str:
        """構建分析提示詞"""
        return f"""
你是一個智能任務分析器。用戶的請求無法被預設的指令系統和對話流程處理。
請分析用戶的需求並判斷是否可以執行。

可執行的任務類型包括：
1. 資料分析和處理 (data_analysis)
2. 文檔生成和轉換 (document_processing)
3. 網頁內容抓取和分析 (web_scraping)
4. 表單填寫和資料收集 (form_processing)
5. 狀態查詢和報告生成 (status_reporting)
6. 檔案格式轉換 (file_conversion)
7. 圖片生成和處理 (image_processing)
8. RSS 訂閱源分析 (rss_analysis)
9. 自動化任務和工作流 (automation)
10. 其他合理的數據處理任務 (general_processing)

用戶請求："{message_text}"

請嚴格以JSON格式回應，不要包含任何其他文字：
{{
  "can_handle": true/false,
  "task_type": "從上述類型中選擇最合適的",
  "task_description": "簡潔的任務描述",
  "parameters": {{"key": "value"}},
  "workflow_suggestion": "建議的 n8n 工作流類型",
  "user_confirmation_needed": true/false,
  "estimated_time": "預估處理時間",
  "confidence": 0.0-1.0,
  "reason": "分析理由"
}}

如果無法處理，請將 can_handle 設為 false 並在 reason 中說明原因。
"""
    
    async def _call_openai_api(self, prompt: str) -> str:
        """調用 OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一個專業的任務分析器，專門判斷用戶請求是否可以通過自動化流程處理。請嚴格按照JSON格式回應。"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    raise Exception(f"OpenAI API 錯誤: {response.status}")
    
    def _parse_llm_response(self, response: str, original_message: str) -> Dict[str, Any]:
        """解析 LLM 回應"""
        try:
            # 嘗試解析 JSON
            analysis = json.loads(response.strip())
            
            # 驗證必要欄位
            required_fields = ['can_handle', 'task_type', 'task_description']
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"缺少必要欄位: {field}")
            
            # 添加原始訊息
            analysis['original_message'] = original_message
            
            # 設定預設值
            analysis.setdefault('parameters', {})
            analysis.setdefault('workflow_suggestion', 'llm_general_processor')
            analysis.setdefault('user_confirmation_needed', True)
            analysis.setdefault('estimated_time', '1-3分鐘')
            analysis.setdefault('confidence', 0.7)
            analysis.setdefault('reason', '基於 LLM 分析')
            
            return analysis
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"解析 LLM 回應失敗: {e}, 回應內容: {response}")
            return self._get_fallback_analysis(original_message)
    
    def _get_fallback_analysis(self, message_text: str) -> Dict[str, Any]:
        """獲取回退分析結果"""
        # 簡單的關鍵字分析
        message_lower = message_text.lower()
        
        # 檢查是否包含 URL
        import re
        has_url = bool(re.search(r'http[s]?://\S+', message_text))
        
        if has_url:
            return {
                "can_handle": True,
                "task_type": "web_scraping",
                "task_description": "網頁內容抓取和分析",
                "parameters": {"url": re.search(r'http[s]?://\S+', message_text).group()},
                "workflow_suggestion": "web_content_processor",
                "user_confirmation_needed": True,
                "estimated_time": "1-2分鐘",
                "confidence": 0.6,
                "reason": "檢測到URL，建議網頁處理",
                "original_message": message_text
            }
        
        # 檢查常見任務關鍵字
        task_keywords = {
            "檔案": "file_conversion",
            "文檔": "document_processing", 
            "分析": "data_analysis",
            "轉換": "file_conversion",
            "報告": "status_reporting",
            "整理": "data_analysis"
        }
        
        for keyword, task_type in task_keywords.items():
            if keyword in message_text:
                return {
                    "can_handle": True,
                    "task_type": task_type,
                    "task_description": f"基於關鍵字 '{keyword}' 的任務處理",
                    "parameters": {"original_message": message_text},
                    "workflow_suggestion": "llm_general_processor",
                    "user_confirmation_needed": True,
                    "estimated_time": "1-3分鐘",
                    "confidence": 0.5,
                    "reason": f"檢測到關鍵字: {keyword}",
                    "original_message": message_text
                }
        
        # 無法識別的請求
        return {
            "can_handle": False,
            "task_type": "unknown",
            "task_description": "無法識別的任務類型",
            "parameters": {},
            "workflow_suggestion": None,
            "user_confirmation_needed": False,
            "estimated_time": "無法估算",
            "confidence": 0.1,
            "reason": "無法識別任務類型，建議使用具體的指令",
            "original_message": message_text,
            "alternatives": [
                "嘗試使用 /說明 查看可用功能",
                "使用更具體的描述，例如：'分析這個網址的內容'",
                "使用指令格式，例如：/分析RSS [網址]"
            ]
        }


class LLMTaskValidator:
    """LLM 任務驗證器"""
    
    @staticmethod
    def validate_task(analysis: Dict[str, Any]) -> Dict[str, Any]:
        """驗證 LLM 分析的任務是否合理"""
        
        # 檢查信心度
        confidence = analysis.get('confidence', 0)
        if confidence < 0.4:
            analysis['can_handle'] = False
            analysis['reason'] = "任務識別信心度過低"
        
        # 檢查是否有具體參數
        parameters = analysis.get('parameters', {})
        task_type = analysis.get('task_type', '')
        
        # 對特定任務類型進行額外驗證
        if task_type == 'web_scraping' and not parameters.get('url'):
            # 嘗試從原始訊息中提取 URL
            original_message = analysis.get('original_message', '')
            import re
            urls = re.findall(r'http[s]?://\S+', original_message)
            if urls:
                parameters['url'] = urls[0]
            else:
                analysis['user_confirmation_needed'] = True
                analysis['reason'] = "需要用戶提供網址"
        
        # 確保工作流建議合理
        workflow_mapping = {
            'data_analysis': 'data_processor',
            'document_processing': 'document_processor', 
            'web_scraping': 'web_content_processor',
            'form_processing': 'form_processor',
            'rss_analysis': 'rss_processor',
            'image_processing': 'image_processor',
            'file_conversion': 'file_converter',
            'automation': 'automation_processor'
        }
        
        if task_type in workflow_mapping:
            analysis['workflow_suggestion'] = workflow_mapping[task_type]
        
        return analysis
    
    @staticmethod
    def generate_confirmation_message(analysis: Dict[str, Any]) -> str:
        """生成確認訊息"""
        task_desc = analysis.get('task_description', '未知任務')
        estimated_time = analysis.get('estimated_time', '未知')
        confidence = analysis.get('confidence', 0)
        
        confidence_emoji = "🔴" if confidence < 0.5 else "🟡" if confidence < 0.8 else "🟢"
        
        message = f"""
{confidence_emoji} 任務分析結果

📋 任務描述：{task_desc}
⏱️ 預估時間：{estimated_time}
📊 信心度：{confidence:.1%}

是否確認執行此任務？

✅ 確認執行
❌ 取消任務
❓ 需要更多說明
"""
        return message.strip()


# 全局實例
llm_client = OpenAIClient()
task_validator = LLMTaskValidator()
