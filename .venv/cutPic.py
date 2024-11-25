import os
import time
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Text, Scrollbar
from tkinter.font import Font
from PIL import Image
import warnings
import glob

# 设置 DPI 意识（仅适用于 Windows）
try:
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except AttributeError:
    pass  # 如果不是 Windows 系统，忽略此设置

# 禁用 DecompressionBombWarning
warnings.filterwarnings("ignore", category=Image.DecompressionBombWarning)
Image.MAX_IMAGE_PIXELS = None  # 或者设置一个合理的最大像素数


def split_image_into_nine(image_path, output_folder, type_folder=None):
    try:
        # 获取图片文件名（不含路径）
        base_name = os.path.basename(image_path)
        # 获取文件名（不含扩展名）
        name_without_ext = os.path.splitext(base_name)[0]

        # 创建子文件夹
        if type_folder:
            sub_output_folder = os.path.join(output_folder, type_folder, name_without_ext)
        else:
            sub_output_folder = os.path.join(output_folder, name_without_ext)

        # 确保子文件夹存在
        if not os.path.exists(sub_output_folder):
            os.makedirs(sub_output_folder)

        # 打开图片
        with Image.open(image_path) as img:
            width, height = img.size

            # 计算每个小图的宽度和高度
            new_width = width // 3
            new_height = height // 3

            # 切割图片并保存
            for i in range(3):  # 行
                for j in range(3):  # 列
                    box = (j * new_width, i * new_height, (j + 1) * new_width, (i + 1) * new_height)
                    cropped_img = img.crop(box)
                    # 构建输出文件名
                    output_filename = f'{name_without_ext}-{i + 1}-{j + 1}.png'
                    cropped_img.save(os.path.join(sub_output_folder, output_filename))
    except Exception as e:
        messagebox.showerror("Error", f"Error splitting image {image_path}: {e}")


def process_images_in_folder(input_folder, output_folder):
    # 支持的图片格式
    supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp')

    # 获取输入文件夹中的所有图片文件
    image_files = [f for f in glob.glob(os.path.join(input_folder, '*')) if f.lower().endswith(supported_extensions)]

    # 统计每种类型的图片数量
    processed_types = {}
    for image_file in image_files:
        extension = os.path.splitext(image_file)[1].lower()
        if extension in processed_types:
            processed_types[extension] += 1
        else:
            processed_types[extension] = 1

    # 判断是否只有一种文件类型
    if len(processed_types) == 1:
        type_folders = {}
    else:
        # 创建类型文件夹
        type_folders = {}
        for ext, count in processed_types.items():
            if count > 5:
                type_folder_name = ext[1:]  # 去掉点号
                type_folders[ext] = type_folder_name
                os.makedirs(os.path.join(output_folder, type_folder_name), exist_ok=True)

    # 更新进度标签
    total_images = len(image_files)
    update_progress_label(0, total_images)

    # 处理每一张图片
    for index, image_file in enumerate(image_files, start=1):
        extension = os.path.splitext(image_file)[1].lower()
        type_folder = type_folders.get(extension)
        split_image_into_nine(image_file, output_folder, type_folder)
        update_progress_label(index, total_images)
        root.update_idletasks()  # 更新界面

    return processed_types


def select_input_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        input_folder_var.set(folder_selected)


def select_output_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_folder_var.set(folder_selected)


