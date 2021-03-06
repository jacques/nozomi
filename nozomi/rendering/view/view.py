"""
Nozomi
View Module
author: hugh@blinkybeach.com
"""
from typing import Optional, Dict, Any, List
from nozomi.rendering.view_template import ViewTemplate
from nozomi.rendering.context import Context
from nozomi.rendering.static_context import StaticContext
from nozomi.rendering.open_graph import OpenGraph


class View:
    """
    An abstract class providing functionality useful for building
    views - That is, web pages that application users will view and
    interact with.

    View is an abstract class that is expected to be inherited by
    a concrete class. For example, an Splash page might be formed
    of a class Splash(View).
    """

    STANDARD_STYLES: List[str] = []
    STANDARD_CLASSES: List[str] = []
    STANDARD_SCRIPTS: List[str] = []

    _transient_context = None

    def __init__(
        self,
        template: str,
        title: str,
        description: str,
        key_words: List[str],
        styles: List[str],
        scripts: List[str],
        classes: List[str],
        open_graph: Optional[OpenGraph] = None,
        static_variables: Optional[Dict[str, Any]] = None,
        static_js_constants: Optional[Dict[str, Any]] = None
    ) -> None:

        self._template_name = template
        assert isinstance(self._template_name, str)
        assert self._template_name[-5:] == '.html'

        assert isinstance(styles, list)
        assert False not in [isinstance(s, str) for s in styles]
        all_styles = self.STANDARD_STYLES + styles

        assert isinstance(classes, list)
        assert False not in [isinstance(c, str) for c in classes]
        for jsclass in classes:
            assert jsclass not in self.STANDARD_CLASSES
        all_classes = self.STANDARD_CLASSES + classes

        assert isinstance(scripts, list)
        assert False not in [isinstance(s, str) for s in scripts]
        for script in scripts:
            assert script not in self.STANDARD_SCRIPTS
        all_scripts = scripts + self.STANDARD_SCRIPTS

        assert isinstance(title, str)
        if open_graph is not None:
            assert isinstance(open_graph, OpenGraph)
        assert isinstance(description, str)
        assert isinstance(key_words, list)
        assert False not in [isinstance(k, str) for k in key_words]

        static_context = StaticContext(
            all_styles,
            all_scripts,
            all_classes,
            title,
            open_graph,
            description,
            key_words,
            static_variables,
            static_js_constants
        )

        self._template = ViewTemplate(
            self._template_name,
            static_context
        )

        return

    def serve(self) -> str:
        """
        Return a string response to a request
        """
        return self._render()

    def _render(self) -> str:
        """
        Return a string rendering of this view
        """
        html = self._template.render(self._transient_context)
        self._transient_context = None
        return html

    def generate_context(self) -> Context:
        """Return a transient context for use in rendering the view"""
        self._transient_context = Context()
        return self._transient_context
