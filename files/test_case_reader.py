import os
import re
from pathlib import Path

class SimplePOSTagger:
    """簡化版的詞性標註器"""
    
    # 定義詞性規則
    VERBS = ['launch', 'navigate', 'verify', 'click', 'enter', 'scroll', 
             'fill', 'select', 'check', 'submit', 'wait', 'search',
             'type', 'press', 'hover', 'drag', 'drop', 'upload',
             'download', 'open', 'close', 'refresh', 'move', 'filter',
             'register', 'login', 'logout', 'add', 'delete', 'edit']
    
    NOUNS = ['browser', 'page', 'button', 'input', 'field', 'link',
             'text', 'message', 'footer', 'header', 'form', 'email',
             'address', 'password', 'arrow', 'url', 'website', 'screen',
             'card', 'movie', 'user', 'name', 'title', 'state']
    
    PREPOSITIONS = ['to', 'in', 'on', 'at', 'with', 'by', 'from', 'for', 'of']
    
    DETERMINERS = ['a', 'an', 'the', 'that', 'this']
    
    CONJUNCTIONS = ['and', 'or', 'but']
    
    @staticmethod
    def tag_word(word):
        """標註單個詞的詞性"""
        word_lower = word.lower().strip('.,!?;:')
        
        if word_lower in SimplePOSTagger.VERBS:
            return 'VERB'
        elif word_lower in SimplePOSTagger.NOUNS:
            return 'NOUN'
        elif word_lower in SimplePOSTagger.PREPOSITIONS:
            return 'PREP'
        elif word_lower in SimplePOSTagger.DETERMINERS:
            return 'DET'
        elif word_lower in SimplePOSTagger.CONJUNCTIONS:
            return 'CONJ'
        elif word.startswith("'") or word.startswith('"'):
            return 'QUOTE'
        elif word_lower in ['is', 'are', 'am', 'was', 'were', 'be', 'been']:
            return 'AUX'
        elif word_lower in ['successfully', 'correctly', 'incorrectly', 'visible']:
            return 'ADV'
        elif word_lower == 'not':
            return 'NEG'
        else:
            return 'WORD'
    
    @staticmethod
    def tokenize_and_tag(text):
        """分詞並標註詞性"""
        # 簡單的分詞
        words = re.findall(r"'[^']+'|\"[^\"]+\"|[\w]+|[.,!?;:]", text)
        
        tagged = []
        for word in words:
            pos = SimplePOSTagger.tag_word(word)
            tagged.append((word, pos))
        
        return tagged


class SVGGenerator:
    """生成 SVG 依存關係圖"""
    
    @staticmethod
    def generate_pos_svg(text, tagged_words, output_file):
        """生成 POS 標註的 SVG"""
        
        # SVG 設置
        width = max(1200, len(tagged_words) * 100)
        height = 200
        word_spacing = width // (len(tagged_words) + 1)
        
        # 顏色配置
        colors = {
            'VERB': '#ff6b6b',
            'NOUN': '#4ecdc4',
            'PREP': '#95e1d3',
            'DET': '#f9ca24',
            'CONJ': '#a29bfe',
            'AUX': '#fd79a8',
            'ADV': '#fdcb6e',
            'QUOTE': '#74b9ff',
            'WORD': '#dfe6e9',
            'NEG': '#ff7675'
        }
        
        svg_parts = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="{width}" height="{height}" fill="white"/>',
            f'<text x="10" y="30" font-size="14" font-weight="bold" fill="#2d3436">{text}</text>'
        ]
        
        # 繪製每個詞和它的 POS 標籤
        for i, (word, pos) in enumerate(tagged_words):
            x = (i + 1) * word_spacing
            y = 100
            
            color = colors.get(pos, '#95a5a6')
            
            # 繪製詞
            svg_parts.append(
                f'<text x="{x}" y="{y}" text-anchor="middle" font-size="16" fill="#2d3436">{word}</text>'
            )
            
            # 繪製 POS 標籤
            svg_parts.append(
                f'<rect x="{x-30}" y="{y+10}" width="60" height="25" fill="{color}" rx="5"/>'
            )
            svg_parts.append(
                f'<text x="{x}" y="{y+27}" text-anchor="middle" font-size="12" fill="white" font-weight="bold">{pos}</text>'
            )
            
            # 繪製連接線
            if i > 0:
                prev_x = i * word_spacing
                svg_parts.append(
                    f'<line x1="{prev_x+30}" y1="{y+20}" x2="{x-30}" y2="{y+20}" stroke="#b2bec3" stroke-width="1" stroke-dasharray="5,5"/>'
                )
        
        # 添加圖例
        legend_y = height - 50
        legend_x = 10
        svg_parts.append(f'<text x="{legend_x}" y="{legend_y-10}" font-size="12" font-weight="bold" fill="#2d3436">POS Tags:</text>')
        
        legend_items = [
            ('VERB', 'Verb'),
            ('NOUN', 'Noun'),
            ('PREP', 'Preposition'),
            ('DET', 'Determiner'),
            ('AUX', 'Auxiliary')
        ]
        
        for i, (pos, label) in enumerate(legend_items):
            lx = legend_x + i * 150
            color = colors.get(pos, '#95a5a6')
            svg_parts.append(f'<rect x="{lx}" y="{legend_y}" width="20" height="15" fill="{color}"/>')
            svg_parts.append(f'<text x="{lx+25}" y="{legend_y+12}" font-size="11" fill="#2d3436">{label}</text>')
        
        svg_parts.append('</svg>')
        
        svg_content = '\n'.join(svg_parts)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return svg_content