def start_processing():
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()

    if not input_folder or not output_folder:
        messagebox.showerror("Error", "请选择要处理的图片所在的文件夹和要输出的文件夹地址")
        return

    try:
        start_time = time.time()  # 记录开始时间
        processed_types = process_images_in_folder(input_folder, output_folder)
        end_time = time.time()  # 记录结束时间
        elapsed_time = end_time - start_time  # 计算总时间
        elapsed_time_str = f"{elapsed_time:.3f}"  # 格式化为3位小数

        # 构建提示信息
        processed_info = []
        for ext, count in processed_types.items():
            processed_info.append(f"{ext}: {count} 张")

        processed_info_str = ", ".join(processed_info)
        messagebox.showinfo("Success", f"图片处理完成，共用时 {elapsed_time_str} 秒\n处理了 {processed_info_str}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def show_tips():
    tips_window = Toplevel(root)
    tips_window.title("Tips")
    tips_window.config(bg="#323232")

    # 创建滚动条
    scrollbar = Scrollbar(tips_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 创建文本框
    text_widget = Text(tips_window, wrap=tk.WORD, yscrollcommand=scrollbar.set, bg="#0d7377", fg="#ffffd2",
                       font=Font(family="SimSun", size=12))
    text_widget.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

    # 插入 Tips 内容
    tips_content = """
    1. **基本操作指南**:
       - 选择文件夹：点击“选择文件夹”按钮，选择包含待处理图片的文件夹和输出文件夹（程序只会读取一层文件夹，不会往下读取子文件夹）。
       - 开始处理：点击“开始处理”按钮，程序将自动切割图片并保存到指定的输出文件夹中。

    2. **常见问题解答 (FAQ)**:
       - **处理速度慢**：如果图片数量较多，处理速度可能会较慢，请耐心等待，未响应也不要随便关掉程序，请查看任务管理器，若CPU占用没有特别低，一般都是在正常运行。
       - **文件格式不支持**：目前支持的文件格式有 jpg, png, jpeg, bmp。如果遇到不支持的格式，建议转换为支持的格式后再进行处理。
       - **输出文件夹结构**：每个处理的图片会在输出文件夹中生成一个同名子文件夹，切割后的图片会保存在对应的子文件夹中。

    3. **程序功能说明**:
       - **选择文件夹**：例如，1.jpg 在 C:\\XX\\1.jpg 这个目录下，需要选择 C:\\XXX\\ 这个文件夹。
       - **图片处理**：支持 jpg, png, jpeg, bmp 四种常用图片类型，如果想要拓展的话可以修改代码。
       - **自定义切割方式**：目前支持将图片切割为 3x3 的九宫格。如果有什么好的想法可以在GitHub上提交Issue，我会尽量实现（只要在我能力范围内的）。
       - **文件分类**：如果某种类型的图片超过5张，程序会为这种类型创建一个专门的文件夹，并将该类型的所有图片的子文件夹存放到这个专门的文件夹中。如果文件夹中只有一种类型的图片，程序将直接按照原始的输出方式进行处理，不再创建分类文件夹。

    4. **技术支持和反馈**:
       - **联系方式**：如有任何问题或建议，请联系作者 @MT-Y-TM (GitHub)。
       - **反馈渠道**：欢迎在 GitHub 上提交 Issue，帮助我们改进程序。

    5. **版权声明**:
       - **特别说明**：本程序永久免费，禁止拿来倒卖程序本身，可用于商业活动。
       - **开源许可**：本程序遵循 MIT 协议，可自由转载和使用。
       - **第三方库&工具**：本程序使用了以下第三方库：
         - Pillow: 用于图像处理
         - Tkinter: 用于图形界面
         - Upx: 用于减少打包后的文件体积

    6. **其他说明**:
       - **作者**：@MT-Y-TM (GitHub)，可自由转载使用，出事我不背锅。
       - **开发工具**：PyCharm、通义千问、配色表（peisebiao.com，在这里寻找的配色参考）。
       - **遵守协议**：本程序遵守 MIT 协议
       - **关于图标**：源于《凉宫春日的忧郁》的作品中 SOS团 的团徽
    """
    text_widget.insert(tk.END, tips_content)
    text_widget.config(state=tk.DISABLED)  # 禁止编辑

    # 配置滚动条
    scrollbar.config(command=text_widget.yview)


def update_progress_label(current, total):
    progress_label.config(text=f"处理进度: {current}/{total}")
    root.update_idletasks()  # 更新界面


# 创建主窗口
root = tk.Tk()
root.title("图片切割九宫格")
root.config(bg="#323232")

# 动态获取图标文件路径
if hasattr(sys, '_MEIPASS'):
    icon_path = os.path.join(sys._MEIPASS, "zoz.ico")
else:
    icon_path = "zoz.ico"

# 设置图标
root.iconbitmap(icon_path)

# 设置字体
label_font = Font(family="SimSun", size=12)
button_font = Font(family="SimSun", size=12)

# 创建变量
input_folder_var = tk.StringVar()
output_folder_var = tk.StringVar()

# 创建和放置控件
tk.Label(root, text="需要处理的图片的文件夹地址:", bg="#323232", fg="#ffffd2").grid(row=0, column=0, padx=10, pady=10,
                                                                                    sticky="e")
tk.Entry(root, textvariable=input_folder_var, width=50, bg="#0d7377", fg="#ffffd2").grid(row=0, column=1, padx=10,
                                                                                         pady=10)
tk.Button(root, text="选择文件夹", command=select_input_folder, bg="#0d7377", fg="#ffffd2").grid(row=0, column=2,
                                                                                                 padx=10, pady=10)

tk.Label(root, text="输出文件夹地址:", bg="#323232", fg="#ffffd2").grid(row=1, column=0, padx=10, pady=10, sticky="e")
tk.Entry(root, textvariable=output_folder_var, width=50, bg="#0d7377", fg="#ffffd2").grid(row=1, column=1, padx=10,
                                                                                          pady=10)
tk.Button(root, text="选择文件夹", command=select_output_folder, bg="#0d7377", fg="#ffffd2").grid(row=1, column=2,
                                                                                                  padx=10, pady=10)

start_button = tk.Button(root, text="开始处理", command=start_processing, bg="#0d7377", fg="#ffffd2")
start_button.grid(row=2, column=1, pady=20)

# 添加进度标签
progress_label = tk.Label(root, text="处理进度: 0/0", bg="#323232", fg="#ffffd2")
progress_label.grid(row=2, column=2, pady=20)

# 添加 Tips 按钮
tk.Button(root, text="Tips", command=show_tips, bg="#0d7377", fg="#ffffd2").grid(row=3, column=1, pady=10)

# 运行主循环
root.mainloop()