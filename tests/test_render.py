from src.utils.render import _is_dot_balanced, render_result_to_html


def test_is_dot_balanced_true_for_valid_dot():
    assert _is_dot_balanced('digraph g { a -> b [label="ok"]; }') is True


def test_is_dot_balanced_false_for_unclosed_quote():
    dot = 'digraph rule {\n  subgraph cluster_after { x [label="x\'\']; a -> b; }\n}'
    assert _is_dot_balanced(dot) is False


def test_is_dot_balanced_false_for_unbalanced_braces():
    assert _is_dot_balanced('digraph g { a -> b;') is False


def test_is_dot_balanced_false_for_unquoted_apostrophe_in_identifier():
    assert _is_dot_balanced("digraph rule { v -> v'; }") is False


def test_is_dot_balanced_true_for_apostrophe_inside_quoted_label():
    assert _is_dot_balanced('digraph rule { x [label="x\'"]; }') is True


def test_render_result_to_html_flags_malformed_graph_block(tmp_path, monkeypatch):
    monkeypatch.setattr("src.utils.render.OUTPUT_DIR", tmp_path)
    text = (
        "prose\n"
        "```dot\ndigraph ok { a -> b; }\n```\n"
        "```dot\ndigraph bad { x [label=\"oops]; }\n```\n"
    )

    path = render_result_to_html(text, label="test")
    html = path.read_text(encoding="utf-8")

    assert '"digraph ok { a -> b; }"' in html
    assert "Malformed graph syntax" in html
    assert "digraph bad" in html
