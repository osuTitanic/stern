function getSelectionRange(textarea) {
    if (typeof textarea.selectionStart === 'number' && typeof textarea.selectionEnd === 'number') {
        return {
            start: textarea.selectionStart,
            end: textarea.selectionEnd
        };
    }

    if (document.selection && textarea.createTextRange) {
        textarea.focus();
        var selectedRange = document.selection.createRange();
        var duplicateRange = selectedRange.duplicate();
        duplicateRange.moveToElementText(textarea);
        duplicateRange.setEndPoint('EndToEnd', selectedRange);

        var selectedText = selectedRange.text || '';
        var end = duplicateRange.text.length;
        var start = end - selectedText.length;

        if (start < 0) {
            start = 0;
        }
        if (end < start) {
            end = start;
        }

        return {
            start: start,
            end: end
        };
    }

    var length = textarea.value.length;
    return {
        start: length,
        end: length
    };
}

function setSelectionRangeCompat(textarea, start, end) {
    if (textarea.setSelectionRange) {
        textarea.setSelectionRange(start, end);
        return;
    }

    if (textarea.createTextRange) {
        var range = textarea.createTextRange();
        range.collapse(true);
        range.moveStart('character', start);
        range.moveEnd('character', end - start);
        range.select();
    }
}

function insertBBCode(event) {
    event = event || window.event;
    preventEventDefault(event);
    var element = getEventTarget(event);

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
        var selection = getSelectionRange(editor);
        var start = selection.start;
        var end = selection.end;
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
        setSelectionRangeCompat(editor, start + bbcodeTag.length + 2, end + bbcodeTag.length + 2);
    }
}

function insertImageBBCode(textarea, content) {
    var bbcodeTagStart = "[img]";
    var bbcodeTagEnd = "[/img]";

    var selection = getSelectionRange(textarea);
    var start = selection.start;
    var end   = selection.end;

    var beforeText = textarea.value.substring(0, start);
    var afterText = textarea.value.substring(end);

    var fullTag = bbcodeTagStart + content + bbcodeTagEnd;
    textarea.value = beforeText + fullTag + afterText;

    // Move the caret to just after the inserted tag:
    var newCaretPos = beforeText.length + fullTag.length;
    textarea.focus();
    setSelectionRangeCompat(textarea, newCaretPos, newCaretPos);
}

function replaceImageBBCode(textarea, oldContent, newContent) {
    var bbcodeTagStart = "[img]";
    var bbcodeTagEnd = "[/img]";
    var oldTag = bbcodeTagStart + oldContent + bbcodeTagEnd;
    var newTag = bbcodeTagStart + newContent + bbcodeTagEnd;

    var value = textarea.value;
    var replaced = false;

    // Replace all occurrences of oldTag with newTag
    var newValue = value.split(oldTag).join(newTag);
    replaced = newValue !== value;
    textarea.value = newValue;

    if (replaced) {
        // Move caret to just after the last replaced tag
        var lastIndex = newValue.lastIndexOf(newTag);
        if (lastIndex !== -1) {
            var newCaretPos = lastIndex + newTag.length;
            textarea.focus();
            setSelectionRangeCompat(textarea, newCaretPos, newCaretPos);
        }
    }
}

var editors = getElementsByClassName('bbcode-editor');
var isUploading = false;

for (var i = 0; i < editors.length; i++) {
    var editor = editors[i];

    addEvent('paste', editor, function(event) {
        event = event || window.event;
        var editor = getEventTarget(event);

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
            preventEventDefault(event);
            stopEventPropagation(event);

            var blob = item.getAsFile();
            if (!blob) {
                continue;
            }

            var uploadPrompt = "Uploading " + blob.name + "...";
            insertImageBBCode(editor, uploadPrompt);

            var formData = new FormData();
            formData.append('input', blob);

            performApiRequest("POST", "/forum/images", formData, function (xhr) {
                setTimeout(function() { isUploading = false }, 1000);
                var response = JSON.parse(xhr.responseText);
                var imageUrl = response.image.image.url;
                replaceImageBBCode(editor, uploadPrompt, imageUrl);
            }, function (xhr) {
                setTimeout(function() { isUploading = false }, 1000);
            });
            return;
        }
    });
}

var toolbars = getElementsByClassName('bbcode-toolbar')

for (var i = 0; i < toolbars.length; i++) {
    addEvent('click', toolbars[i], insertBBCode);
}
