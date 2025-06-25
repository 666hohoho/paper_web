import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import time

from sklearn.cluster import KMeans
from tqdm import tqdm
from sklearn.metrics import silhouette_score


from langchain import LLMChain
import openai
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import warnings
import os
import ast
warnings.filterwarnings("ignore")
pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',300)


from dotenv import load_dotenv, find_dotenv
#load_dotenv(find_dotenv(), override=True)
from openai import OpenAI

def cluster_literature(df, api_host, api_key, selected_headers):
    
    df=df[df.columns.tolist()]
    print(f"original size of the data set: {df.shape}")
    print(df.columns.tolist())

    base_url = f"{api_host}/v1"
    client = OpenAI(
    api_key=api_key,
    base_url =base_url)

    def get_embedding(text, model="text-embedding-3-small"):
        text = text.replace("\n", " ")
        response = client.embeddings.create(
            input=[text],
            model=model
        )
        return response.data[0].embedding

    # 把selected_headers的内容合并成一个字符串
    if isinstance(selected_headers, str):
        selected_headers = [selected_headers]
    df['text'] = df[selected_headers].astype(str).agg(' '.join, axis=1)

    df['text_embedding'] = df['text'].apply(lambda x: get_embedding(x, model='text-embedding-3-small'))
    print(df.columns.tolist())
    print(f"向量长度: {len(df['text_embedding'][0])}")  # 应为 1536（text-embedding-3-small）

    # 仅对字符串类型的值应用 ast.literal_eval
    df['text_embedding'] = df['text_embedding'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )

    # 检查嵌套列表长度是否一致
    lengths = df['text_embedding'].apply(len)
    max_length = lengths.max()

    # 填充嵌套列表为相同长度
    df['text_embedding'] = df['text_embedding'].apply(lambda x: x + [0] * (max_length - len(x)))

    # 将嵌套列表转换为二维数值矩阵
    matrix = np.vstack(df['text_embedding'].values)

    def calculate_silhouette_scores(data_matrix, min_clusters=2, max_clusters=len(df)-1):
        cluster_results_km = pd.DataFrame(columns=['k', 'score'])

        for k in tqdm(range(min_clusters, max_clusters + 1)):
            km_model = KMeans(n_clusters=k, init='k-means++', random_state=42)
            y = km_model.fit_predict(data_matrix)
            silhouette = silhouette_score(data_matrix, y)
            dic={'k': [k], 'score': [silhouette]}
            cluster_results_km=pd.concat([cluster_results_km, pd.DataFrame(dic)])
        return cluster_results_km

    def find_optimal_cluster(cluster_results):
        cluster_results = cluster_results.reset_index(drop=True)
        optimal_cluster = cluster_results['score'].idxmax()
        optimal_cluster = cluster_results['k'].iloc[optimal_cluster]
        return optimal_cluster


    cluster_results_km = calculate_silhouette_scores(matrix)
    num_cluster = find_optimal_cluster(cluster_results_km)
    print(num_cluster)


    km_model = KMeans(n_clusters = num_cluster, init ='k-means++', random_state = 42)
    y = km_model.fit_predict(matrix)
    df['Cluster']=y

    for i in range(num_cluster):
        # 获取当前cluster的研究目标
        cluster_texts = df.loc[
            (df['Cluster'] == i) &  # 筛选属于特定 Cluster 的行
            ~df[selected_headers].isin(['处理失败', '未提及']).any(axis=1),  # 去掉包含“处理失败”或“未提及”的行
            selected_headers
        ].dropna().astype(str)  # 去掉空值并转换为字符串

        
        if not cluster_texts.empty:  # 检查是否有数据
            print(cluster_texts.iloc[0])  # 安全访问第一个元素

            # 调用API
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个科研助手，擅长总结研究主题"},
                    {"role": "user", "content": "请用不超过20个中文词总结这类研究的核心目标"},
                    {"role": "user", "content": '; '.join(cluster_texts)}
                ],
                temperature=0.3  # 减少随机性
            )

            # 赋值给对应cluster的行
            summary = completion.choices[0].message.content
            df.loc[df['Cluster'] == i, 'topic'] = summary
        else:
            print(f"警告：Cluster {i}没有有效数据")

    #df去掉text_embedding列
    df = df.drop(columns=['text', 'text_embedding'])
    return df

if __name__ == "__main__":
    # 仅在直接运行此文件时使用默认路径
    df= pd.read_excel('/Users/sunxueyao/Documents/paper_web/back-end/results/literature_summary.xlsx')
    df=cluster_literature(df,api_host='https://api.gptsapi.net',api_key='sk-fW6ed3b49f7fa03dbb8b1f28396f4d69f3f1878bd0aoatl2', selected_headers=['研究内容',' Data Source'])
    df.to_excel('/Users/sunxueyao/Documents/paper_web/back-end/results/literature_summary_clustered.xlsx', index=False)