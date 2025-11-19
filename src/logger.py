"""
로깅 유틸리티 모듈

전체 분석 파이프라인의 로깅을 중앙에서 관리합니다.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "ureter_stone_analysis",
    level: str = "INFO",
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    로거를 설정합니다.

    Args:
        name: 로거 이름
        level: 로깅 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 로그 파일 경로 (None이면 파일에 저장하지 않음)

    Returns:
        설정된 Logger 객체
    """
    logger = logging.getLogger(name)

    # 레벨 설정
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 기존 핸들러 제거 (중복 방지)
    logger.handlers = []

    # 포맷터 설정
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (옵션)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.info(f"로그 파일 생성: {log_file}")

    return logger


def get_logger(name: str = "ureter_stone_analysis") -> logging.Logger:
    """
    기존 로거를 가져옵니다.

    Args:
        name: 로거 이름

    Returns:
        Logger 객체
    """
    return logging.getLogger(name)
