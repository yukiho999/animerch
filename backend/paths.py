# ============================================
# 项目路径工具 — 解决相对路径问题
# ============================================
import os


def get_project_root() -> str:
    """向上查找包含 config.yaml 的目录"""
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        if os.path.exists(os.path.join(current, "config.yaml")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    # fallback: cwd
    return os.getcwd()


def resolve_path(path: str) -> str:
    """把相对路径转成绝对路径（基于项目根目录）"""
    if os.path.isabs(path):
        return path
    return os.path.join(get_project_root(), path)
