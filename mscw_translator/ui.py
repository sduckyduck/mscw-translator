from __future__ import annotations

import pyperclip
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .capture import ScreenCaptureService
from .glossary_service import GlossaryService
from .ocr import OCRService
from .replies import ReplyService
from .translator import TranslatorService


class CaptureWorker(QThread):
    finished_text = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, capture: ScreenCaptureService, ocr: OCRService) -> None:
        super().__init__()
        self.capture = capture
        self.ocr = ocr

    def run(self) -> None:
        try:
            image = self.capture.capture_default_chat_area()
            text = self.ocr.read_image(image)
            self.finished_text.emit(text)
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MSCW Translator")
        self.setMinimumSize(720, 720)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.capture = ScreenCaptureService()
        self.ocr = OCRService()
        self.glossary = GlossaryService()
        self.translator = TranslatorService()
        self.replies = ReplyService()
        self.worker: CaptureWorker | None = None

        self.source_box = QTextEdit()
        self.source_box.setPlaceholderText("OCR result or paste English chat here. Example: LF> bishop for cpq")
        self.term_box = QTextEdit()
        self.term_box.setReadOnly(True)
        self.translation_box = QTextEdit()
        self.translation_box.setReadOnly(True)
        self.reply_box = QTextEdit()
        self.reply_box.setReadOnly(True)

        capture_btn = QPushButton("Capture chat area + OCR")
        capture_btn.clicked.connect(self.capture_and_ocr)

        translate_btn = QPushButton("Explain + Translate")
        translate_btn.clicked.connect(self.translate_current_text)

        copy_source_btn = QPushButton("Copy source")
        copy_source_btn.clicked.connect(lambda: pyperclip.copy(self.source_box.toPlainText()))

        copy_translation_btn = QPushButton("Copy translation")
        copy_translation_btn.clicked.connect(lambda: pyperclip.copy(self.translation_box.toPlainText()))

        button_row = QHBoxLayout()
        button_row.addWidget(capture_btn)
        button_row.addWidget(translate_btn)
        button_row.addWidget(copy_source_btn)
        button_row.addWidget(copy_translation_btn)

        layout = QVBoxLayout()
        title = QLabel("MSCW Translator - screen OCR, glossary translation, quick replies")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        if not self.ocr.available:
            warn = QLabel("OCR backend is not available. You can still paste text manually. Install PaddleOCR for real OCR.")
            warn.setStyleSheet("color: #a65f00;")
            layout.addWidget(warn)

        layout.addLayout(button_row)
        layout.addWidget(QLabel("Original / OCR text"))
        layout.addWidget(self.source_box, stretch=2)
        layout.addWidget(QLabel("Recognized MapleStory terms"))
        layout.addWidget(self.term_box, stretch=1)
        layout.addWidget(QLabel("Chinese translation / explanation"))
        layout.addWidget(self.translation_box, stretch=2)
        layout.addWidget(QLabel("Quick reply suggestions"))
        layout.addWidget(self.reply_box, stretch=1)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def capture_and_ocr(self) -> None:
        if not self.ocr.available:
            QMessageBox.information(self, "OCR not ready", "PaddleOCR is not available. Paste chat text manually for now.")
            return
        self.worker = CaptureWorker(self.capture, self.ocr)
        self.worker.finished_text.connect(self.on_ocr_done)
        self.worker.failed.connect(self.on_worker_failed)
        self.worker.start()

    def on_ocr_done(self, text: str) -> None:
        self.source_box.setPlainText(text or "")
        self.translate_current_text()

    def on_worker_failed(self, message: str) -> None:
        QMessageBox.warning(self, "Capture failed", message)

    def translate_current_text(self) -> None:
        text = self.source_box.toPlainText().strip()
        terms = self.glossary.explain(text)
        self.term_box.setPlainText(terms)
        self.translation_box.setPlainText(self.translator.translate_to_chinese(text, terms))
        reply_lines = []
        for label, reply in self.replies.suggest(text):
            reply_lines.append(label + ": " + reply)
        self.reply_box.setPlainText("\n".join(reply_lines))


def run_app() -> int:
    app = QApplication([])
    window = MainWindow()
    window.show()
    return app.exec()
