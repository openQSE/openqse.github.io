// Wait for both DOM and Mermaid to be ready
(function () {
    function initMermaid() {
        if (typeof mermaid === 'undefined') {
            setTimeout(initMermaid, 100);
            return;
        }

        // Find and convert all mermaid code blocks
        var blocks = document.querySelectorAll('pre > code.language-mermaid');

        blocks.forEach(function (element) {
            var pre = element.closest('pre');
            var div = document.createElement('div');
            div.className = 'mermaid';
            div.textContent = element.textContent;
            pre.parentElement.replaceChild(div, pre);
        });

        // Initialize and render
        mermaid.initialize({ startOnLoad: true });
        mermaid.run();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMermaid);
    } else {
        initMermaid();
    }
})();