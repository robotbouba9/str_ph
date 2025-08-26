#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
نظام حفظ تاريخ المحادثات البرمجية
"""

import json
import os
from datetime import datetime

class ChatHistory:
    def __init__(self, history_file='chat_history.json'):
        self.history_file = history_file
        self.history = self.load_history()
    
    def load_history(self):
        """تحميل تاريخ المحادثات من الملف"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        """حفظ تاريخ المحادثات في الملف"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving chat history: {e}")
    
    def add_conversation(self, user_message, ai_response):
        """إضافة محادثة جديدة"""
        conversation = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'ai_response': ai_response,
            'type': 'programming_assistance'
        }
        
        self.history.append(conversation)
        
        # الاحتفاظ بآخر 100 محادثة فقط
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        self.save_history()
    
    def get_recent_conversations(self, limit=10):
        """الحصول على المحادثات الأخيرة"""
        return self.history[-limit:] if self.history else []
    
    def search_conversations(self, keyword):
        """البحث في المحادثات"""
        results = []
        for conv in self.history:
            if keyword.lower() in conv['user_message'].lower() or keyword.lower() in conv['ai_response'].lower():
                results.append(conv)
        return results
    
    def get_programming_topics(self):
        """استخراج المواضيع البرمجية الشائعة"""
        topics = {}
        programming_keywords = [
            'python', 'flask', 'database', 'sql', 'html', 'css', 'javascript',
            'function', 'class', 'route', 'template', 'form', 'validation',
            'error', 'bug', 'fix', 'optimize', 'performance'
        ]
        
        for conv in self.history:
            message = conv['user_message'].lower()
            for keyword in programming_keywords:
                if keyword in message:
                    topics[keyword] = topics.get(keyword, 0) + 1
        
        return sorted(topics.items(), key=lambda x: x[1], reverse=True)