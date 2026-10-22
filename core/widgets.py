"""Custom admin widgets (rich/markdown editor etc.)."""

from django import forms


class MarkdownEditorWidget(forms.Textarea):
    """Textarea with the EasyMDE markdown editor (toolbar + live preview).

    Stores plain markdown in the field; the frontend renders it to HTML.
    EasyMDE is vendored under core/static/admin/easymde/ (no CDN, works
    offline and from RU).
    """

    class Media:
        css = {"all": ["admin/easymde/easymde.min.css"]}
        js = ["admin/easymde/easymde.min.js", "admin/easymde/init.js"]

    def __init__(self, attrs=None):
        default_attrs = {"class": "markdown-editor", "rows": 14}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
