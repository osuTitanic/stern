function insertBBCode(event) {
    event.preventDefault();
    event.returnValue = false;
    var element = event.target;

    if (element.tagName !== 'BUTTON') {
        element = element.parentElement // whyyy
    }

    var bbcodeTag = element.getAttribute('data-bbcode-tag');
    var property = element.getAttribute('data-property');
    var noClose = element.getAttribute('data-no-close');

    var parent = element.parentElement;
    var editor = parent.parentElement.querySelector('textarea');

    if (editor && bbcodeTag) {
        var start = editor.selectionStart;
        var end = editor.selectionEnd;
        var selectedText = editor.value.substring(start, end);
        var beforeText = editor.value.substring(0, start);
        var afterText = editor.value.substring(end);
        var bbcodeTagStart = "[" + bbcodeTag + "]";
        var bbcodeTagEnd = "[/" + bbcodeTag + "]";

        if (property !== null) {
            bbcodeTagStart = "[" + bbcodeTag + "=" + property + "]";
        }

        if (noClose !== null) {
            bbcodeTagEnd = "";
        }

        editor.value = beforeText + bbcodeTagStart + selectedText + bbcodeTagEnd + afterText;
        editor.focus();
        editor.selectionStart = start + bbcodeTag.length + 2;
        editor.selectionEnd = end + bbcodeTag.length + 2;
    }
}

elements = document.querySelectorAll('#bbcode-toolbar')

for (var i = 0; i < elements.length; i++) {
    elements[i].addEventListener('click', insertBBCode);
}
