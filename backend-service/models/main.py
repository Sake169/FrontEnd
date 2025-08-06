# 基本使用
from integrated_api import IntegratedDocumentProcessor

# processor = IntegratedDocumentProcessor(output_dir="./output")
# result = processor.process_document_from_file("document.pdf")

# 使用模板
processor = IntegratedDocumentProcessor(
    output_dir="./output",
    template_path="/Users/jackliu/AI_Services/ai_manage/AiInvestmentFilingPlatform/template.xlsx"
)
result = processor.process_document_from_file("/Users/jackliu/AI_Services/ai_manage/AiInvestmentFilingPlatform/test/基金E账户App投资者公募基金持有信息-【2025-02-26】.xlsx",
                        model_type='pipeline')