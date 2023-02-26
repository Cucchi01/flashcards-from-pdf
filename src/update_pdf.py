from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QThreadPool, pyqtBoundSignal
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import resolve1
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

import os
import time

from worker_thread import Worker


def update_pdf(path_pdf_to_update: str) -> None:
    path_of_new_pdf: str
    path_of_new_pdf, _ = QFileDialog.getOpenFileName(
        caption="Open file", filter="*.pdf", directory=os.getcwd()
    )

    if is_path_empty(path_of_new_pdf):
        return

    # compare the pdf on a different thread
    threadpool = QThreadPool()
    worker = Worker(compare_two_pdf_text_only, path_pdf_to_update, path_of_new_pdf)
    worker.signals.result.connect(print_output)
    worker.signals.finished.connect(thread_complete)
    worker.signals.progress.connect(progress_fn)
    threadpool.start(worker)

    # compare_two_pdf_text_only(path_pdf_to_update, path_of_new_pdf)
    # compare_pages(path_pdf_to_update, path_of_new_pdf, 0, 3)


def is_path_empty(path: str) -> bool:
    return path == ""


def compare_two_pdf_text_only(
    path_of_pdf_a: str, path_of_pdf_b: str, progress_callback: pyqtBoundSignal
) -> None:
    text_x_page_pdf_a: list[str] = []
    text_x_page_pdf_b: list[str] = []
    text_x_page_pdf: list[str] = []
    num_pages_pdf_a: int
    num_pages_pdf_b: int
    paired_pages_pdf_a: set[int]
    paired_pages_pdf_b: set[int]

    # TODO: speed up the retrival of the data, maybe doing it with different threads one that reads the pdf and the other that does the comparison
    start: float = time.time()
    (text_x_page_pdf_a, num_pages_pdf_a) = get_pdf_data(
        path_of_pdf_a, progress_callback
    )
    print(
        "Time retrival of first pdf: {interval}".format(
            interval=round(time.time() - start)
        )
    )
    (text_x_page_pdf_b, num_pages_pdf_b) = get_pdf_data(
        path_of_pdf_b, progress_callback
    )
    paired_pages_pdf_b = set(range(num_pages_pdf_b))

    print(
        "Time retrival of second pdf: {interval}".format(
            interval=round(time.time() - start)
        )
    )
    text_x_page_pdf = text_x_page_pdf_a + text_x_page_pdf_b

    print("Concatenation: {interval}".format(interval=round(time.time() - start)))

    vectorizer = TfidfVectorizer(min_df=1)
    tfidf_pdf = vectorizer.fit_transform(text_x_page_pdf)

    print("Vectorization: {interval}".format(interval=round(time.time() - start)))

    for index_a in range(num_pages_pdf_a):
        page_pdf_a = np.asarray(tfidf_pdf[index_a].todense())
        page_pdf_b = np.asarray(tfidf_pdf[num_pages_pdf_a:, :].todense())
        val = cosine_similarity(page_pdf_a, page_pdf_b, dense_output=True)
        print(val)

    print("Finished cosine: {interval}".format(interval=round(time.time() - start)))


def get_pdf_data(
    path_of_pdf: str, progress_callback: pyqtBoundSignal
) -> tuple[list[str], int]:
    text_x_page: list[str] = []
    with open(path_of_pdf, "rb") as pdf:
        parser = PDFParser(pdf)
        document = PDFDocument(parser)

        num_pages_pdf = resolve1(document.catalog["Pages"])["Count"]

        for page_index in range(num_pages_pdf):
            progress_callback.emit(round(page_index / num_pages_pdf * 100))
            text_page: str = extract_text(
                pdf,
                page_numbers=[page_index],
                maxpages=1,
            )
            text_x_page.append(text_page)

    return (text_x_page, num_pages_pdf)


def compare_pages(
    first_path_of_pdf: str,
    second_path_of_pdf: str,
    first_page_index: int,
    second_page_index: int,
) -> None:
    first_text: str = extract_text(
        first_path_of_pdf,
        page_numbers=[first_page_index],
        maxpages=1,
    )
    second_text: str = extract_text(
        second_path_of_pdf,
        page_numbers=[second_page_index],
        maxpages=1,
    )
    corpus = [first_text, second_text]
    vect = TfidfVectorizer(min_df=1, stop_words="english")
    tfidf = vect.fit_transform(corpus)
    pairwise_similarity = tfidf * tfidf.T


def progress_fn(n):
    print(n)


def print_output(s):
    print(s)


def thread_complete():
    print("THREAD COMPLETE!")
