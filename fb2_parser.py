#! /usr/bin/env python3

import xml.etree.ElementTree as ET
import os


class FB2Parser:
    def __init__(self, filename, external_annotations=True):
        self.root = ET.parse(filename).getroot()
        self.cleanup()
        self.external_annotations = external_annotations

    def cleanup(self):
        for element in self.root.iter():
                element.tag = element.tag.partition('}')[-1]

    def is_flat(self):
        return self.root.find('./body/section/section') is None

    def extract(self):
        self._book_title = self.root.find('./description/title-info/book-title').text
        self._main, *rest, self._annotations = self.root.findall('body')
        if self.is_flat():
            self.write(self.split(self._main))
        else:
            for part_id, part in enumerate(self._main.findall('section')):
                self.write(self.split(part, id=part_id))
        self.write_description()
        if self._annotations and self.external_annotations:
            self.write_annotations()

    def split(self, section, id=None):
        part_title = section.find('./title/p').text
        parts = {}
        for chapter_id, chapter in enumerate(section.findall('section')):
            chapter_title = chapter.find('./title/p').text
            part_path = '%02d_%s' % (id, part_title) if id is not None else ''
            chapter_path = os.path.join(part_path,
                                        '%02d_%s.fb2' % (chapter_id, chapter_title))
            path = os.path.join('.', self._book_title, chapter_path)
            parts[path] = chapter
        return parts

    def write_description(self):
        path = os.path.join('.', self._book_title, 'description.fb2')
        fb = ET.Element('FictionBook', attrib={'xmlns': "http://www.gribuser.ru/xml/fictionbook/2.0"})
        fb.append(self.root.find('description'))
        images = self.root.find('binary')
        if images:
            fb.append(images)
        book = ET.ElementTree(fb)
        book.write(path, encoding='utf-8', xml_declaration=True)

    def write_annotations(self):
        path = os.path.join('.', self._book_title, 'annotations.fb2')
        self.write({path: self._annotations})

    def write(self, data):
        for path, chapter in data.items():
            dir = os.path.dirname(path)
            fb = ET.Element('FictionBook',
                            attrib={'xmlns': "http://www.gribuser.ru/xml/fictionbook/2.0"})
            body = ET.SubElement(fb, 'body')
            body.append(chapter)
            if self._annotations and not self.external_annotations:
                body.append(self._annotations)
            book = ET.ElementTree(fb)
            os.makedirs(dir, exist_ok=True)
            book.write(path, encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    FB2Parser('gmn.fb2').extract()



