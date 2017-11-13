# coding:utf8
import sys
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class NewVisitorTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = "http://" + arg.split("=")[1]
                return
            super().setUpClass()
            cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            super().tearDownClass()


    def setUp(self):
        self.browser = webdriver.Firefox(timeout=10)
        # 隐式等待
        self.browser.implicitly_wait(10)

    def tearDown(self):
        self.browser.quit()

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element_by_id("id_list_table")
        rows = table.find_elements_by_tag_name("tr")
        self.assertIn(row_text, [row.text for row in rows])
        return

    def test_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get(self.server_url)
        self.browser.set_window_size(1024, 768)
        # 判断标题和头部是否都包含 To-Do
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name("h1").text
        self.assertIn('To-Do', header_text)

        # 输入一个待办事项
        inputbox = self.browser.find_element_by_id("id_new_item")
        self.assertEqual(
            inputbox.get_attribute("placeholder"),
            "Enter a to-do item"
        )
        # 测试 输入框居中显示
        self.assertAlmostEqual(inputbox.location['x'] + inputbox.size['width'] / 2,
                               512,
                               delta=5)

        # 输入 "Buy peacock feathers"
        inputbox.send_keys("Buy peacock feathers")

        # 按下回车键 页面刷新
        # 待办事项表格中显示 "1: Buy peacock feathers"
        inputbox.send_keys(Keys.ENTER)

        time.sleep(1)
        # 跳转到新的页面 专属此用户的页面
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')
        self.check_for_row_in_list_table('1: Buy peacock feathers')

        # 页面中还有一个文本框  继续输入待办事项
        inputbox = self.browser.find_element_by_id("id_new_item")
        # 测试 输入框居中显示
        self.assertAlmostEqual(inputbox.location['x'] + inputbox.size['width'] / 2,
                               512,
                               delta=5)

        # 输入 "Use peacock feathers to make a fly"
        inputbox.send_keys("Use peacock feathers to make a fly")
        inputbox.send_keys(Keys.ENTER)

        time.sleep(1)
        self.check_for_row_in_list_table('1: Buy peacock feathers')
        self.check_for_row_in_list_table('2: Use peacock feathers to make a fly')

        # 测试另一用户无法看到上一用户的信息
        self.browser.quit()
        self.browser = webdriver.Firefox()

        self.browser.get(self.server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertNotIn('make a fly', page_text)

        # 新用户进行输入
        # 输入一个待办事项
        inputbox = self.browser.find_element_by_id("id_new_item")
        inputbox.send_keys("Buy milk")
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        # 测试此页面仅显示 新用户信息
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacock feathers', page_text)
        self.assertIn('Buy milk', page_text)

        self.fail("Finish the test!")
        return