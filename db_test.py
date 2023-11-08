from pdf_utils import PDFUtils
folder_path = './db'
pdfutils = PDFUtils(folder_path)
query = "placenta previa"

docs = pdfutils.get_context(query)
print(docs)
print("testing done")