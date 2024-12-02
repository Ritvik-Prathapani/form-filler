import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time
import json

class FormAutoFiller:
    def __init__(self):
        self.driver = self.setup_driver()
        self.saved_form_data = {}
        self.config_file = 'form_data_config.json'
        self.load_saved_data()

    def setup_driver(self):
        options = Options()
        options.add_argument("--start-maximized")
        driver_path = r"C:\webdrivers\msedgedriver.exe"
        service = Service(driver_path)
        driver = webdriver.Edge(service=service, options=options)
        return driver

    def navigate_to_page(self, url):
        self.driver.get(url)
        print(f"Opened page: {url}")
        time.sleep(2)

    def detect_form_elements(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        
        form_data = []
        forms = self.driver.find_elements(By.TAG_NAME, "form")
        
        for form in forms:
            form_fields = {
                "text_inputs": [],
                "dropdowns": [],
                "checkboxes": [],
                "file_inputs": []
            }
            
            # Find input fields
            inputs = form.find_elements(By.TAG_NAME, "input")
            for input_field in inputs:
                input_type = input_field.get_attribute("type")
                field_name = input_field.get_attribute("name") or input_field.get_attribute("id")
                
                if input_type in ["text", "email", "password", "tel", "number"]:
                    form_fields["text_inputs"].append({
                        "type": input_type, 
                        "name": field_name,
                        "element": input_field
                    })
                elif input_type == "checkbox":
                    form_fields["checkboxes"].append({
                        "type": input_type, 
                        "name": field_name,
                        "element": input_field
                    })
                elif input_type == "file":
                    form_fields["file_inputs"].append({
                        "type": input_type, 
                        "name": field_name,
                        "element": input_field
                    })
            
            # Find dropdowns
            selects = form.find_elements(By.TAG_NAME, "select")
            for select in selects:
                field_name = select.get_attribute("name") or select.get_attribute("id")
                form_fields["dropdowns"].append({
                    "type": "select", 
                    "name": field_name,
                    "element": select
                })
            
            form_data.append(form_fields)
        
        return form_data

    def prompt_for_missing_values(self, form_data):
        """Prompt user to input values for form fields"""
        for form_index, form in enumerate(form_data):
            print(f"\n--- Form {form_index + 1} Configuration ---")
            
            # Prompt for text inputs
            for input_field in form["text_inputs"]:
                if input_field['name'] not in self.saved_form_data:
                    value = input(f"Enter value for {input_field['name']} ({input_field['type']} input): ")
                    self.saved_form_data[input_field['name']] = value
            
            # Prompt for file inputs
            for file_input in form["file_inputs"]:
                if file_input['name'] not in self.saved_form_data:
                    file_path = input(f"Enter file path for {file_input['name']} (file input): ")
                    self.saved_form_data[file_input['name']] = file_path
            
            # Prompt for checkboxes
            for checkbox in form["checkboxes"]:
                if checkbox['name'] not in self.saved_form_data:
                    check = input(f"Check {checkbox['name']} checkbox? (y/n): ").lower() == 'y'
                    self.saved_form_data[checkbox['name']] = check
            
            # Prompt for dropdowns
            for dropdown in form["dropdowns"]:
                if dropdown['name'] not in self.saved_form_data:
                    value = input(f"Select value for {dropdown['name']} dropdown: ")
                    self.saved_form_data[dropdown['name']] = value
        
        # Save the configuration
        self.save_form_data()

    def fill_form_fields(self, form_data):
        """Fill form fields with saved or user-provided values"""
        for form_index, form in enumerate(form_data):
            print(f"\n--- Filling Form {form_index + 1} ---")
            
            # Fill text inputs
            for input_field in form["text_inputs"]:
                name = input_field['name']
                if name in self.saved_form_data:
                    input_field['element'].clear()
                    input_field['element'].send_keys(self.saved_form_data[name])
            
            # Fill file inputs
            for file_input in form["file_inputs"]:
                name = file_input['name']
                if name in self.saved_form_data:
                    file_path = self.saved_form_data[name]
                    if os.path.exists(file_path):
                        file_input['element'].send_keys(file_path)
                    else:
                        print(f"File not found: {file_path}")
            
            # Handle checkboxes
            for checkbox in form["checkboxes"]:
                name = checkbox['name']
                if name in self.saved_form_data:
                    if self.saved_form_data[name]:
                        if not checkbox['element'].is_selected():
                            checkbox['element'].click()
                    else:
                        if checkbox['element'].is_selected():
                            checkbox['element'].click()
            
            # Handle dropdowns
            for dropdown in form["dropdowns"]:
                name = dropdown['name']
                if name in self.saved_form_data:
                    select = Select(dropdown['element'])
                    try:
                        select.select_by_visible_text(self.saved_form_data[name])
                    except:
                        try:
                            select.select_by_value(self.saved_form_data[name])
                        except:
                            print(f"Could not select value for dropdown: {name}")

    def save_form_data(self):
        """Save form data to a JSON configuration file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.saved_form_data, f)

    def load_saved_data(self):
        """Load saved form data from JSON configuration file"""
        try:
            with open(self.config_file, 'r') as f:
                self.saved_form_data = json.load(f)
        except FileNotFoundError:
            self.saved_form_data = {}

    def auto_fill_form(self, url):
        """Main method to navigate, detect, and fill forms"""
        # Navigate to the page
        self.navigate_to_page(url)
        
        # Detect form elements
        form_data = self.detect_form_elements()
        
        # Prompt for missing values if needed
        if not self.saved_form_data:
            self.prompt_for_missing_values(form_data)
        
        # Fill form fields
        self.fill_form_fields(form_data)

    def close(self):
        """Close the browser"""
        self.driver.quit()

def main():
    # Create form auto filler instance
    form_filler = FormAutoFiller()
    
    try:
        # Replace with the target website
        target_url = "https://www.instagram.com/"
        
        # Automatically fill the form
        form_filler.auto_fill_form(target_url)
        
        # Optional: Keep browser open for verification
        input("Press Enter to close the browser...")
    
    finally:
        # Always close the browser
        form_filler.close()

if __name__ == "__main__":
    main()