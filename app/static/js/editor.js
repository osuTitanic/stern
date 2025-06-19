function insertBBCode(event) {
    event.preventDefault();
    event.returnValue = false;
    var element = event.target;

    if (element.tagName !== 'BUTTON') {
        element = getParentElement(element) // whyyy
    }

    var bbcodeTag = element.getAttribute('data-bbcode-tag');
    var property = element.getAttribute('data-property');
    var noClose = element.getAttribute('data-no-close');

    var parent = getParentElement(element);
    var textAreas = getParentElement(parent).getElementsByTagName('textarea');
    
    if (textAreas.length === 0) {
        console.warn("No text area found in the parent element.");
        return;
    }

    var editor = textAreas[0];

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

function insertImageBBCode(textarea, url) {
    var bbcodeTagStart = "[img]";
    var bbcodeTagEnd = "[/img]";

    var start = textarea.selectionStart;
    var end   = textarea.selectionEnd;

    var beforeText = textarea.value.substring(0, start);
    var afterText = textarea.value.substring(end);

    var fullTag = bbcodeTagStart + url + bbcodeTagEnd;
    textarea.value = beforeText + fullTag + afterText;

    // Move the caret to just after the inserted tag:
    var newCaretPos = beforeText.length + fullTag.length;
    textarea.focus();
    textarea.selectionStart = textarea.selectionEnd = newCaretPos;
}

var editors = document.getElementsByClassName('bbcode-editor');
var isUploading = false;

for (var i = 0; i < editors.length; i++) {
    var editor = editors[i];

    addEvent('paste', editor, function(event) {
        var editor = event.target;

        if (!event.clipboardData) {
            return;
        }

        var items = event.clipboardData.items;
        if (!items) {
            return;
        }

        if (isUploading) {
            return;
        }

        isUploading = true;

        // Find the first “image/*” item in the clipboard items:
        for (var i = 0; i < items.length; i++) {
            var item = items[i];

            if (item.kind !== 'file' || item.type.indexOf('image') !== 0) {
                // Not an image file, skip it.
                continue;
            }

            // We’ve found an image in the clipboard.
            // Prevent the default “pasting” of the image
            event.preventDefault();
            event.stopPropagation();

            var blob = item.getAsFile();
            if (!blob) {
                continue;
            }

            var formData = new FormData();
            formData.append('input', blob);

            performApiRequest("POST", "/forum/images", formData, function (xhr) {
                setTimeout(function() { isUploading = false }, 1000);
                var response = JSON.parse(xhr.responseText);
                var imageUrl = response.image.image.url;
                insertImageBBCode(editor, imageUrl);
            }, function (xhr) {
                setTimeout(function() { isUploading = false }, 1000);
            });
            return;
        }
    });
}

var toolbars = document.getElementsByClassName('bbcode-toolbar')

for (var i = 0; i < toolbars.length; i++) {
    addEvent('click', toolbars[i], insertBBCode);
}
