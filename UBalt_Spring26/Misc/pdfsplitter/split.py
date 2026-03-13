import pymupdf
import os
from pathlib import Path
import glob

INPUT_FOLDER  = './sources'      
OUTPUT_FOLDER = './extracted'   

def split_pdf(pdf_path, output_folder):
    doc = pymupdf.open(pdf_path)
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    for i in range(len(doc)):
        new_pdf = pymupdf.open()
        new_pdf.insert_pdf(doc, from_page=i, to_page=i)
        new_pdf.save(os.path.join(output_folder, f'page_{i+1:03d}.pdf'))
        new_pdf.close()

    print(f'✔ {Path(pdf_path).name}  →  {len(doc)} pages  →  {output_folder}')
    doc.close()

def batch_split(input_folder, output_base):
    pdf_files = glob.glob(os.path.join(input_folder, '*.pdf'))

    if not pdf_files:
        print(f'No PDFs found in {INPUT_FOLDER} folder')
        return

    for pdf_file in pdf_files:
        pdf_stem = Path(pdf_file).stem
        subfolder = os.path.join(output_base, pdf_stem)   
        split_pdf(pdf_file, subfolder)

    print(f'\nDone. {len(pdf_files)} PDFs processed.')

batch_split(INPUT_FOLDER, OUTPUT_FOLDER)
