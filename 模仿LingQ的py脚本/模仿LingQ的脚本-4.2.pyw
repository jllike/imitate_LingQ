import customtkinter as ctk # type: ignore
from tkinter import filedialog
import os
from Text_new_word_ratio_check import VocabularyAnalyzer # type: ignore

# ====== 所有 UI 配置集中在这里 ======
UI_CONFIG = {
    # 主题模式 ("dark", "light", "system")
    "theme": "dark",

    # 主题颜色（customtkinter 默认蓝色）
    "primary_color": "blue",
    
    # 字体配置
    "font_family": "Microsoft YaHei",
    "text_font": ("Microsoft YaHei", 20),
    "button_font": ("Microsoft YaHei", 15),
    "status_font": ("Microsoft YaHei", 15),
    
    # 文本区域
    "text_bg": "#2b2b2b",  # 背景色
    "text_fg": "#808b96",  # 字体颜色
    "highlight_color": "#ffb000",  # 高亮颜色
    
    # 按钮颜色
    "button_bg": "#3a3a3a",
    "button_hover": "#4a4a4a",
    
    # 状态栏
    "status_bg": "#252526",
    "status_fg": "#a0a0a0",
    
    # 窗口大小
    "window_size": "800x600",
}

EDGE_PUNCTUATION = {' ', '\n', '—', ',', '，', '.', '。', '“', '”', '"', "!", "！", ";", "；"}

