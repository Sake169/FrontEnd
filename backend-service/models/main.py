# 基本使用
from integrated_api import IntegratedDocumentProcessor

# processor = IntegratedDocumentProcessor(output_dir="./output")
# result = processor.process_document_from_file("document.pdf")

# 使用模板
processor = IntegratedDocumentProcessor(
    output_dir="./output",
    template_path="/Users/jackliu/AI_Services/ai_manage/AiInvestmentFilingPlatform/template.xlsx"
)
result = processor.process_document_from_file("/Users/jackliu/AI_Services/ai_manage/AiInvestmentFilingPlatform/test/投资任职情况查询报告.pdf",
                        model_type='vlm-transformers')