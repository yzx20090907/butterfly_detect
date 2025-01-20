import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import json
from infer import load_model, predict_and_draw_boxes
import cv2
from datetime import datetime

output_folder = "result"
ok_folder = "ok"

class ButterflyDetectorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("蝴蝶识别系统")
        
        # 设置窗口最小大小和背景色
        self.root.minsize(1000, 700)
        self.root.configure(bg='#f0f0f0')
        
        # 配置主窗口的网格权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # 加载模型
        self.model = load_model("best-4.pt")
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)  # 左侧可以伸缩
        self.main_frame.grid_columnconfigure(1, weight=0)  # 右侧固定宽度
        
        # 创建标题
        self.title_frame = ttk.Frame(self.main_frame)
        self.title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))
        self.title_label = ttk.Label(
            self.title_frame, 
            text="蝴蝶图像识别系统", 
            font=('Arial', 24, 'bold'),
            padding=(0, 10)
        )
        self.title_label.pack()
        
        # 创建左侧面板
        self.left_panel = ttk.Frame(self.main_frame)
        self.left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        
        # 创建右侧面板
        self.right_panel = ttk.Frame(self.main_frame, width=235)
        self.right_panel.grid(row=1, column=1, sticky=(tk.N, tk.S), padx=10)
        self.right_panel.grid_propagate(False)  # 防止子组件影响框架大小
        
        # 创建按钮框架
        self.button_frame = ttk.Frame(self.left_panel)
        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建渐变按钮
        self.select_button = self.create_gradient_button(
            self.button_frame,
            "上传图片进行识别",
            self.select_images,
            width=200,
            height=40
        )
        self.select_button.pack(pady=10)
        
        # 创建左侧图片显示区域
        self.create_image_display()
        
        # 创建右侧识别记录区域
        self.create_record_display()
        
        # 初始化变量
        self.image_paths = []
        self.current_image_index = 0
        self.total_detections = 0
        self.correct_detections = 0
        
        # 加载历史记录
        self.load_records()
        
    def create_image_display(self):
        # 创建图片显示框架
        self.image_frame = ttk.LabelFrame(
            self.left_panel, 
            text="图片预览", 
            padding=10
        )
        self.image_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建图片标签
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(padx=5, pady=5)
        
        # 添加提示文本
        self.hint_label = ttk.Label(
            self.image_frame,
            text="Powered by yzx",
            font=('Arial', 12),
            foreground='#666666'
        )
        self.hint_label.pack(pady=20)
        
    def create_record_display(self):
        # 创建记录显示框架
        self.record_frame = ttk.LabelFrame(
            self.right_panel, 
            text="识别记录", 
            padding=10,
            width=235  # 设置固定宽度
        )
        self.record_frame.pack(fill=tk.BOTH, expand=True)
        self.record_frame.pack_propagate(False)  # 防止子组件影响框架大小
        
        # 创建统计信息标签
        self.stats_frame = ttk.Frame(self.record_frame)
        self.stats_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.stats_label = ttk.Label(
            self.stats_frame,
            text="统计信息",
            font=('Arial', 11, 'bold'),
            wraplength=200  # 设置文本换行宽度
        )
        self.stats_label.pack(anchor=tk.W)
        
        # 创建记录容器Canvas
        self.records_canvas = tk.Canvas(
            self.record_frame,
            bg='#f0f0f0',
            highlightthickness=0,
            width=215  # 设置画布宽度
        )
        self.records_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加滚动条
        self.record_scrollbar = ttk.Scrollbar(
            self.record_frame,
            orient="vertical",
            command=self.records_canvas.yview
        )
        self.record_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建记录框架
        self.records_frame = ttk.Frame(self.records_canvas)
        self.records_canvas.create_window((0, 0), window=self.records_frame, anchor='nw')
        
        # 配置Canvas滚动
        self.records_canvas.configure(yscrollcommand=self.record_scrollbar.set)
        self.records_frame.bind('<Configure>', lambda e: self.records_canvas.configure(scrollregion=self.records_canvas.bbox("all")))
        
        # 存储记录框架的列表
        self.record_frames = []
        
    def load_records(self):
        try:
            if os.path.exists('detection_records.json'):
                with open('detection_records.json', 'r', encoding='utf-8') as f:
                    records = json.load(f)
                    self.total_detections = records.get('total', 0)
                    self.correct_detections = records.get('correct', 0)
                    
                    # 加载记录
                    for record in records.get('records', []):
                        # 解析记录内容
                        lines = record.strip().split('\n')
                        if len(lines) >= 3:
                            timestamp = lines[0]
                            filename = lines[1]
                            status_line = lines[2]
                            
                            # 创建记录框架
                            is_correct = "正确" in status_line
                            record_frame = ttk.Frame(self.records_frame)
                            bg_color = '#e8f5e9' if is_correct else '#ffebee'
                            record_frame.configure(style='Record.TFrame')
                            style = ttk.Style()
                            style.configure('Record.TFrame', background=bg_color)
                            
                            # 添加记录内容
                            ttk.Label(
                                record_frame,
                                text=timestamp,
                                font=('Arial', 8),
                                foreground='#666666'
                            ).pack(anchor='w', padx=10, pady=(5, 0))
                            
                            ttk.Label(
                                record_frame,
                                text=filename,
                                font=('Arial', 10, 'bold')
                            ).pack(anchor='w', padx=10, pady=(2, 0))
                            
                            ttk.Label(
                                record_frame,
                                text=status_line,
                                font=('Arial', 20, 'bold'),
                                foreground='#2e7d32' if is_correct else '#c62828'
                            ).pack(anchor='w', padx=10, pady=(2, 5))
                            
                            ttk.Separator(record_frame, orient='horizontal').pack(fill='x', padx=5)
                            record_frame.pack(fill='x', pady=2, expand=True)
                            
                            # 添加到记录列表
                            self.record_frames.append(record_frame)
                    
                    self.update_stats()
        except Exception as e:
            print(f"加载记录失败: {str(e)}")
            
    def save_records(self):
        try:
            records = {
                'total': self.total_detections,
                'correct': self.correct_detections,
                'records': []
            }
            
            # 收集所有记录的文本
            for frame in self.record_frames:
                record_text = ""
                for child in frame.winfo_children():
                    if isinstance(child, ttk.Label):
                        record_text += child.cget('text') + "\n"
                records['records'].append(record_text)
            
            with open('detection_records.json', 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记录失败: {str(e)}")
            
    def update_stats(self):
        accuracy = (self.correct_detections / self.total_detections * 100) if self.total_detections > 0 else 0
        stats_text = f"总识别数: {self.total_detections}  |  正确数: {self.correct_detections}  |  正确率: {accuracy:.1f}%"
        self.stats_label.config(
            text=stats_text,
            font=('Arial', 11, 'bold'),
            foreground='#333333'
        )
        
    def add_record(self, image_path, is_correct, confidence=None):
        # 更新统计数据
        self.total_detections += 1
        if is_correct:
            self.correct_detections += 1
            
        # 创建新记录框架
        record_frame = ttk.Frame(self.records_frame)
        
        # 设置背景色
        bg_color = '#e8f5e9' if is_correct else '#ffebee'
        record_frame.configure(style=f'Record{len(self.record_frames)}.TFrame')
        style = ttk.Style()
        style.configure(f'Record{len(self.record_frames)}.TFrame', background=bg_color)
        
        # 添加记录内容
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = os.path.basename(image_path)
        status = "✓ 正确" if is_correct else "✗ 错误"
        conf_text = f"置信度: {confidence:.2f}" if confidence is not None else ""
        
        # 创建记录标签
        ttk.Label(
            record_frame,
            text=timestamp,
            font=('Arial', 8),
            foreground='#666666'
        ).pack(anchor='w', padx=10, pady=(5, 0))
        
        ttk.Label(
            record_frame,
            text=filename,
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', padx=10, pady=(2, 0))
        
        ttk.Label(
            record_frame,
            text=f"{status} {conf_text}",
            font=('Arial', 20, 'bold'),
            foreground='#2e7d32' if is_correct else '#c62828'
        ).pack(anchor='w', padx=10, pady=(2, 5))
        
        # 添加分隔线
        ttk.Separator(record_frame, orient='horizontal').pack(fill='x', padx=5)
        
        # 将新记录添加到顶部，但先不显示
        record_frame.pack_forget()
        
        # 添加到记录列表
        self.record_frames.insert(0, record_frame)
        
        # 执行动画
        self._animate_records(record_frame)
        
        # 更新统计信息显示
        self.update_stats()
        
        # 保存记录
        self.save_records()
        
    def _animate_records(self, new_record):
        # 动画参数
        steps = 20
        delay = 20  # 毫秒
        total_movement = 100  # 总移动像素
        
        # 确保所有记录都可见
        for frame in self.record_frames:
            if frame != new_record:
                frame.pack(fill='x', pady=2, expand=True, side='top')
        
        # 获取所有现有记录的当前位置
        positions = {}
        for frame in self.record_frames[1:]:  # 除了新记录之外的所有记录
            frame.update_idletasks()
            positions[frame] = frame.winfo_y()
        
        # 设置新记录的初始位置（在底部）
        new_record.pack(fill='x', pady=2, expand=True, side='top')
        new_record.update_idletasks()
        start_y = positions[self.record_frames[1]] if len(self.record_frames) > 1 else 0
        
        def move_step(step):
            if step < steps:
                # 计算当前进度 (0 到 1)
                progress = step / steps
                
                # 移动新记录（从底部到顶部）
                new_y = start_y * (1 - progress)
                new_record.place(x=0, y=new_y, relwidth=1)
                
                # 移动其他记录（向下移动）
                for frame in self.record_frames[1:]:
                    original_y = positions[frame]
                    current_y = original_y + (total_movement * progress)
                    frame.place(x=0, y=current_y, relwidth=1)
                
                # 安排下一步
                self.root.after(delay, lambda: move_step(step + 1))
            else:
                # 动画完成，重置所有记录的位置
                for frame in self.record_frames:
                    frame.place_forget()
                    frame.pack(fill='x', pady=2, expand=True, side='top')
        
        # 开始动画
        move_step(0)
        
    def show_image(self, image_path, is_result=False):
        if image_path and os.path.exists(image_path):
            # 加载并调整图片大小
            image = Image.open(image_path)
            # 计算调整后的大小，保持宽高比
            display_size = (600, 600)
            image.thumbnail(display_size)
            photo = ImageTk.PhotoImage(image)
            
            # 更新图片显示
            self.image_label.configure(image=photo)
            self.image_label.image = photo  # 保持引用
            
            
    def show_current_image(self):
        if self.image_paths:
            # 显示原图和结果图
            image_path = self.image_paths[self.current_image_index]
            result_path = os.path.join("result", os.path.basename(image_path))
            if os.path.exists(result_path):
                self.show_image(result_path)
            else:
                self.show_image(image_path)
                
    def select_images(self):
        # 打开文件选择对话框
        file_paths = filedialog.askopenfilenames(
            title="选择图片",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if not file_paths:
            return
            
        # 清除之前的图片
        self.image_paths = []
        self.current_image_index = 0
        
        # 添加新选择的图片
        self.image_paths.extend(file_paths)
        
        # 显示第一张图片
        if self.image_paths:
            self.show_current_image()
        for image_path in self.image_paths:
            try:
                # 进行检测
                is_correct, confidence = predict_and_draw_boxes(image_path, self.model, output_folder, ok_folder)
                # 添加识别记录
                self.add_record(image_path, is_correct, confidence)
            except Exception as e:
                messagebox.showerror("错误", f"处理图片失败: {image_path}\n错误信息: {str(e)}")
        
        # 刷新当前显示的图片
        self.show_current_image()
            
    def detect_images(self):
        if not self.image_paths:
            messagebox.showwarning("警告", "请先选择图片")
            return
            
        # 创建结果文件夹
        
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(ok_folder, exist_ok=True)
        
        # 处理每张图片
        
    def create_gradient_button(self, parent, text, command, width=200, height=40):
        # 创建Canvas作为按钮
        canvas = tk.Canvas(parent, width=width, height=height, highlightthickness=0)
        
        # 先创建文本（确保在最上层）
        text_id = canvas.create_text(
            width/2, 
            height/2, 
            text=text, 
            font=('Arial', 12, 'bold'), 
            fill='#ffffff',
            tags="text"
        )
        
        def draw_gradient(is_hover=False):
            # 清除之前的内容
            canvas.delete("gradient")
            canvas.delete("corners")
            
            # 创建渐变效果
            for i in range(height):
                if not is_hover:
                    r1, g1, b1 = 0x4C, 0xAF, 0x50  # 浅绿色开始
                    r2, g2, b2 = 0x2E, 0x7D, 0x32  # 深绿色结束
                else:
                    r1, g1, b1 = 0x66, 0xBB, 0x6A  # 更亮的绿色
                    r2, g2, b2 = 0x43, 0xA0, 0x47  # 更亮的深绿色
                
                r = int(r1 + (r2 - r1) * i / height)
                g = int(g1 + (g2 - g1) * i / height)
                b = int(b1 + (b2 - b1) * i / height)
                color = f'#{r:02x}{g:02x}{b:02x}'
                canvas.create_line(0, i, width, i, fill=color, tags="gradient")
            
            # 创建圆角矩形
            radius = 20
            colors = ['#66BB6A', '#43A047'] if is_hover else ['#4CAF50', '#2E7D32']
            
            canvas.create_arc(0, 0, radius*2, radius*2, 
                             start=90, extent=90, 
                             fill=colors[0], outline=colors[0], 
                             tags="corners")
            canvas.create_arc(width-radius*2, 0, width, radius*2, 
                             start=0, extent=90, 
                             fill=colors[0], outline=colors[0], 
                             tags="corners")
            canvas.create_arc(0, height-radius*2, radius*2, height, 
                             start=180, extent=90, 
                             fill=colors[1], outline=colors[1], 
                             tags="corners")
            canvas.create_arc(width-radius*2, height-radius*2, width, height, 
                             start=270, extent=90, 
                             fill=colors[1], outline=colors[1], 
                             tags="corners")
            
            # 确保文本在最上层
            canvas.tag_raise("text")
        
        def on_enter(e):
            draw_gradient(True)
        
        def on_leave(e):
            draw_gradient(False)
        
        def on_click(e):
            # 点击效果
            canvas.configure(relief="sunken")
            command()
            canvas.after(100, lambda: canvas.configure(relief="raised"))
        
        # 初始渐变
        draw_gradient()
        
        # 绑定事件
        canvas.bind('<Enter>', on_enter)
        canvas.bind('<Leave>', on_leave)
        canvas.bind('<Button-1>', on_click)
        canvas.bind('<ButtonRelease-1>', lambda e: canvas.configure(relief="raised"))
        
        return canvas

def main():
    root = tk.Tk()
    app = ButterflyDetectorUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
