from __future__ import annotations

import pyperclip
from PyQt6.QtCore import QPoint, QRect, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QPainter, QPen, QColor
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

from .capture import CaptureRegion, ScreenCaptureService
from .glossary_service import GlossaryService
from .ocr import OCRService
from .replies import ReplyService
from .translator import TranslatorService


class RegionSelectOverlay(QWidget):
    region_selected = pyqtSignal(QRect)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.start_pos = QPoint()
        self.end_pos = QPoint()
        self.is_selecting = False

    def mousePressEvent(self, event) -> None:
        self.start_pos = event.position().toPoint()
        self.end_pos = self.start_pos
        self.is_selecting = True
        self.update()

    def mouseMoveEvent(self, event) -> None:
        if self.is_selecting:
            self.end_pos = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        self.end_pos = event.position().toPoint()
        self.is_selecting = False
        rect = QRect(self.start_pos, self.end_pos).normalized()
        self.hide()
        if rect.width() > 10 and rect.height() > 10:
            self.region_selected.emit(rect)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 90))
        if not self.start_pos.isNull() and not self.end_pos.isNull():
            rect = QRect(self.start_pos, self.end_pos).normalized()
            painter.setPen(QPen(QColor(255, 210, 80), 3))
            painter.drawRect(rect)
            painter.fillRect(rect, QColor(255, 210, 80, 35))


