import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
from weasyprint import HTML
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

TEMPLATE_DIR = "templates"
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def generate_plan_documents(data, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 収支計算
    df = data['projection_data'].copy()
    df['売上総利益'] = df['売上高'] - df['売上原価']
    # （中略：以前の計算ロジック）

    # PDF生成（日本語フォントを強制指定）
    main_template = env.get_template('main_plan_template.html')
    # 日本語フォント IPAexGothic を使うようにCSSをHTML側に書くのがコツです
    html_out = main_template.render(data=data)
    
    p1 = os.path.join(output_dir, "plan.pdf")
    p2 = os.path.join(output_dir, "projection.pdf")
    p3 = os.path.join(output_dir, "plan.xlsx")
    
    HTML(string=html_out).write_pdf(p1)
    # 収支表も同様に生成...
    df.to_excel(p3)
    
    return p1, p2, p3
