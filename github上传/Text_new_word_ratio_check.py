import re
import os
from typing import Set

class VocabularyAnalyzer:
    def __init__(self, proficient_vocab_file="proficient_vocabulary.txt", 
                 Unfamiliar_file="Unfamiliar_words.txt"):
        self.proficient_vocab_file = proficient_vocab_file
        self.Unfamiliar_file = Unfamiliar_file
        
        # 初始化词汇文件
        if not os.path.exists(self.proficient_vocab_file):
            open(self.proficient_vocab_file, 'w').close()
        if not os.path.exists(self.Unfamiliar_file):
            open(self.Unfamiliar_file, 'w').close()
    
    def extract_words(self, text: str) -> Set[str]:
        """从文本中提取所有英文单词，返回小写不重复的集合"""
        # 匹配英文单词的正则表达式
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return {word.lower() for word in words}
    
    def read_vocabulary_file(self, file_path: str) -> Set[str]:
        """从词汇文件中读取所有单词，返回小写不重复的集合"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return {line.strip().lower() for line in f if line.strip()}
        except:
            return set()
    
    def update_proficient_vocabulary(self, text: str):
        """分析文本，更新熟练词汇表"""
        # 提取文本中的单词
        new_words = self.extract_words(text)
        
        # 读取现有的熟练词汇
        proficient_words = self.read_vocabulary_file(self.proficient_vocab_file)
        
        # 读取存档文件中的单词
        Unfamiliar_words = self.read_vocabulary_file(self.Unfamiliar_file)
        
        # 计算要添加的新词(不在熟练词汇中且不在存档中的词)
        words_to_add = new_words - proficient_words - Unfamiliar_words
        
        # 将新词写入熟练词汇文件
        if words_to_add:
            with open(self.proficient_vocab_file, 'a', encoding='utf-8') as f:
                for word in sorted(words_to_add):
                    f.write(f"{word}\n")
        
        # 检查并移除熟练词汇中出现在存档文件中的词
        words_to_remove = proficient_words & Unfamiliar_words
        if words_to_remove:
            updated_words = proficient_words - words_to_remove
            with open(self.proficient_vocab_file, 'w', encoding='utf-8') as f:
                for word in sorted(updated_words):
                    f.write(f"{word}\n")
    
    def calculate_new_word_ratio(self, text: str) -> float:
        """计算新词比例(文本中不在熟练词汇中的单词比例)"""
        # 提取文本中的单词
        text_words = self.extract_words(text)
        if not text_words:
            return 0.0
        
        # 读取熟练词汇
        proficient_words = self.read_vocabulary_file(self.proficient_vocab_file)
        
        # 计算不在熟练词汇中的单词
        new_words = text_words - proficient_words
        
        # 计算比例
        return len(new_words) / len(text_words)
