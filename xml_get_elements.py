import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify_xml(elem):
    """
    Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    re_parsed = minidom.parseString(rough_string)
    return re_parsed.toprettyxml(indent="  ")

def split_by_element(input_file):
    """
    Splits XML elements inside <bpr:contents> into separate files,
    organizing them by element type in different folders.
    """
    try:
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        # Define namespaces
        namespaces = {
            'bpr': 'http://www.blueprism.co.uk/product/release',
            'bp': 'http://www.blueprism.co.uk/product/process',
            'bpm': 'http://www.bp.com/bpm'
        }
        
        # Register namespaces
        for prefix, uri in namespaces.items():
            ET.register_namespace(prefix, uri)
        
        # Find contents element
        contents = root.find('.//bpr:contents', namespaces)
        if contents is None:
            print("Element <bpr:contents> not found")
            return
        
        files_created = 0
        # Process each element inside contents
        for element in contents:
            # Get element type (without namespace)
            element_type = element.tag.split('}')[-1]
            
            # Get element ID
            element_id = None
            if 'id' in element.attrib:
                element_id = element.attrib['id']
            elif 'name' in element.attrib:
                element_id = element.attrib['name']
            else:
                # Look for id or name in child elements
                for ns in namespaces.keys():
                    id_elem = element.find(f'.//{ns}:id', namespaces)
                    name_elem = element.find(f'.//{ns}:name', namespaces)
                    if id_elem is not None and id_elem.text:
                        element_id = id_elem.text
                        break
                    elif name_elem is not None and name_elem.text:
                        element_id = name_elem.text
                        break
                
                if element_id is None:
                    element_id = f"unknown_{files_created}"
            
            # Create directory for this element type
            type_dir = os.path.join("element_files", element_type)
            if not os.path.exists(type_dir):
                os.makedirs(type_dir)
            
            # Clean up ID to use as filename
            filename = f"{element_id.replace(' ', '_').replace('/', '_')}.xml"
            filepath = os.path.join(type_dir, filename)
            
            # Add XML declaration and namespace to individual element
            element_str = ET.tostring(element, encoding='unicode')
            full_xml = f'<?xml version="1.0" encoding="utf-8"?>\n{element_str}'
            
            # Save element to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_xml)
            
            files_created += 1
            print(f"Created: {filepath}")
        
        print(f"Total files created: {files_created}")
            
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        print("Please check if the XML file is properly formatted")
        return
    finally:
        # Clean up temporary files
        temp_files = ["temp_parse.xml", "temp_output.xml"]
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"Temporary file {temp_file} removed.")
            except Exception as e:
                print(f"Could not remove temporary file {temp_file}: {e}")

if __name__ == "__main__":
    # Get input file from user or use default
    input_file = input("Enter path to the XML file (or press Enter to use default 'xml.xml'): ")
    if not input_file:
        input_file = "xml.xml"
    
    # Process the file
    split_by_element(input_file) 