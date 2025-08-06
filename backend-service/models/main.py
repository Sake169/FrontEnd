# 基本使用
from integrated_api import IntegratedDocumentProcessor

# processor = IntegratedDocumentProcessor(output_dir="./output")
# result = processor.process_document_from_file("document.pdf")

processor = IntegratedDocumentProcessor(
    output_dir="./output",
    template_path="./backend-service/models/qwen-api-framework/filled_template.xlsx"
)
result = processor.process_document_from_file('/Users/jackliu/AI_Services/ai_manage/AiInvestmentFilingPlatform/【范例】投资申报/【范例】基金E账户持仓/基金E账户App投资者公募基金持有信息-【2025-02-26】.xlsx',
                        model_type='pipeline')