from flask import Flask, render_template, request, redirect, send_file, after_this_request
from apryse_sdk import PDFNet, PDFDoc, Optimizer, SDFDoc
from pdf2image import convert_from_path
from pdf2pptx import convert_pdf2pptx
from pdf2docx import parse
import zipfile
import PyPDF2
import uuid
import fitz
import os

app = Flask(__name__, static_folder='static')
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'files/uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'files/output')
PAGES_FOLDER = os.path.join(BASE_DIR, 'files/pages')
PDF_FOLDER = os.path.join(BASE_DIR, 'files/pdfs')

for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, PAGES_FOLDER, PDF_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['PAGES_FOLDER'] = PAGES_FOLDER
app.config['PDF_FOLDER'] = PDF_FOLDER


def name_uuid():
    new_uuid = uuid.uuid4()
    return str(new_uuid)

def total_pages(pdf_file):
  with open(pdf_file, 'rb') as pdf:
    pdf_reader = PyPDF2.PdfReader(pdf)
    return len(pdf_reader.pages)
  
def format_page_nos(pagenos):
  page_ranges = []
  for range_str in pagenos.split(','):
    start, end = range_str.split('-')
    page_ranges.append([int(start), int(end)])
  return page_ranges
  
def get_size_format(b, factor=1024, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"




# Index Page
@app.route('/')
def upload_form():
    return render_template('index.html')







# PDF Compress
@app.route('/pdfcompress', methods=['GET','POST'])
def compress_pdf():

    if request.method == 'GET':
        endpoint="/pdfcompress"
        output = "Compressed PDF"
        return render_template('upload.html', endpoint = endpoint, title = output)

    if 'file' not in request.files:
        return redirect("/")

    file = request.files['file']
    if file.filename.lower().endswith('.pdf'):
        input_filename = file.filename.replace(" ","_")
        output_filename = f'{file.filename.replace(" ","_")}_{name_uuid()}.pdf'
        input_filepath = f"{app.config['UPLOAD_FOLDER']}/{input_filename}"
        output_filepath = f"{app.config['OUTPUT_FOLDER']}/{output_filename}"
        file.save(input_filepath)

        initial_size = os.path.getsize(input_filepath)

        try:
            PDFNet.Initialize("demo:1709312703601:7f2e580203000000007ee1b91f359c3c8eaf4e966719e679ff8ede8a22")
            doc = PDFDoc(input_filepath)
            doc.InitSecurityHandler()
            Optimizer.Optimize(doc)
            doc.Save(output_filepath, SDFDoc.e_linearized)
            doc.Close()
        except Exception as e:
            print("Error compress_file=", e)
            doc.Close()

        compressed_size = os.path.getsize(output_filepath)
        ratio = 1 - (compressed_size / initial_size)

        initial_size = get_size_format(initial_size)
        compressed_size = get_size_format(compressed_size)
        ratio = "{0:.3%}.".format(ratio)

        os.remove(input_filepath)
        download_link = f"/download/{output_filename}"

        return render_template('success.html', download_link=download_link, initial_size = initial_size, compressed_size = compressed_size, ratio = ratio)
    else:
        return redirect("/")









# PDF to PPTX
@app.route('/pdf2pptx', methods=['GET','POST'])
def upload_file_to_doc():

    if request.method == 'GET':
        endpoint="/pdf2pptx"
        output = "PDF to PPTX"
        return render_template('upload.html', endpoint = endpoint, title = output)

    if 'file' not in request.files:
        return redirect("/")

    file = request.files['file']
    if file.filename.lower().endswith('.pdf'):
        input_filename = file.filename.replace(" ","_")
        output_filename = f'{file.filename.replace(" ","_")}_{name_uuid()}.pptx'
        input_filepath = f"{app.config['UPLOAD_FOLDER']}/{input_filename}"
        output_filepath = f"{app.config['OUTPUT_FOLDER']}/{output_filename}"
        file.save(input_filepath)
        pages = total_pages(input_filepath)

        convert_pdf2pptx(input_filepath, output_filepath, 500, 0, pages)
        os.remove(input_filepath)
        download_link = f"/download/{output_filename}"

        return render_template('success.html', download_link=download_link)
    else:
        return redirect("/")











# PDF to DOC
@app.route('/pdf2doc', methods=['GET','POST'])
def upload_file_to_pptx():

    if request.method == 'GET':
        endpoint="/pdf2doc"
        output = "PDF to DOC"
        return render_template('upload.html', endpoint = endpoint, title = output)

    if 'file' not in request.files:
        return redirect("/")

    file = request.files['file']
    if file.filename.lower().endswith('.pdf'):
        input_filename = file.filename.replace(" ","_")
        output_filename = f'{file.filename.replace(" ","_")}_{name_uuid()}.docx'
        input_filepath = f"{app.config['UPLOAD_FOLDER']}/{input_filename}"
        output_filepath = f"{app.config['OUTPUT_FOLDER']}/{output_filename}"
        file.save(input_filepath)

        parse(input_filepath, output_filepath)
        os.remove(input_filepath)
        download_link = f"/download/{output_filename}"

        return render_template('success.html', download_link=download_link)
    else:
        return redirect("/")











# PDF to Image
@app.route('/pdf2image', methods=['GET','POST'])
def upload_file_to_image():

    if request.method == 'GET':
        endpoint="/pdf2image"
        output = "PDF to Image"
        return render_template('upload.html', endpoint = endpoint, title = output)

    if 'file' not in request.files:
        return redirect("/")

    file = request.files['file']
    if file.filename.lower().endswith('.pdf'):
        input_filename = file.filename.replace(" ","_")
        output_filename = f'{file.filename.replace(" ","_")}_{name_uuid()}.zip'
        input_filepath = f"{app.config['UPLOAD_FOLDER']}/{input_filename}"
        output_filepath = f"{app.config['OUTPUT_FOLDER']}/{output_filename}"
        file.save(input_filepath)

        images = convert_from_path(input_filepath)
        with zipfile.ZipFile(output_filepath, 'w', zipfile.ZIP_DEFLATED) as zip_archive:
            for i, image in enumerate(images):
                image_file = f"{app.config['PAGES_FOLDER']}/page_{i+1}.jpg"
                image.save(image_file, 'JPEG')
                zip_archive.write(image_file)
                os.remove(image_file)
        
        os.remove(input_filepath)
        download_link = f"/download/{output_filename}"

        return render_template('success.html', download_link=download_link)
    else:
        return redirect("/")
    










# Split PDF
@app.route('/splitpdf', methods=['GET','POST'])
def split_pdf():

    if request.method == 'GET':
        endpoint="/splitpdf"
        output = "Split PDF"
        return render_template('upload.html', endpoint = endpoint, title = output, options = "split")

    if 'file' not in request.files or 'pagenos' not in request.form:
        return redirect("/")
    
    page_ranges = format_page_nos(request.form.get('pagenos'))

    file = request.files['file']
    if file.filename.lower().endswith('.pdf'):
        input_filename = file.filename.replace(" ","_")
        output_filename = f'{file.filename.replace(" ","_")}_{name_uuid()}.zip'
        input_filepath = f"{app.config['UPLOAD_FOLDER']}/{input_filename}"
        output_filepath = f"{app.config['OUTPUT_FOLDER']}/{output_filename}"
        file.save(input_filepath)

        pdf_document = fitz.open(input_filepath)
        ind = 0

        with zipfile.ZipFile(output_filepath, 'w', zipfile.ZIP_DEFLATED) as zip_archive:
          for page_range in page_ranges:
            start_page, end_page = page_range

            if start_page > end_page or start_page < 1 or end_page > pdf_document.page_count:
                print(f"Invalid page range: {page_range}. Skipping...")
                continue
            new_pdf = fitz.open()
            new_pdf.insert_pdf(pdf_document, from_page=start_page - 1, to_page=end_page - 1)
            temp_file_path = f"{app.config['PDF_FOLDER']}/{ind}_pages_{start_page}-{end_page}.pdf"
            ind += 1
            new_pdf.save(temp_file_path)
            zip_archive.write(temp_file_path)
            new_pdf.close()
            os.remove(temp_file_path)

        pdf_document.close()
        ind = 0

        os.remove(input_filepath)
        download_link = f"/download/{output_filename}"

        return render_template('success.html', download_link=download_link)
    else:
        return redirect("/")













# Merge PDFs
@app.route('/mergepdfs', methods=['GET','POST'])
def merge_pdfs():

    if request.method == 'GET':
        endpoint="/mergepdfs"
        output = "Merge PDFs"
        return render_template('upload.html', endpoint = endpoint, title = output, options = "merge")

    if 'pdfs' not in request.files:
        return redirect("/")

    pdfs = request.files.getlist('pdfs')
    pdf_paths = []
    merged_pdf = fitz.open()
    output_filename = f'Merged_PDF_{name_uuid()}.pdf'
    output_filepath = f"{app.config['OUTPUT_FOLDER']}/{output_filename}"
    for pdf in pdfs:
        if not pdf.filename.lower().endswith('.pdf'):
            return redirect("/")
        input_filename = pdf.filename.replace(" ","_")
        input_filepath = f"{app.config['UPLOAD_FOLDER']}/{input_filename}"
        pdf_paths.append(input_filepath)
        pdf.save(input_filepath)
    pdf_paths.sort()

    for pdf_file in pdf_paths:
        pdf_document = fitz.open(pdf_file)
        for page_number in range(pdf_document.page_count):
            merged_pdf.insert_pdf(pdf_document, from_page=page_number, to_page=page_number)
        pdf_document.close()
    merged_pdf.save(output_filepath)
    merged_pdf.close()
    
    for pdf in pdf_paths:
        os.remove(pdf)
    download_link = f"/download/{output_filename}"
    return render_template('success.html', download_link=download_link)










# Download Files
@app.route('/download/<filename>')
def download_file(filename):
    filepath = f"{app.config['OUTPUT_FOLDER']}/{filename}"

    @after_this_request
    def remove_file(response):
        try:
            os.remove(filepath)
        except OSError as e:
            app.logger.error(f"Error deleting file: {e}")
        return response
    try:
        return send_file(filepath, as_attachment=True)
    except FileNotFoundError:
        return render_template("404.html")




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
