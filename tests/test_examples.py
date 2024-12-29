import logging
import os
import shutil
import unittest

from cmg.generator import generate
from cmg.schema import Klass
from examples import eda, solar_system

TEST_RUN_DIR = "generated"


class TestExamples(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_RUN_DIR):
            shutil.rmtree(TEST_RUN_DIR)
        os.makedirs(TEST_RUN_DIR)

    def test_eda(self):
        schema = eda.schema
        generate(schema, TEST_RUN_DIR, logging.getLogger("test"))

    def test_solar_system(self):
        schema = solar_system.schema
        generate(schema, TEST_RUN_DIR, logging.getLogger("test"))
