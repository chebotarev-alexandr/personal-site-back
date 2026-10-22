/* Инициализация EasyMDE для всех textarea с классом .markdown-editor.
   Работает в том числе для форм, добавленных динамически (inline). */
(function () {
  'use strict';

  function init(scope) {
    var root = scope || document;
    var areas = root.querySelectorAll('textarea.markdown-editor');
    areas.forEach(function (ta) {
      if (ta.dataset.easymde === '1') return;
      ta.dataset.easymde = '1';
      new EasyMDE({
        element: ta,
        spellChecker: false,
        status: false,
        autosave: { enabled: false },
        minHeight: '320px',
        toolbar: [
          'bold', 'italic', 'heading', '|',
          'quote', 'unordered-list', 'ordered-list', '|',
          'link', 'image', 'code', '|',
          'preview', 'side-by-side', 'fullscreen', 'guide'
        ]
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
})();