class CaptureWorker(QThread):
    finished_text = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, capture: ScreenCaptureService, ocr: OCRService, region: CaptureRegion | None = None) -> None:
        super().__init__()
        self.capture = capture
        self.ocr = ocr
        self.region = region

    def run(self) -> None:
        try:
            if self.region is None:
                image = self.capture.capture_default_chat_area()
            else:
                image = self.capture.capture_region(self.region)
            text = self.ocr.read_image(image)
            self.finished_text.emit(text)
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("冒险岛聊天翻译器")
        self.setMinimumSize(760, 760)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.capture = ScreenCaptureService()
        self.ocr = OCRService()
        self.glossary = GlossaryService()
        self.translator = TranslatorService()
        self.replies = ReplyService()
        self.worker: CaptureWorker | None = None
        self.overlay: RegionSelectOverlay | None = None

        self.source_box = QTextEdit()
        self.source_box.setPlaceholderText("在这里粘贴英文聊天，或点击截图识别。例如：LF> bishop for cpq")
        self.term_box = QTextEdit()
        self.term_box.setReadOnly(True)
        self.translation_box = QTextEdit()
        self.translation_box.setReadOnly(True)
        self.reply_box = QTextEdit()
        self.reply_box.setReadOnly(True)

        default_capture_btn = QPushButton("识别默认聊天区")
        default_capture_btn.clicked.connect(self.capture_default_area)

        select_capture_btn = QPushButton("框选截图识别")
        select_capture_btn.clicked.connect(self.select_region_and_capture)

        translate_btn = QPushButton("翻译/解析")
        translate_btn.clicked.connect(self.translate_current_text)

        copy_source_btn = QPushButton("复制原文")
        copy_source_btn.clicked.connect(lambda: pyperclip.copy(self.source_box.toPlainText()))

        copy_translation_btn = QPushButton("复制翻译")
        copy_translation_btn.clicked.connect(lambda: pyperclip.copy(self.translation_box.toPlainText()))

        copy_reply_btn = QPushButton("复制第一条回复")
        copy_reply_btn.clicked.connect(self.copy_first_reply)

        button_row = QHBoxLayout()
        button_row.addWidget(default_capture_btn)
        button_row.addWidget(select_capture_btn)
        button_row.addWidget(translate_btn)
        button_row.addWidget(copy_source_btn)
        button_row.addWidget(copy_translation_btn)
        button_row.addWidget(copy_reply_btn)

        layout = QVBoxLayout()
        title = QLabel("冒险岛聊天翻译器：截图 OCR + 术语词库 + 快捷回复")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(title)

        status_text = "OCR 状态："
        if self.ocr.available:
            status_text += "已启用 " + self.ocr.backend_name
            status_color = "#2e8b57"
        else:
            status_text += "未启用。仍可手动粘贴文字翻译。请安装 PaddleOCR / paddlepaddle 后重启。"
            status_color = "#d18a00"
        warn = QLabel(status_text)
        warn.setStyleSheet("color: " + status_color + ";")
        layout.addWidget(warn)

        tip = QLabel("使用建议：游戏开窗口化或无边框窗口化。先用‘框选截图识别’选择聊天框区域，识别后会自动翻译。")
        tip.setWordWrap(True)
        layout.addWidget(tip)

        layout.addLayout(button_row)
        layout.addWidget(QLabel("原文 / OCR 识别文本"))
        layout.addWidget(self.source_box, stretch=2)
        layout.addWidget(QLabel("识别到的冒险岛术语"))
        layout.addWidget(self.term_box, stretch=1)
        layout.addWidget(QLabel("中文翻译 / 解释"))
        layout.addWidget(self.translation_box, stretch=2)
        layout.addWidget(QLabel("快捷英文回复建议"))
        layout.addWidget(self.reply_box, stretch=1)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def capture_default_area(self) -> None:
        self.start_ocr_worker(region=None)

    def select_region_and_capture(self) -> None:
        if not self.ocr.available:
            QMessageBox.information(self, "OCR 未启用", "当前没有可用 OCR。请先安装 PaddleOCR，或直接手动粘贴文字。")
            return
        self.hide()
        QApplication.processEvents()
        self.overlay = RegionSelectOverlay()
        self.overlay.region_selected.connect(self.on_region_selected)
        self.overlay.show()

    def on_region_selected(self, rect: QRect) -> None:
        self.show()
        screen = QGuiApplication.primaryScreen()
        ratio = screen.devicePixelRatio() if screen else 1
        region = CaptureRegion(
            left=int(rect.left() * ratio),
            top=int(rect.top() * ratio),
            width=int(rect.width() * ratio),
            height=int(rect.height() * ratio),
        )
        self.start_ocr_worker(region=region)

    def start_ocr_worker(self, region: CaptureRegion | None) -> None:
        if not self.ocr.available:
            QMessageBox.information(self, "OCR 未启用", "当前没有可用 OCR。请先安装 PaddleOCR，或直接手动粘贴文字。")
            return
        self.worker = CaptureWorker(self.capture, self.ocr, region=region)
        self.worker.finished_text.connect(self.on_ocr_done)
        self.worker.failed.connect(self.on_worker_failed)
        self.worker.start()

    def on_ocr_done(self, text: str) -> None:
        if not text.strip():
            QMessageBox.information(self, "没有识别到文字", "这次截图没有识别到文字。请放大聊天框，或重新框选更准确的区域。")
            return
        self.source_box.setPlainText(text)
        self.translate_current_text()

    def on_worker_failed(self, message: str) -> None:
        QMessageBox.warning(self, "截图识别失败", message)

    def translate_current_text(self) -> None:
        text = self.source_box.toPlainText().strip()
        terms = self.glossary.explain(text)
        self.term_box.setPlainText(terms)
        self.translation_box.setPlainText(self.translator.translate_to_chinese(text, terms))
        reply_lines = []
        for label, reply in self.replies.suggest(text):
            reply_lines.append(label + "：" + reply)
        self.reply_box.setPlainText("\n".join(reply_lines))

    def copy_first_reply(self) -> None:
        first_line = self.reply_box.toPlainText().splitlines()[0] if self.reply_box.toPlainText().splitlines() else ""
        if "：" in first_line:
            first_line = first_line.split("：", 1)[1]
        elif ":" in first_line:
            first_line = first_line.split(":", 1)[1]
        pyperclip.copy(first_line.strip())


def run_app() -> int:
    app = QApplication([])
    window = MainWindow()
    window.show()
    return app.exec()
