
from markdown.extensions.toc import TocTreeprocessor, TocExtension

class Treeprocessor(TocTreeprocessor):
    def build_toc_div(self, toc_list):
        if not toc_list:
            return super().build_toc_div(toc_list)
        
        if toc_list[0]['level'] != 1:
            return super().build_toc_div(toc_list)

        # Remove first element of toc_list, to
        # remove the title of the article
        element = toc_list.pop(0)

        # Append remaining children to toc_list
        toc_list.extend(element['children'])

        # Continue with the original method
        return super().build_toc_div(toc_list)

TocExtension.TreeProcessorClass = Treeprocessor
