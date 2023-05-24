import unittest
import platform
import graphviz as gv
import os
from src.visualizer import *

class TestMakeNode(unittest.TestCase):
    def setUp(self):
        self.graph = gv.Digraph()
        self.nodes = set()

    def test_empty_set(self):
        code = "New_Course"
        makeNodeIfNotExists(self.graph, self.nodes, code, "CIS")
        self.assertIn(code, self.nodes)

    def test_course_in_nodes(self):
        code = "New_Course"
        self.nodes = set([code])
        makeNodeIfNotExists(self.graph, self.nodes, code, "CIS")
        self.assertIn(code, self.nodes)
        self.assertEqual(len(self.nodes), 1)

    def test_multiple_courses(self):
        codes = ["c1", "c2", "c3"]
        self.nodes = set()
        for code in codes:
            makeNodeIfNotExists(self.graph, self.nodes, code, "CIS")
            assert code in self.nodes
        assert len(self.nodes) == 3

class TestFileFlag(unittest.TestCase):
    def setUp(self):
        self.graph = gv.Digraph()

    def test_pdf(self):
        checkFileType(self.graph, "pdf")

    def test_png(self):
        checkFileType(self.graph, "png")

    def test_json(self):
        checkFileType(self.graph, 'json')

    def test_bmp(self):
        checkFileType(self.graph, 'bmp')

    def test_cgimage(self):
        checkFileType(self.graph, 'cgimage')

    def test_canon(self):
        checkFileType(self.graph, 'canon')

    def test_dot(self):
        checkFileType(self.graph, 'dot')

    def test_gv(self):
        checkFileType(self.graph, 'gv')

    def test_xdot(self):
        checkFileType(self.graph, 'xdot')

    def test_eps(self):
        checkFileType(self.graph, 'eps')

    def test_exr(self):
        checkFileType(self.graph, 'exr')

    def test_gif(self):
        checkFileType(self.graph, 'gif')

    def test_ico(self):
        checkFileType(self.graph, 'ico')

    def test_jpg(self):
        checkFileType(self.graph, 'jpg')

    def test_jpeg(self):
        checkFileType(self.graph, 'jpeg')

    def test_pic(self):
        checkFileType(self.graph, 'pic')

    def test_plain(self):
        checkFileType(self.graph, 'plain')

    def test_ps(self):
        checkFileType(self.graph, 'ps')

    def test_svg(self):
        checkFileType(self.graph, 'svg')

if __name__ == '__main__':
    unittest.main()
