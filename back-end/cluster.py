import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import time

from sklearn.cluster import KMeans
from tqdm.notebook import tqdm
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
warnings.filterwarnings("ignore")
pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',300)


from dotenv import load_dotenv, find_dotenv
#load_dotenv(find_dotenv(), override=True)
from openai import OpenAI

def process_literature(result_path, api_host, api_key, col):
    
    df =pd.read_excel(result_path)
    df=df[df.columns.tolist()]
    print(f"original size of the data set: {df.shape}")

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


    df['text_embedding'] = df[col].apply(lambda x: get_embedding(x, model='text-embedding-3-small'))
    #print(f"向量长度: {len(df['text_embedding'][0])}")  # 应为 1536（text-embedding-3-small）

    def calculate_silhouette_scores(data_matrix, min_clusters=3, max_clusters=25):
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

    matrix = np.vstack(df['text_embedding'].values)

    cluster_results_km = calculate_silhouette_scores(matrix)
    num_cluster = find_optimal_cluster(cluster_results_km)


    km_model = KMeans(n_clusters = num_cluster, init ='k-means++', random_state = 42)
    y = km_model.fit_predict(matrix)
    df['Cluster']=y

    for i in range(num_cluster):
        # 获取当前cluster的研究目标
        cluster_texts = df.loc[df['Cluster'] == i, ' Research Objective'].dropna().astype(str)

        if not cluster_texts.empty:  # 检查是否有数据
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

    df.to_excel('topic.xlsx')

if __name__ == "__main__":
    # 仅在直接运行此文件时使用默认路径
    default_file_path = os.path.join(os.path.dirname(__file__), 'results', 'literature_summary.xlsx')
    process_literature(default_file_path)