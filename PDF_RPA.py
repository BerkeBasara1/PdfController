import PyPDF2
import re
import difflib
from collections import Counter
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.colors import red, green

class PDFTextFormatter:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text = ""

    def extract_text_from_pdf(self):
        with open(self.pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                self.text += reader.pages[page_num].extract_text()

    def format_text(self):
        # Temizleme işlemleri
        self.text = re.sub(r'(\w)(\s{2,})(\w)', r'\1 \3', self.text)  # Kelimeler arasında fazla boşlukları düzeltme
        self.text = re.sub(r'\s+', ' ', self.text)  # Fazla boşlukları temizleme
        self.text = re.sub(r'\s([.,;:!?])', r'\1', self.text)  # Noktalama işaretlerinden önceki boşlukları temizleme
        self.text = re.sub(r'([.,;:!?])([A-Za-z])', r'\1 \2', self.text)  # Noktalama işaretlerinden sonraki boşlukları ekleme
        self.text = re.sub(r'(\d)(\s+)(\d)', r'\1\3', self.text)  # Sayılar arasında fazla boşlukları düzeltme
        self.text = re.sub(r'\s+\n', '\n', self.text).strip()  # Satır başındaki boşlukları temizleme
        
        # Paragrafları ayırma
        formatted_text = ""
        lines = self.text.split('\n')
        for line in lines:
            if line.strip():
                formatted_text += line.strip() + ' '
            else:
                formatted_text = formatted_text.strip() + '\n\n'
        
        self.text = re.sub(r'\n\n+', '\n\n', formatted_text)  # Fazla boş satırları temizleme

    def get_formatted_text(self):
        self.extract_text_from_pdf()
        self.format_text()
        return self.text.strip()

def highlight_differences(text1, text2):
    diff = difflib.ndiff(text1.split(), text2.split())
    highlighted_text1 = []
    highlighted_text2 = []

    for word in diff:
        if word.startswith('- '):
            highlighted_text1.append(f"<font color='red'><u>{word[2:]}</u></font>")
        elif word.startswith('+ '):
            highlighted_text2.append(f"<font color='green'><u>{word[2:]}</u></font>")
        else:
            word = word[2:]
            highlighted_text1.append(word)
            highlighted_text2.append(word)
    
    return ' '.join(highlighted_text1), ' '.join(highlighted_text2)

def compare_pdfs(pdf_path1, pdf_path2):
    formatter1 = PDFTextFormatter(pdf_path1)
    text1 = formatter1.get_formatted_text()
    
    formatter2 = PDFTextFormatter(pdf_path2)
    text2 = formatter2.get_formatted_text()

    # Benzerlik yüzdesini hesaplama
    sequence_matcher = difflib.SequenceMatcher(None, text1, text2)
    similarity_percentage = sequence_matcher.ratio() * 100

    # Farklı kelimeleri bulma
    words1 = Counter(re.findall(r'\w+', text1))
    words2 = Counter(re.findall(r'\w+', text2))
    
    diff_words1 = words1 - words2
    diff_words2 = words2 - words1
    
    different_words_count = sum(diff_words1.values()) + sum(diff_words2.values())

    # Farklı kelimeleri metinlerde belirterek gösterme
    highlighted_text1, highlighted_text2 = highlight_differences(text1, text2)

    return similarity_percentage, different_words_count, highlighted_text1, highlighted_text2

def create_pdf(text, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    for line in text.split('\n'):
        story.append(Paragraph(line, styles['Normal']))
    doc.build(story)

# PDF dosyalarının yolları
pdf_path1 = r"C:\Users\berkeb\Desktop\1. Belge.pdf"
pdf_path2 = r"C:\Users\berkeb\Desktop\2. Belge.pdf"

# PDF'leri kıyaslama
similarity_percentage, different_words_count, highlighted_text1, highlighted_text2 = compare_pdfs(pdf_path1, pdf_path2)

# Benzerlik yüzdesini ve farklı kelime sayısını yazdırma
print(f"Benzerlik Yüzdesi: {similarity_percentage:.2f}%")
print(f"Farklı Kelime Sayısı: {different_words_count}")

# Terminalde farkları yazdırma
print("Birinci PDF'nin Farklı Kelimeleri:")
print(highlighted_text1.replace('<font color=\'red\'><u>', '\033[4m\033[91m').replace('</u></font>', '\033[0m'))

print("İkinci PDF'nin Farklı Kelimeleri:")
print(highlighted_text2.replace('<font color=\'green\'><u>', '\033[4m\033[92m').replace('</u></font>', '\033[0m'))

# Yeni PDF dosyalarını oluşturma
output_path1 = r"C:\Users\berkeb\Desktop\1. Belge_highlighted.pdf"
output_path2 = r"C:\Users\berkeb\Desktop\2. Belge_highlighted.pdf"
create_pdf(highlighted_text1, output_path1)
create_pdf(highlighted_text2, output_path2)
