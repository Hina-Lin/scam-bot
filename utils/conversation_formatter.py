"""
對話格式化工具

此模組提供將對話歷史記錄格式化為不同格式的工具，
以便於LLM模型閱讀和分析。
"""

from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def format_conversation(messages: List[str], format_type: str = "json", user_id: Optional[str] = None) -> str:
    """
    根據指定的格式類型將對話歷史記錄格式化。
    
    Args:
        messages: 對話歷史記錄列表
        format_type: 格式類型，可選 "json" 或 "xml"，默認為 "json"
        user_id: 可選的用戶ID，用於識別主要用戶
        
    Returns:
        str: 格式化後的對話歷史
    """
    if format_type.lower() == "xml":
        return format_history_as_xml(messages, user_id)
    else:  # 默認為 JSON
        return format_history_as_json(messages, user_id)
    
def format_history_as_json(messages: List[str], user_id: Optional[str] = None) -> str:
    """
    將對話歷史記錄格式化為 JSON 格式。
    
    Args:
        messages: 對話歷史記錄列表
        user_id: 可選的用戶ID，用於識別主要用戶
        
    Returns:
        str: 格式化為 JSON 字符串的對話歷史
    """
    parsed_messages = []
    
    # 嘗試解析每一條消息
    for message in messages:
        parsed = _parse_message(message)
        if parsed:
            parsed_messages.append(parsed)
    
    # 構建最終的 JSON 結構
    formatted = {
        "conversation": parsed_messages,
        "metadata": {
            "message_count": len(parsed_messages),
            "current_user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    return json.dumps(formatted, ensure_ascii=False, indent=2)

def format_history_as_xml(messages: List[str], user_id: Optional[str] = None) -> str:
    """
    將對話歷史記錄格式化為 XML 格式。
    
    Args:
        messages: 對話歷史記錄列表
        user_id: 可選的用戶ID，用於識別主要用戶
        
    Returns:
        str: 格式化為 XML 字符串的對話歷史
    """
    root = ET.Element("conversation")
    
    # 添加元數據
    metadata = ET.SubElement(root, "metadata")
    ET.SubElement(metadata, "message_count").text = str(len(messages))
    if user_id:
        ET.SubElement(metadata, "current_user_id").text = user_id
    ET.SubElement(metadata, "timestamp").text = datetime.now().isoformat()
    
    # 添加消息
    messages_elem = ET.SubElement(root, "messages")
    
    for message in messages:
        parsed = _parse_message(message)
        if parsed:
            msg_elem = ET.SubElement(messages_elem, "message")
            
            if "date" in parsed:
                ET.SubElement(msg_elem, "date").text = parsed["date"]
            
            if "time" in parsed:
                ET.SubElement(msg_elem, "time").text = parsed["time"]
            
            if "sender" in parsed:
                ET.SubElement(msg_elem, "sender").text = parsed["sender"]
            
            if "content" in parsed:
                ET.SubElement(msg_elem, "content").text = parsed["content"]
            
            if "type" in parsed:
                ET.SubElement(msg_elem, "type").text = parsed["type"]
    
    # 美化 XML 輸出
    rough_string = ET.tostring(root, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')

def _parse_message(message: str) -> Dict[str, Any]:
    """
    嘗試從原始消息字符串中解析出日期、時間、發送者和內容。
    
    Args:
        message: 原始消息字符串
        
    Returns:
        Dict: 包含解析出的字段的字典，如果無法解析則返回空字典
    """
    result = {}
    
    # 嘗試匹配常見的消息格式
    
    # 1. 嘗試匹配日期行（如 "2025.04.22 星期二"）
    date_match = re.match(r'^(\d{4}\.\d{2}\.\d{2}\s+[\u4e00-\u9fa5]+)$', message)
    if date_match:
        result["type"] = "date_marker"
        result["date"] = date_match.group(1)
        return result
    
    # 2. 嘗試匹配時間、發送者和消息內容（如 "21:49 林國晴 Hina https://docs.google.com/..."）
    msg_match = re.match(r'^(\d{1,2}:\d{2})\s+([\u4e00-\u9fa5\w\s]+?)\s+(.+)$', message)
    if msg_match:
        result["type"] = "message"
        result["time"] = msg_match.group(1)
        result["sender"] = msg_match.group(2).strip()
        result["content"] = msg_match.group(3).strip()
        return result
    
    # 3. 如果無法匹配特定格式，則將整個消息作為內容
    if message.strip():
        result["type"] = "unknown"
        result["content"] = message.strip()
    
    return result


