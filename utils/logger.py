import logging
import sys

COLOR_MAP = {
    "DEBUG": "\033[36m",
    "INFO": "\033[32m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[1;31m",
    "RESET": "\033[0m",
}


class ColorAlignedFormatter(logging.Formatter):
    def format(self, record):
        # 補齊 level 欄位（帶中括號）
        record.levelname_bracket = f"[{record.levelname}]".ljust(9)
        # 對 filename:lineno 做 padding（檔名 + 行號）
        record.filename_lineno = f"{record.filename}:{record.lineno}".ljust(25)
        # 對 funcName 做 padding
        record.func_padded = record.funcName.ljust(23)

        # 呼叫原 formatter 處理格式
        message = super().format(record)

        # 加上 ANSI 色碼
        color = COLOR_MAP.get(record.levelname, "")
        reset = COLOR_MAP["RESET"]
        return f"{color}{message}{reset}"


formatter = ColorAlignedFormatter(
    fmt="%(asctime)s %(levelname_bracket)s %(filename_lineno)s %(func_padded)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

logging.basicConfig(level=logging.DEBUG, handlers=[console_handler])
