
import re
import json
from collections import OrderedDict
from typing import Dict, Tuple


class CitationProcessor:
    """文献引用处理器"""
    
    def __init__(self, metadata: Dict):
        """
        Args:
            metadata: 参考文献元数据字典，格式如 {"cite_key": {...}, ...}
        """
        self.metadata = metadata
        self.citation_mapping = OrderedDict()  # citation_key -> 编号
    
    def process(self, content: str) -> Tuple[str, str]:
        """
        处理文档中的引用
        
        Args:
            content: 初稿内容
            
        Returns:
            (处理后的内容, 参考文献列表)
        """
        # 1. 提取并编号所有引用
        self._build_citation_mapping(content)
        
        # 2. 替换文中的引用标记
        processed_content = self._replace_citations(content)
        
        # 3. 生成参考文献列表
        reference_list = self._generate_references()
        
        return processed_content, reference_list
    
    def _build_citation_mapping(self, content: str):
        """扫描文档，按首次出现顺序为引用分配编号"""
        # 匹配 [cite:xxx] 或 [cite:xxx, yyy]
        pattern = r'\[cite:([^\]]+)\]'
        matches = re.findall(pattern, content)
        
        counter = 1
        for match in matches:
            # 处理多个引用的情况（逗号分隔）
            cite_keys = [key.strip() for key in match.split(',')]
            
            for cite_key in cite_keys:
                if cite_key not in self.citation_mapping:
                    self.citation_mapping[cite_key] = counter
                    counter += 1
        
        print(f"✅ 找到 {len(self.citation_mapping)} 个引用")
    
    def _replace_citations(self, content: str) -> str:
        """将 [cite:xxx] 替换为 [数字]"""
        def replace_match(match):
            cite_text = match.group(1)
            cite_keys = [key.strip() for key in cite_text.split(',')]
            
            # 转换为数字编号
            numbers = []
            for key in cite_keys:
                if key in self.citation_mapping:
                    numbers.append(str(self.citation_mapping[key]))
                else:
                    print(f"⚠️  警告: 未找到引用 '{key}' 的元数据")
                    numbers.append(f"cite:{key}")
            
            return f"[{', '.join(numbers)}]"
        
        pattern = r'\[cite:([^\]]+)\]'
        return re.sub(pattern, replace_match, content)
    
    def _generate_references(self) -> str:
        """生成参考文献列表"""
        references = []
        
        for cite_key, number in self.citation_mapping.items():
            if cite_key in self.metadata:
                meta = self.metadata[cite_key]
                
                # 格式化作者
                authors = ', '.join(meta.get('authors', ['Unknown']))
                
                # 格式化参考文献条目
                ref = (
                    f"[{number}] {authors}. "
                    f"{meta.get('year', 'n.d.')}. "
                    f"{meta.get('title', 'Unknown title')}. "
                    f"{meta.get('journal', 'Unknown journal')}."
                )
                
                # 可选：添加 DOI
                if meta.get('doi'):
                    ref += f" DOI: {meta['doi']}"
                
                references.append(ref)
            else:
                references.append(f"[{number}] {cite_key} (元数据缺失)")
        
        return '\n'.join(references)


def process_draft(draft_content: str, metadata: Dict) -> str:
    """
    处理初稿，插入文献引用
    
    Args:
        draft_content: 初稿内容（Markdown 格式）
        metadata: 参考文献元数据字典
        
    Returns:
        处理后的完整文档（包含参考文献列表）
    """
    processor = CitationProcessor(metadata)
    processed_content, reference_list = processor.process(draft_content)
    
    # 组装最终文档
    final_document = f"{processed_content}\n\n## 参考文献 (References)\n\n{reference_list}"
    
    return final_document


# ============ 使用示例 ============

if __name__ == "__main__":
    
    # 示例：从文件读取
    with open('full_content.md', 'r', encoding='utf-8') as f:
        draft = f.read()
    
    with open('references.json', 'r', encoding='utf-8') as f:
        refs = json.load(f)
    
    # 处理
    final_doc = process_draft(draft, refs)
    
    # 保存
    with open('final_report.md', 'w', encoding='utf-8') as f:
        f.write(final_doc)
    
    print("✅ 完成！")