class TextHighlighter:
    def __init__(self, root):
        self.root = root
        self.root.title("仿LingQ工具")
        
        # 应用主题
        ctk.set_appearance_mode(UI_CONFIG["theme"])
        ctk.set_default_color_theme(UI_CONFIG["primary_color"])  # 现在不会报错了
        
        # 尝试读取保存的位置，否则使用默认位置
        try:
            with open("window_position.txt", "r") as f:
                geometry = f.read().strip()
                self.root.geometry(geometry)
        except:
            self.root.geometry(UI_CONFIG["window_size"] + "+300+100")        
        
        self.vocab_analyzer = VocabularyAnalyzer()
        self.enable_vocab_analysis = ctk.BooleanVar(value=False)  # 默认关闭词汇分析
        
        # 初始化变量
        self.file_path = ""
        self.selected_text = ""
        self.start_pos = None
        self.highlight_tags = set()
        self.record_file = "Unfamiliar_words.txt"
        self.progress_file = "reading_progress.txt"  

        
        # 创建存档文件(如果不存在)
        if not os.path.exists(self.record_file):
            open(self.record_file, 'w').close()
        
        # 创建UI
        self.create_widgets()
        
        # 绑定事件
        self.bind_events()
    
    def create_widgets(self):
        # 顶部按钮框架
        btn_frame = ctk.CTkFrame(self.root)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        # 打开文件按钮
        self.open_btn = ctk.CTkButton(
            btn_frame, 
            text="打开文件",
            command=self.open_file,
        )
        self.open_btn.pack(side="left", padx=5)
        
        # 添加词汇分析开关复选框
        self.vocab_check = ctk.CTkCheckBox(
            btn_frame,
            text="是否学习完毕",
            variable=self.enable_vocab_analysis,
        )
        self.vocab_check.pack(side="left", padx=10)
        
        # 文本区域
        self.text = ctk.CTkTextbox(
            self.root,
            wrap="word",
            font=UI_CONFIG["text_font"],
            fg_color=UI_CONFIG["text_bg"],
            text_color=UI_CONFIG["text_fg"],
        )
        self.text.pack(fill="both", expand=True, padx=5, pady=5)
        self.text.configure(state="disabled")  # 默认禁用
        
        # 状态栏
        self.status = ctk.CTkLabel(
            self.root,
            text="就绪",
            fg_color=UI_CONFIG["status_bg"],
            text_color=UI_CONFIG["status_fg"],
            font=UI_CONFIG["status_font"],
        )
        self.status.pack(side="left", padx=5, pady=(0, 5))
    
    def bind_events(self):
        # 鼠标事件
        self.text.bind("<Button-1>", self.on_click)
        self.text.bind("<B1-Motion>", self.on_drag)
        self.text.bind("<ButtonRelease-1>", self.on_release)
        self.text.bind("<Button-3>", self.on_right_click)
        
        # 键盘事件
        self.text.bind("<KeyPress-space>", self.on_space)
    
    # ====== 原有逻辑保持不变 ======
    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path = file_path
            self.text.configure(state="normal")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text.delete('1.0', 'end')
                self.text.insert('1.0', content)

            ratio = self.vocab_analyzer.calculate_new_word_ratio(content)
            ratio_percent = round(ratio * 100, 2)
            self.status.configure(text=f"就绪 | 新词比例: {ratio_percent}%")
            
            self.text.configure(state="disabled")
            self.highlight_matches()
           
            # 加载阅读进度
            self.load_reading_progress()


    def save_reading_progress(self):
        # 保存当前进度条位置
        saved_scroll_pos = self.text.yview()[0]  # 只保存 start
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                f.write(f"{round(saved_scroll_pos, 3)}")
        except Exception as e:
            print(f"保存进度失败: {e}")
    def load_reading_progress(self):
        # 加载进度条位置
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    saved_info = f.read()
                    relative_pos = float(saved_info)
                    self.text.yview_moveto(relative_pos)
        except Exception as e:
            print(f"恢复进度失败: {e}")

 
    def highlight_matches(self):
        for tag in self.highlight_tags:
            self.text.tag_remove(tag, '1.0', 'end')
        self.highlight_tags.clear()
        
        try:
            with open(self.record_file, 'r', encoding='utf-8') as f:
                lines = [line.strip().lower() for line in f.readlines() if line.strip()]
        except:
            lines = []
        
        content = self.text.get('1.0', 'end').lower()
        for word in lines:
            if word in content:
                self.highlight_word(word)
    
    def highlight_word(self, word):
        start = '1.0'
        while True:
            pos = self.text.search(word, start, stopindex='end', nocase=1)
            if not pos:
                break
                
            end = f"{pos}+{len(word)}c"
            
            prev_char = self.text.get(f"{pos}-1c") if pos != '1.0' else ' '
            next_char = self.text.get(end)
            
            boundary_chars = EDGE_PUNCTUATION
            if prev_char in boundary_chars and next_char in boundary_chars:
                tag_name = f"highlight_{len(self.highlight_tags)}"
                self.text.tag_add(tag_name, pos, end)
                self.text.tag_config(tag_name, foreground=UI_CONFIG["highlight_color"])
                self.highlight_tags.add(tag_name)
            
            start = end
    
    def on_click(self, event):
        self.start_pos = self.text.index(f"@{event.x},{event.y}")
    
    def on_drag(self, event):
        try:
            end_pos = self.text.index(f"@{event.x},{event.y}")
            self.text.tag_remove("sel", '1.0', 'end')
            self.text.tag_add("sel", self.start_pos, end_pos)
        except:
            pass
    
    def on_release(self, event):
        try:
            if self.text.tag_ranges("sel"):
                self.expand_selection()
                self.selected_text = self.text.get("sel.first", "sel.last")
                self.status.configure(text=f"已选中: {self.selected_text}")
        except:
            pass
    
    def expand_selection(self):
        # 获取当前选择范围
        start_pos = self.text.index("sel.first")
        end_pos = self.text.index("sel.last")
        
        # 向左扩展直到遇到边界标点
        while True:
            if start_pos == '1.0':  # 已经到达文本开头
                break
            prev_pos = self.text.index(f"{start_pos}-1c")
            char = self.text.get(prev_pos)
            if char in EDGE_PUNCTUATION:
                break
            start_pos = prev_pos
        
        # 向右扩展直到遇到边界标点
        while True:
            next_pos = self.text.index(f"{end_pos}+1c")
            if next_pos == end_pos:  # 已经到达文本末尾 (next_pos不再变化)
                break
            char = self.text.get(end_pos)
            if char in EDGE_PUNCTUATION:
                break
            end_pos = next_pos
        
        # 更新选择范围
        self.text.tag_remove("sel", '1.0', 'end')
        self.text.tag_add("sel", start_pos, end_pos)
    
    def on_right_click(self, event):
        if self.selected_text:
            with open(self.record_file, 'a', encoding='utf-8') as f:
                f.write(self.selected_text + '\n')
            self.highlight_matches()
            self.status.configure(text=f"已保存: {self.selected_text}")
            self.selected_text = ""
    
    def on_space(self, event):
        if self.text.tag_ranges("sel"):
            self.text.tag_remove("sel", '1.0', 'end')
            selected = self.selected_text.lower()
            
            with open(self.record_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip().lower() != selected]
            
            with open(self.record_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')
            
            self.highlight_matches()
            self.status.configure(text=f"已删除: {self.selected_text}")
            self.selected_text = ""
            return "break"
    
    def run(self):
        def on_closing():
            with open("window_position.txt", "w") as f:
                f.write(self.root.geometry())

            # 保存阅读进度
            self.save_reading_progress()
                
            if self.enable_vocab_analysis.get():
                content = self.text.get('1.0', 'end')
                if content.strip():
                    self.vocab_analyzer.update_proficient_vocabulary(content)
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    root = ctk.CTk()
    app = TextHighlighter(root)
    app.run()
