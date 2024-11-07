"""
This app turns a single-frame gif into a double-frame one.
"""


import logging
import os
import shutil

import imageio
import numpy as np
from PIL import Image, ImageSequence

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def process_gif_folder(folder_path):
    # 创建Processed子目录
    output_dir = os.path.join(os.getcwd(), 'Processed')
    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith('.gif'):
            file_path = os.path.join(folder_path, file_name)
            with Image.open(file_path) as img:
                # 获取GIF的帧数
                frames = [frame.copy().convert("RGBA")
                          for frame in ImageSequence.Iterator(img)]

                logging.info(f"Processing {file_name} with { \
                             len(frames)} frames")
                if len(frames) > 1:
                    # 多帧GIF直接复制到Processed目录
                    shutil.copy(file_path, output_dir)
                else:
                    # 单帧GIF将唯一帧复制并生成2帧动画
                    frames = [frames[0].copy() for _ in range(2)]

                    # 修改每一帧的左上角像素，确保内容不同
                    for i, frame in enumerate(frames):
                        pixels = np.array(frame)
                        pixels[0, 0] = (i * 50 % 255, 0, 0,
                                        255)  # 修改左上角像素的红色通道
                        frames[i] = Image.fromarray(pixels)

                    save_path = os.path.join(output_dir, file_name)

                    # 使用imageio保存GIF
                    duration = img.info.get('duration', 100) / 1000.0  # 转换为秒
                    imageio.mimsave(save_path, [np.array(frame)
                                    for frame in frames], duration=duration)


# 使用示例
folder_path = './Download'  # 替换为您存放原GIF文件的文件夹路径
process_gif_folder(folder_path)
