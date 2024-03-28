from pypdf import PdfReader  # pip install pypdf --upgrade
import re
import datetime
import os

german_month_names = {
        'Januar': "01",
        'Februar': "02",
        'März': "03",
        'April': "04",
        'Mai': "05",
        'Juni': "06",
        'Juli': "07",
        'August': "08",
        'September': "09",
        'Oktober': "10",
        'November': "11",
        'Dezember': "12"
    }


def get_protocol_date_from_pdf_file(filepath):
    pdfFileObj = open(filepath, "rb")
    pdfReader = PdfReader(pdfFileObj)
    pageObj = pdfReader.pages[0]

    # only search in the first 300 characters
    text = pageObj.extract_text()[:300]

    if len(text) < 1:
        print("This protocoll needs OCR embedding")

    results = []

     # search for date in the format 12. Oktober 2022
    match = re.search(r"\d{2}\.\s*(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s*\d{4}", text)
    if match is not None:
        date = match.group(0).replace(" ", "").replace(".", "")
        position = match.start()
        for month in german_month_names:
            date = date.replace(month, german_month_names[month])
        try:
            date = datetime.datetime.strptime(date, "%d%m%Y").date().strftime("%d.%m.%Y")
            results.append({"date": date, "position": position})
        except ValueError:
            date = "Datum unbekannt"
    
    # search for date in the format 12 October 2022
    match = re.search(r"\d{2}\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{4}", text)
    if match is not None:
        date = match.group(0).replace(" ", "").replace(".", "")
        position = match.start()        
        try: 
            date = datetime.datetime.strptime(date, "%d%B%Y").date().strftime("%d.%m.%Y")
            results.append({"date": date, "position": position})
        except ValueError:
            date = "Datum unbekannt"

    # search for date in the format 12. Oktober 2022
    match = re.search(r"\d{1,2}\s*\.\s*[\D]+\s*\d{4}", text)
    if match is not None:
        date = match.group(0).replace(" ", "").replace(".", "")
        position = match.start()
        if date[1] == ".":
            date = "0" + date
        # find it in the german format
        try:
            date = datetime.datetime.strptime(date, "%d%B%Y").date().strftime("%d.%m.%Y") 
            results.append({"date": date, "position": position})
        except ValueError:
            date = "Datum unbekannt"

    # search for date in the format 12.10.2022
    match = re.search(r"\d{1,2}\s*\.\s*\d{1,2}\s*\.\s*\d{4}", text)
    if match is not None:
        date = match.group(0).replace(" ", "").replace(".", "")
        position = match.start()
        if date[1] == ".":
            date = "0" + date
        if date[4] == ".":
            date = date[:3] + "0" + date[3:]
        try:
            date = datetime.datetime.strptime(date, "%d%m%Y").date().strftime("%d.%m.%Y")
            results.append({"date": date, "position": position})
        except ValueError:
            date = "Datum unbekannt"

    if len(results) > 0:
        results = sorted(results, key=lambda x: x["position"])
        return results[0]["date"]
    else:
        return "Datum unbekannt"
    
   

def save_protocol_pages_to_txt(filepath):
    pages = get_text_from_pdf(filepath)
    for page_number, page_content in pages.items():
        if not os.path.exists(filepath[:-4]):
            os.makedirs(filepath[:-4])
        txt_filename = filepath[:-4] + "/" + str(page_number) + ".txt"
        # if there is no text file for the current page, create one
        if not os.path.isfile(txt_filename):
            with open(txt_filename, "w") as text_file:
                text_file.write(page_content)

def get_text_from_pdf(filepath):
    pdfFileObj = open(filepath, "rb")
    pdfReader = PdfReader(pdfFileObj)

    pages = {}
    for i in range(len(pdfReader.pages)):
        pageObj = pdfReader.pages[i]
        pages[i] = pageObj.extract_text()
    
    pdfFileObj.close()

    return pages

from pprint import pprint

if __name__ == "__main__":
    link = "downloads/studierendenkonvent/Sitzungsprotokoll-des-StuKo-vom-14.10.2021.pdf"
    print(get_protocol_date_from_pdf_file(link))
    print()
    pprint(get_text_from_pdf(link)[0])