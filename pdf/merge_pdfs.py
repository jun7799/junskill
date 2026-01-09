#!/usr/bin/env python3
"""合并PDF文件"""

from pypdf import PdfWriter, PdfReader
import sys
import os

def merge_pdfs(input_files, output_file):
    """合并多个PDF文件"""
    writer = PdfWriter()

    for pdf_file in input_files:
        if not os.path.exists(pdf_file):
            print(f"错误：文件 '{pdf_file}' 不存在")
            return False

        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                writer.add_page(page)
            print(f"已添加: {pdf_file} ({len(reader.pages)} 页)")
        except Exception as e:
            print(f"读取文件 '{pdf_file}' 时出错: {e}")
            return False

    try:
        with open(output_file, "wb") as output:
            writer.write(output)
        print(f"\n合并成功！输出文件: {output_file}")
        return True
    except Exception as e:
        print(f"写入输出文件时出错: {e}")
        return False

if __name__ == "__main__":
    # PDF文件列表（使用绝对路径）
    base_dir = r"C:\Users\44162\Desktop\测试项目"
    pdf_files = [
        os.path.join(base_dir, "教育部学籍在线验证报告_柯文俊.pdf"),
        os.path.join(base_dir, "测试的.pdf")
    ]

    output_file = os.path.join(base_dir, "合并文档.pdf")

    print("开始合并PDF文件...")
    merge_pdfs(pdf_files, output_file)
