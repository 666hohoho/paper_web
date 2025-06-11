from pathlib import Path
from openai import OpenAI
from openpyxl import Workbook
import json
import os

def process_literature(file_path):
    # 初始化 OpenAI 客户端
    client = OpenAI(
        api_key="sk-BvBtk34mZJ3FBqi82F9EBIjmkNIy4jsbCHjgCC0r8STKMtY5",
        base_url="https://api.moonshot.cn/v1",
    )

    # 上传文件到 API
    file_object = client.files.create(file=Path(file_path), purpose="file-extract")

    # 获取文件内容
    file_content = client.files.content(file_id=file_object.id).text

    # 构建对话消息
    messages = [
        {
            "role": "system",
            "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
        },
        {
            "role": "system",
            "content": file_content,
        },
        {
            "role": "user",
            "content": "请分析这篇文献，提取以下信息并以json格式输出：文件名、作者、发表年份、研究区域、研究目标、数据源、研究方法、时间跨度、空间尺度、光污染水平、变化趋势、测量指标、数据类型、主要驱动力、边界效应、区域差异、保护区类型、地理特征、主要结论、创新点、局限性、管理建议、分析技术、模型方法、验证方式、精度评估。如果某个字段在文献中没有明确提及，请填写'未提及'",
        },
    ]

    # 调用 chat-completion API 获取回答
    completion = client.chat.completions.create(
        model="moonshot-v1-32k",
        messages=messages,
        temperature=0.3,
    )

    # 解析返回的 JSON 数据
    response_content = completion.choices[0].message.content
    #print("大模型输出的结果:")
    #print(response_content)


    parsed_data = json.loads(response_content)


    # 提取所有字段
    authors = parsed_data.get("作者", "未知")
    publish_year = parsed_data.get("发表年份", "未知")
    research_area = parsed_data.get("研究区域", "未知")
    research_goal = parsed_data.get("研究目标", "未知")
    data_source = parsed_data.get("数据源", "未知")
    research_method = parsed_data.get("研究方法", "未知")
    time_span = parsed_data.get("时间跨度", "未知")
    spatial_scale = parsed_data.get("空间尺度", "未知")
    light_pollution_level = parsed_data.get("光污染水平", "未知")
    trend = parsed_data.get("变化趋势", "未知")
    indicator = parsed_data.get("测量指标", "未知")
    data_type = parsed_data.get("数据类型", "未知")
    driving_force = parsed_data.get("主要驱动力", "未知")
    boundary_effect = parsed_data.get("边界效应", "未知")
    regional_difference = parsed_data.get("区域差异", "未知")
    reserve_type = parsed_data.get("保护区类型", "未知")
    geo_feature = parsed_data.get("地理特征", "未知")
    main_conclusion = parsed_data.get("主要结论", "未知")
    innovation = parsed_data.get("创新点", "未知")
    limitation = parsed_data.get("局限性", "未知")
    management_advice = parsed_data.get("管理建议", "未知")
    analysis_technique = parsed_data.get("分析技术", "未知")
    model_method = parsed_data.get("模型方法", "未知")
    validation = parsed_data.get("验证方式", "未知")
    accuracy = parsed_data.get("精度评估", "未知")

    # 将字典或者列表类型的数据转换为字符串
    def dict_to_str(val):
        return json.dumps(val, ensure_ascii=False) if isinstance(val, (dict, list)) else val

    authors = dict_to_str(authors)
    publish_year = dict_to_str(publish_year)
    research_area = dict_to_str(research_area)
    research_goal = dict_to_str(research_goal)
    data_source = dict_to_str(data_source)
    research_method = dict_to_str(research_method)
    time_span = dict_to_str(time_span)
    spatial_scale = dict_to_str(spatial_scale)
    light_pollution_level = dict_to_str(light_pollution_level)
    trend = dict_to_str(trend)
    indicator = dict_to_str(indicator)
    data_type = dict_to_str(data_type)
    driving_force = dict_to_str(driving_force)
    boundary_effect = dict_to_str(boundary_effect)
    regional_difference = dict_to_str(regional_difference)
    reserve_type = dict_to_str(reserve_type)
    geo_feature = dict_to_str(geo_feature)
    main_conclusion = dict_to_str(main_conclusion)
    innovation = dict_to_str(innovation)
    limitation = dict_to_str(limitation)
    management_advice = dict_to_str(management_advice)
    analysis_technique = dict_to_str(analysis_technique)
    model_method = dict_to_str(model_method)
    validation = dict_to_str(validation)
    accuracy = dict_to_str(accuracy)

    # 准备写入 Excel 的数据
    row_data = [
        Path(file_path).name, authors, publish_year, research_area, research_goal,
        data_source, research_method, time_span, spatial_scale, light_pollution_level,
        trend, indicator, data_type, driving_force, boundary_effect, regional_difference,
        reserve_type, geo_feature, main_conclusion, innovation, limitation, management_advice,
        analysis_technique, model_method, validation, accuracy]

    # 确保输出为 JSON 格式
    print(json.dumps(row_data, ensure_ascii=False))

    # 返回处理后的数据
    return row_data

if __name__ == "__main__":
    # 仅在直接运行此文件时使用默认路径
    default_file_path = os.path.join(os.path.dirname(__file__), 'literature', 'test.pdf')
    process_literature(default_file_path)
