"""
Simple client server unit test
"""

import logging
import threading
import unittest

import clientserver
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)


class TestEchoService(unittest.TestCase):
    """The test"""
    _server = clientserver.Server()  # create single server in class variable
    _server_thread = threading.Thread(target=_server.receiveGet)  # define thread for running server

    @classmethod
    def setUpClass(cls):
        cls._server_thread.start()  # start server loop in a thread (called only once)

    def setUp(self):
        super().setUp()
        self.client = clientserver.Client()  # create new client for each test

    # def test_srv_get(self):  # each test_* function is a test
    #     """Test simple call"""
    #     msg = self.client.call("Hello VS2Lab")
    #     self.assertEqual(msg, 'Hello VS2Lab*')

        
    def test_get_name(self):
        """Test get methode"""
        print("Search 'Tim'")
        msg = self.client.get("Tim")
        self.assertEqual(msg,'456-789-0123')
        
    def test_get_name2(self):
        """Test get methode"""
        print("Search 'Kevin'")
        msg = self.client.get("Kevin")
        self.assertEqual(msg,'123-456-7890')

    def test_get_noname(self):
        """Test get with wrong name"""
        print("Suche 'Kare'")
        msg = self.client.get("Kare")
        self.assertEqual(msg,'not found')
    
    def test_getall(self):
        """Test getall method"""
        expected_msg = (
           "('Kevin', '123-456-7890')\n"
            "('Tim', '456-789-0123')\n"
            "('Chris', '789-012-3456')\n"
            "('Maxi', '012-345-6789')\n"
            "('Lex', '234-567-8901')\n"
            "('Max', '345-678-9012')\n"
            "('Tom', '456-789-0123')\n"
            "('Hanka', '567-890-1234')\n"
            "('Victoria', '678-901-2345')\n"
            "('Ailana', '789-012-3456')\n"
            "('Katrin', '890-123-4567')\n"
            "('Karsten', '901-234-5678')\n"
            "('Joachim', '012-345-6789')\n"
            "('Gertrud', '123-456-7890')\n"
            "('Moritz', '234-567-8901')\n"
            "('David', '345-678-9012')\n"
            "('Mohammed', '456-789-0123')\n"
            "('Abdel', '567-890-1234')\n"
            "('Christian', '678-901-2345')\n"
            "('Patrick', '789-012-3456')\n"
            "('Johannes', '890-123-4567')"
        )
        
    def tearDown(self):
        self.client.close()  # terminate client after each test

    @classmethod
    def tearDownClass(cls):
        cls._server._serving = False  # break out of server loop. pylint: disable=protected-access
        cls._server_thread.join()  # wait for server thread to terminate


if __name__ == '__main__':
    unittest.main()
