from PIL import Image
import os
import warnings

# 禁用 DecompressionBombWarning
warnings.filterwarnings("ignore", category=Image.DecompressionBombWarning)
Image.MAX_IMAGE_PIXELS = None  # 或者设置一个合理的最大像素数


def split_image_into_nine(image_path, output_folder):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

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
                cropped_img.save(os.path.join(output_folder, f'part_{i + 1}_{j + 1}.png'))


if __name__ == "__main__":
    # 图片路径和输出文件夹
    image_path = r'D:\OneDrive\桌面\19 -》 20.png'
    output_folder = r'D:\OneDrive\桌面\output'

    # 调用函数
    split_image_into_nine(image_path, output_folder)