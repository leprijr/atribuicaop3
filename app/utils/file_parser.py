import pandas as pd
import pdfplumber
import docx
import os
import re


def parse_classification_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.csv':
        return _parse_csv(filepath)
    elif ext == '.xlsx':
        return _parse_xlsx(filepath)
    elif ext == '.docx':
        return _parse_docx(filepath)
    elif ext == '.doc':
        return _parse_doc(filepath)
    elif ext == '.pdf':
        return _parse_pdf(filepath)
    else:
        raise ValueError(f'Formato não suportado: {ext}')


def _parse_csv(filepath):
    df = pd.read_csv(filepath)
    return _df_to_rows(df)


def _parse_xlsx(filepath):
    df = pd.read_excel(filepath, engine='openpyxl')
    return _df_to_rows(df)


def _parse_docx(filepath):
    doc = docx.Document(filepath)
    text = '\n'.join([p.text for p in doc.paragraphs])
    return _parse_text_table(text)


def _parse_doc(filepath):
    try:
        import subprocess
        result = subprocess.run(
            ['antiword', filepath],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return _parse_text_table(result.stdout)
    except Exception:
        pass
    try:
        import olefile
        import zlib
        ole = olefile.OleFileIO(filepath)
        if ole.exists('WordDocument'):
            stream = ole.openstream('WordDocument')
            data = stream.read()
            text = data.decode('utf-8', errors='ignore')
            return _parse_text_table(text)
    except Exception:
        pass
    raise ValueError('Não foi possível processar o arquivo DOC. Converta para DOCX ou use outro formato.')


def _parse_pdf(filepath):
    text = ''
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
    return _parse_text_table(text)


def _parse_text_table(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    results = []
    for line in lines:
        parts = re.split(r'[;\t|,]+', line)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 3:
            try:
                classification = float(parts[2].replace(',', '.'))
            except ValueError:
                continue
            results.append({
                'teacher': parts[0],
                'subject': parts[1],
                'classification': classification
            })
    if not results:
        raise ValueError(
            'Nenhum dado válido encontrado. O arquivo deve conter colunas: Professor, Disciplina, Classificação '
            '(separadas por vírgula, ponto e vírgula, tabulação ou pipe)'
        )
    return results


def _df_to_rows(df):
    df.columns = [str(c).strip().lower() for c in df.columns]
    teacher_col = None
    subject_col = None
    classif_col = None
    for col in df.columns:
        if any(t in col for t in ['professor', 'teacher', 'docente', 'nome']):
            teacher_col = col
        elif any(t in col for t in ['disciplina', 'subject', 'materia', 'matéria']):
            subject_col = col
        elif any(t in col for t in ['classificacao', 'classificação', 'classification', 'nota', 'nota_final']):
            classif_col = col

    if not all([teacher_col, subject_col, classif_col]):
        cols = list(df.columns)
        if len(cols) >= 3:
            teacher_col = cols[0]
            subject_col = cols[1]
            classif_col = cols[2]

    results = []
    for _, row in df.iterrows():
        try:
            classification = float(str(row[classif_col]).replace(',', '.'))
            results.append({
                'teacher': str(row[teacher_col]).strip(),
                'subject': str(row[subject_col]).strip(),
                'classification': classification
            })
        except (ValueError, KeyError):
            continue
    return results