class TestCaseReader:
    """讀取並解析測試案例檔案"""
    
    def __init__(self, upload_dir="."):
        self.upload_dir = upload_dir
        self.test_cases = []
        self.output_dir = "svg_output"
        
        # 創建輸出目錄
        Path(self.output_dir).mkdir(exist_ok=True)
    
    def read_all_files(self):
        """讀取所有.feature檔案"""
        upload_path = Path(self.upload_dir)
        feature_files = sorted(upload_path.glob("*.feature"))
        
        print(f"找到 {len(feature_files)} 個測試檔案\n")
        
        for file_path in feature_files:
            test_case = self.read_file(file_path)
            if test_case:
                self.test_cases.append(test_case)
        
        return self.test_cases
    
    def read_file(self, file_path):
        """讀取單一feature檔案"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析檔案內容
            lines = content.strip().split('\n')
            
            # 提取檔案名稱
            file_name = file_path.name
            
            # 提取URL
            urls = None
            if lines and lines[0].startswith('urls = '):
                urls = lines[0]
            
            # 提取測試案例標題
            title = None
            steps = []
            
            for i, line in enumerate(lines):
                if line.startswith('Test Case'):
                    title = line
                elif line.strip() and line[0].isdigit() and '. ' in line:
                    steps.append(line.strip())
            
            test_case = {
                'file_name': file_name,
                'urls': urls,
                'title': title,
                'steps': steps,
                'content': content
            }
            
            return test_case
            
        except Exception as e:
            print(f"讀取檔案 {file_path} 時發生錯誤: {e}")
            return None
    
    def analyze_and_generate_svgs(self):
        """分析每個步驟並生成 SVG"""
        print("=" * 80)
        print("開始分析測試步驟並生成 SVG")
        print("=" * 80)
        
        for tc_idx, tc in enumerate(self.test_cases):
            print(f"\n處理: {tc['file_name']}")
            
            # 為每個測試案例創建子目錄
            tc_dir = Path(self.output_dir) / tc['file_name'].replace('.feature', '')
            tc_dir.mkdir(exist_ok=True)
            
            for step_idx, step in enumerate(tc['steps'], 1):
                # 移除步驟編號
                step_text = re.sub(r'^\d+\.\s*', '', step)
                
                # 進行 POS 標註
                tagged = SimplePOSTagger.tokenize_and_tag(step_text)
                
                # 生成 SVG 文件名
                svg_filename = tc_dir / f"step_{step_idx:02d}.svg"
                
                # 生成 SVG
                SVGGenerator.generate_pos_svg(step_text, tagged, svg_filename)
                
                print(f"  步驟 {step_idx}: {svg_filename}")
                
                # 顯示 POS 分析結果
                print(f"    原文: {step_text}")
                print(f"    POS: {' '.join([f'{w}({p})' for w, p in tagged])}")
        
        print(f"\n所有 SVG 檔案已生成在 '{self.output_dir}' 目錄中")
    
    def display_summary(self):
        """顯示所有測試案例的摘要"""
        print("=" * 60)
        print("測試案例摘要")
        print("=" * 60)
        
        for i, tc in enumerate(self.test_cases, 1):
            print(f"\n[{i}] {tc['file_name']}")
            print(f"    {tc['title']}")
            print(f"    步驟數量: {len(tc['steps'])}")


if __name__ == "__main__":
    # 創建讀取器實例
    reader = TestCaseReader()
    
    # 讀取所有檔案
    test_cases = reader.read_all_files()
    
    # 顯示摘要
    reader.display_summary()
    
    print("\n")
    
    # 分析並生成 SVG
    reader.analyze_and_generate_svgs()
