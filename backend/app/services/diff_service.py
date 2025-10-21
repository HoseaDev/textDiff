"""
差异比较服务
基于 difflib 实现文本差异算法
"""
import difflib
from typing import List, Dict, Tuple, Optional
from ..schemas.document import DiffChange


class DiffService:
    """文本差异比较服务"""

    @staticmethod
    def compute_diff(
        old_text: str,
        new_text: str,
        diff_mode: str = "semantic",
        ignore_whitespace: bool = False,
        ignore_case: bool = False,
    ) -> Tuple[List[DiffChange], Dict]:
        """
        计算两个文本之间的差异

        Args:
            old_text: 旧文本
            new_text: 新文本
            diff_mode: 差异模式 (character, word, line, semantic)
            ignore_whitespace: 是否忽略空白字符
            ignore_case: 是否忽略大小写

        Returns:
            差异列表和统计信息
        """
        # 文本预处理
        if ignore_whitespace:
            old_text = " ".join(old_text.split())
            new_text = " ".join(new_text.split())

        if ignore_case:
            old_text = old_text.lower()
            new_text = new_text.lower()

        # 根据模式选择差异算法
        if diff_mode == "line":
            return DiffService._line_diff(old_text, new_text)
        elif diff_mode == "word":
            return DiffService._word_diff(old_text, new_text)
        elif diff_mode == "character":
            return DiffService._character_diff(old_text, new_text)
        else:  # semantic (默认)
            return DiffService._semantic_diff(old_text, new_text)

    @staticmethod
    def _line_diff(old_text: str, new_text: str) -> Tuple[List[DiffChange], Dict]:
        """行级差异比较"""
        old_lines = old_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)

        diff = difflib.unified_diff(old_lines, new_lines, lineterm="")
        changes = []
        stats = {"added": 0, "deleted": 0, "modified": 0, "unchanged": 0}

        # 使用 SequenceMatcher 获取更详细的差异信息
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                stats["unchanged"] += i2 - i1
                # 添加未变化的内容，用于显示完整文本
                changes.append(
                    DiffChange(
                        type="unchanged",
                        old_text="".join(old_lines[i1:i2]),
                        new_text="".join(old_lines[i1:i2]),
                        old_line_start=i1 + 1,
                        old_line_end=i2,
                        new_line_start=i1 + 1,
                        new_line_end=i2,
                    )
                )
            elif tag == "replace":
                stats["modified"] += max(i2 - i1, j2 - j1)
                changes.append(
                    DiffChange(
                        type="modified",
                        old_text="".join(old_lines[i1:i2]),
                        new_text="".join(new_lines[j1:j2]),
                        old_line_start=i1 + 1,
                        old_line_end=i2,
                        new_line_start=j1 + 1,
                        new_line_end=j2,
                    )
                )
            elif tag == "delete":
                stats["deleted"] += i2 - i1
                changes.append(
                    DiffChange(
                        type="deleted",
                        old_text="".join(old_lines[i1:i2]),
                        old_line_start=i1 + 1,
                        old_line_end=i2,
                    )
                )
            elif tag == "insert":
                stats["added"] += j2 - j1
                changes.append(
                    DiffChange(
                        type="added",
                        new_text="".join(new_lines[j1:j2]),
                        new_line_start=j1 + 1,
                        new_line_end=j2,
                    )
                )

        return changes, stats

    @staticmethod
    def _word_diff(old_text: str, new_text: str) -> Tuple[List[DiffChange], Dict]:
        """单词级差异比较"""
        old_words = old_text.split()
        new_words = new_text.split()

        matcher = difflib.SequenceMatcher(None, old_words, new_words)
        changes = []
        stats = {"added": 0, "deleted": 0, "modified": 0, "unchanged": 0}

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                stats["unchanged"] += i2 - i1
                # 添加未变化的内容，用于显示完整文本
                changes.append(
                    DiffChange(
                        type="unchanged",
                        old_text=" ".join(old_words[i1:i2]),
                        new_text=" ".join(old_words[i1:i2]),
                    )
                )
            elif tag == "replace":
                stats["modified"] += max(i2 - i1, j2 - j1)
                changes.append(
                    DiffChange(
                        type="modified",
                        old_text=" ".join(old_words[i1:i2]),
                        new_text=" ".join(new_words[j1:j2]),
                    )
                )
            elif tag == "delete":
                stats["deleted"] += i2 - i1
                changes.append(
                    DiffChange(type="deleted", old_text=" ".join(old_words[i1:i2]))
                )
            elif tag == "insert":
                stats["added"] += j2 - j1
                changes.append(
                    DiffChange(type="added", new_text=" ".join(new_words[j1:j2]))
                )

        return changes, stats

    @staticmethod
    def _character_diff(old_text: str, new_text: str) -> Tuple[List[DiffChange], Dict]:
        """字符级差异比较"""
        matcher = difflib.SequenceMatcher(None, old_text, new_text)
        changes = []
        stats = {"added": 0, "deleted": 0, "modified": 0, "unchanged": 0}

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                stats["unchanged"] += i2 - i1
                # 添加未变化的内容，用于显示完整文本
                changes.append(
                    DiffChange(
                        type="unchanged",
                        old_text=old_text[i1:i2],
                        new_text=old_text[i1:i2],
                    )
                )
            elif tag == "replace":
                stats["modified"] += max(i2 - i1, j2 - j1)
                changes.append(
                    DiffChange(
                        type="modified",
                        old_text=old_text[i1:i2],
                        new_text=new_text[j1:j2],
                    )
                )
            elif tag == "delete":
                stats["deleted"] += i2 - i1
                changes.append(DiffChange(type="deleted", old_text=old_text[i1:i2]))
            elif tag == "insert":
                stats["added"] += j2 - j1
                changes.append(DiffChange(type="added", new_text=new_text[j1:j2]))

        return changes, stats

    @staticmethod
    def _semantic_diff(old_text: str, new_text: str) -> Tuple[List[DiffChange], Dict]:
        """
        语义级差异比较
        结合行级和字符级差异，提供更智能的对比结果
        """
        # 先进行行级对比
        old_lines = old_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)

        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        changes = []
        stats = {"added": 0, "deleted": 0, "modified": 0, "unchanged": 0}

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                stats["unchanged"] += i2 - i1
                # 添加未变化的内容，用于显示完整文本
                changes.append(
                    DiffChange(
                        type="unchanged",
                        old_text="".join(old_lines[i1:i2]),
                        new_text="".join(old_lines[i1:i2]),
                        old_line_start=i1 + 1,
                        old_line_end=i2,
                        new_line_start=i1 + 1,
                        new_line_end=i2,
                    )
                )
            elif tag == "replace":
                # 对于替换的行，进行字符级对比以显示具体变化
                old_chunk = "".join(old_lines[i1:i2])
                new_chunk = "".join(new_lines[j1:j2])

                # 如果变化很小，显示详细的字符级差异
                similarity = difflib.SequenceMatcher(None, old_chunk, new_chunk).ratio()
                if similarity > 0.3:  # 相似度超过30%，认为是修改
                    stats["modified"] += 1
                    changes.append(
                        DiffChange(
                            type="modified",
                            old_text=old_chunk,
                            new_text=new_chunk,
                            old_line_start=i1 + 1,
                            old_line_end=i2,
                            new_line_start=j1 + 1,
                            new_line_end=j2,
                        )
                    )
                else:  # 否则分别标记为删除和添加
                    stats["deleted"] += i2 - i1
                    stats["added"] += j2 - j1
                    changes.append(
                        DiffChange(
                            type="deleted",
                            old_text=old_chunk,
                            old_line_start=i1 + 1,
                            old_line_end=i2,
                        )
                    )
                    changes.append(
                        DiffChange(
                            type="added",
                            new_text=new_chunk,
                            new_line_start=j1 + 1,
                            new_line_end=j2,
                        )
                    )
            elif tag == "delete":
                stats["deleted"] += i2 - i1
                changes.append(
                    DiffChange(
                        type="deleted",
                        old_text="".join(old_lines[i1:i2]),
                        old_line_start=i1 + 1,
                        old_line_end=i2,
                    )
                )
            elif tag == "insert":
                stats["added"] += j2 - j1
                changes.append(
                    DiffChange(
                        type="added",
                        new_text="".join(new_lines[j1:j2]),
                        new_line_start=j1 + 1,
                        new_line_end=j2,
                    )
                )

        return changes, stats

    @staticmethod
    def generate_html_diff(old_text: str, new_text: str) -> str:
        """
        生成 HTML 格式的差异报告（可选功能）
        """
        differ = difflib.HtmlDiff()
        return differ.make_file(
            old_text.splitlines(),
            new_text.splitlines(),
            fromdesc="旧版本",
            todesc="新版本",
            context=True,
            numlines=3,
        )
