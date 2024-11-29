from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options  # Import Options class
import time

def setup_driver():
    # Set up the Edge WebDriver
    options = Options()
    options.add_argument("--start-maximized")
    driver_path = r"C:\webdrivers\msedgedriver.exe"  # Replace with the actual path to msedgedriver.exe
    service = Service(driver_path)
    driver = webdriver.Edge(service=service, options=options)
    return driver

def navigate_to_page(driver, url):
    driver.get(url)
    print(f"Opened page: {url}")
    time.sleep(2)  

def detect_form_elements(driver):
    # Wait until the page is fully loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "form")))
    
    form_data = []
    forms = driver.find_elements(By.TAG_NAME, "form")  # Find all forms on the page
    
    for form in forms:
        print("Form detected:")
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
                form_fields["text_inputs"].append({"type": input_type, "name": field_name})
            elif input_type == "checkbox":
                form_fields["checkboxes"].append({"type": input_type, "name": field_name})
            elif input_type == "file":
                form_fields["file_inputs"].append({"type": input_type, "name": field_name})
        
        # Find dropdowns
        selects = form.find_elements(By.TAG_NAME, "select")
        for select in selects:
            field_name = select.get_attribute("name") or select.get_attribute("id")
            form_fields["dropdowns"].append({"type": "select", "name": field_name})
        
        form_data.append(form_fields)
    
    return form_data

# Function to display detected elements
def print_form_elements(form_data):
    for index, form in enumerate(form_data):
        print(f"\n--- Form {index + 1} ---")
        for key, elements in form.items():
            print(f"{key.capitalize()}:")
            for element in elements:
                print(f"  - {element['name']} ({element['type']})")

if __name__ == "__main__":
    # Step 1: Set up and navigate
    driver = setup_driver()
    target_url = "https://www.instagram.com/"  # Replace with the target website
    navigate_to_page(driver, target_url)
    
    # Step 2: Detect form elements
    form_data = detect_form_elements(driver)
    print_form_elements(form_data)
    
    # Close the driver
    driver.quit()
