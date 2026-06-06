import os
import pytest
from pathlib import Path
from PIL import Image

from src.core.parser import parse
from src.ast_tree.visualizer import render_ast, expr_to_filename

OUTPUT_DIR = Path("output/trees")


@pytest.fixture(autouse=True)
def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _render(infix: str, rpn: str, result: float = 0.0) -> Path:
    ast = parse(infix)
    fname = expr_to_filename(infix) + ".jpg"
    path = OUTPUT_DIR / fname
    render_ast(ast, infix, rpn, str(path), result=result)
    return path


class TestFileCreated:
    def test_simple_expr_creates_jpg(self):
        path = _render("3 + 4", "3 4 +")
        assert path.exists()
        assert path.suffix == ".jpg"

    def test_function_expr_creates_jpg(self):
        path = _render("sin(3 + 4) * 2", "3 4 + sin 2 *")
        assert path.exists()

    def test_power_expr_creates_jpg(self):
        path = _render("2 ^ (3 + 1)", "2 3 1 + ^")
        assert path.exists()


class TestImageProperties:
    def test_image_is_valid_jpeg(self):
        path = _render("log(100) + 2", "100 log 2 +")
        img = Image.open(path)
        assert img.format == "JPEG"

    def test_image_min_resolution(self):
        path = _render("(3 + 4) * 2", "3 4 + 2 *")
        img = Image.open(path)
        width, height = img.size
        assert width >= 600
        assert height >= 400


class TestFilenameHelper:
    def test_sanitize_parens(self):
        name = expr_to_filename("sin(3 + 4) * 2")
        assert "/" not in name
        assert "\\" not in name

    def test_sanitize_spaces_removed(self):
        name = expr_to_filename("3 + 4")
        assert " " not in name

    def test_max_length(self):
        long_expr = "sin(x)" * 20
        assert len(expr_to_filename(long_expr)) <= 80


class TestAllSupportedExprs:
    @pytest.mark.parametrize("infix,rpn", [
        ("3 + 4",             "3 4 +"),
        ("2 ^ 3",             "2 3 ^"),
        ("sin(0)",            "0 sin"),
        ("cos(0)",            "0 cos"),
        ("tan(0)",            "0 tan"),
        ("log(100)",          "100 log"),
        ("(3 + 4) * 2",       "3 4 + 2 *"),
        ("2 ^ (3 + 1)",       "2 3 1 + ^"),
        ("sin(3 + 4) * 2",    "3 4 + sin 2 *"),
        ("log(100) + 2",      "100 log 2 +"),
    ])
    def test_render_produces_file(self, infix, rpn):
        path = _render(infix, rpn)
        assert path.exists()
