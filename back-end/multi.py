import os
from min import process_literature
from openpyxl import Workbook
from pathlib import Path
import time

# 路径统一
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LITERATURE_FOLDER = os.path.join(BASE_DIR, 'literature')
RESULT_FILE = os.path.join(BASE_DIR, 'results', 'literature_summary.xlsx')

wb = Workbook()
ws = wb.active
ws.title = "文献总结"

headers = [
    "文件名", "作者", "发表年份", "研究区域", "研究目标", 
    "数据源", "研究方法", "时间跨度", "空间尺度", "光污染水平",
    "变化趋势", "测量指标", "数据类型", "主要驱动力", 
    "边界效应", "区域差异", "保护区类型", "地理特征", 
    "主要结论", "创新点", "局限性", "管理建议", 
    "分析技术", "模型方法", "验证方式", "精度评估"]
ws.append(headers)

if not os.path.exists(LITERATURE_FOLDER):
    os.makedirs(LITERATURE_FOLDER)

for filename in os.listdir(LITERATURE_FOLDER):
    if filename.endswith(".pdf"):
        file_path = os.path.join(LITERATURE_FOLDER, filename)
        try:
            row_data = process_literature(file_path)
            ws.append(row_data)
            print(f"已处理: {filename}")
        except Exception as e:
            print(f"处理 {filename} 时出错: {str(e)}")
        time.sleep(50)

if not os.path.exists(os.path.dirname(RESULT_FILE)):
    os.makedirs(os.path.dirname(RESULT_FILE))
wb.save(RESULT_FILE)
print(f"文献总结已保存到 {RESULT_FILE}")
