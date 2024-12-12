import time
import selenium
from selenium.webdriver.common.by import By


class SchemesData:
    def __init__(self, webdriver: selenium, scheme: selenium):
        self.webdriver = webdriver
        self.scheme = scheme
        self.tags_list = []
        self.category_list = []
        self.highlight_list = []
        self.benefit_list = []
        self.eligible_list = []
        self.apply_list = []
        
    def _get_title(self):
        self.title = (self.scheme
                      .find_element(By.CLASS_NAME, "MainSection-sc-k5m04n-2")
                      .find_element(By.CLASS_NAME, "Title-sc-k5m04n-6")
                      .text)
        print(self.title)
    
    def _get_description(self):
        self.description = (self.scheme
                            .find_element(By.CLASS_NAME, "MainSection-sc-k5m04n-2")
                            .find_element(By.CLASS_NAME, "Description-sc-k5m04n-7")
                            .text)
    
    def _get_tags(self):
        tags = (self.scheme
                .find_element(By.CLASS_NAME, "TagsContainer-sc-k5m04n-9")
                .find_elements(By.TAG_NAME, "span"))
        for tag in tags:
            self.tags_list.append(tag.text)
        print(self.tags_list)
        #self.tags = " ".join(self.tags_list)
        
    def _get_link(self):
        self.link = self.scheme.get_attribute("href")
    
    def _enter_item_link(self):
        # Switch to the new tab
        self.webdriver.execute_script("window.open('');")
        self.webdriver.switch_to.window(self.webdriver.window_handles[-1])
        self.webdriver.get(self.link)
        time.sleep(1)
        
        
    def _get_category(self):
        time.sleep(1)
        categories = self.webdriver.find_element(By.CLASS_NAME, "category-wrapper").find_elements(By.TAG_NAME, "a")
        for cat in categories:
            self.category_list.append(cat.text)
        
    def _get_highlights(self):
        highlights = (self.webdriver
                      .find_element(By.CLASS_NAME, "SchemeHighlightsWrapper-sc-1el0czi-2")
                      .find_elements(By.TAG_NAME, "li"))
        for highlight in highlights:
            self.highlight_list.append(highlight.text)
        
        self.highlight = " ".join(self.highlight_list)
    
    def _get_accordian_items(self):
        # Expand all accordian so we can extract the text
        (self.webdriver
         .find_element(By.XPATH, "//button[contains(@class, 'StyledTextButton') and span[text()='Expand all sections']]")
         .click()
        )
        
        self.accordian_items = self.webdriver.find_elements(By.CSS_SELECTOR, '[data-accordion-component="AccordionItemPanel"]')
        
            
    def _get_benefits_info(self):
        
        benefit_items = (self.accordian_items[0]
                         .find_elements(By.TAG_NAME, "p"))
        for item in benefit_items:
            self.benefit_list.append(item.text)

        self.benefit = " ".join(self.benefit_list)
            
    def _get_eligibility_info(self):

        eligible_items = (self.accordian_items[1]
                          .find_elements(By.TAG_NAME, "p"))
        for item in eligible_items:
            self.eligible_list.append(item.text)
        
        self.eligible = " ".join(self.eligible_list)
        
    def _get_apply_info(self):
        
        apply_items = (self.accordian_items[2]
                       .find_elements(By.TAG_NAME, "p"))
        for item in apply_items:
            self.apply_list.append(item.text)

        self.apply = " ".join(self.apply_list)
        
    def extract_items(self):
        self._get_title()
        self._get_description()
        self._get_tags()
        
        self._get_link()
        self._enter_item_link()
        
        self._get_category()
        self._get_accordian_items()
        self._get_highlights()
        self._get_benefits_info()
        self._get_eligibility_info()
        self._get_apply_info()
        
        self.webdriver.close()
        self.webdriver.switch_to.window(self.webdriver.window_handles[-1])
    
        
    
        
    
    
    
    
    
    
# def main():
#     driver = webdriver.Chrome()
#     driver.get(url)
#     list_of_schemes = webdriver.find_elements(By.CLASS_NAME, "GrantCardWrapper-sc-bqo4pt-0")[0].find_elements(By.TAG_NAME, "a")
    
#     for scheme in list_of_schemes:
        