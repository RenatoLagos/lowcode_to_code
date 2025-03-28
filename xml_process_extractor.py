import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

def remove_xml_headers(input_file, temp_output_file):
    """
    Removes the specified XML header and footer from an XML file
    while preserving the content between them and removing indentation.
    
    Args:
        input_file (str): Path to the input XML file
        temp_output_file (str): Path to the temporary output file
    """
    # Lines to skip (start markers)
    skip_start_markers = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<bpr:release xmlns:bpr="http://www.blueprism.co.uk/product/release">',
        '<bpr:name>Processes</bpr:name>',
        '<bpr:release-notes />',
        '<bpr:created>',  # Partial match for date line
        '<bpr:package-id>',
        '<bpr:package-name>',
        '<bpr:user-created-by>',
        '<bpr:contents count='
    ]
    
    # Lines to skip (end markers)
    skip_end_markers = [
        '</bpr:contents>',
        '</bpr:release>'
    ]
    
    # Read the input file line by line
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Process the content
    content_started = False
    content_ended = False
    output_lines = []
    
    for line in lines:
        # Skip lines with start markers if content hasn't started yet
        if not content_started:
            should_skip = False
            for marker in skip_start_markers:
                if marker in line:
                    should_skip = True
                    break
            
            if not should_skip:
                content_started = True
                # Remove leading whitespace and add to output
                output_lines.append(line.lstrip())
        # Skip lines with end markers and everything after
        elif not content_ended:
            should_skip = False
            for marker in skip_end_markers:
                if marker in line:
                    content_ended = True
                    should_skip = True
                    break
            
            if not should_skip:
                # Remove leading whitespace and add to output
                output_lines.append(line.lstrip())
    
    # Write the processed content to the output file
    with open(temp_output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"Headers removed. Temporary file saved to {temp_output_file}")

def prettify_xml(elem):
    """
    Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def split_by_process(input_file, output_dir="process_files"):
    """
    Splits an XML file containing multiple process elements into separate XML files,
    one for each process. Names files based on process IDs.
    
    Args:
        input_file (str): Path to the input XML file
        output_dir (str): Directory where output files will be saved
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read the input XML file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {input_file}: {e}")
        return
    
    # Set up XML namespace for parsing
    namespaces = {'bp': 'http://www.blueprism.co.uk/product/process'}
    
    # Find all process elements
    # First, wrap the content in a root element to make it valid XML if needed
    if not content.strip().startswith('<'):
        content = f"<root>{content}</root>"
    
    try:
        # Try to parse directly - this assumes content is already well-formed XML
        root = ET.fromstring(content)
        processes = root.findall('.//process')
        
        # If no processes found with default namespace, try with explicit namespace
        if not processes:
            processes = root.findall('.//bp:process', namespaces)
    except ET.ParseError:
        # If parsing fails, try to extract process elements using regex
        print("XML parsing failed. Attempting to extract processes using regex...")
        pattern = r'<(?:bp:)?process[^>]*id="([^"]+)".*?</(?:bp:)?process>'
        process_matches = re.finditer(pattern, content, re.DOTALL)
        
        files_created = 0
        for match in process_matches:
            process_content = match.group(0)
            process_id = match.group(1)
            
            # Clean up process_id to use as filename
            filename = f"process_{process_id.replace(' ', '_').replace('/', '_')}.xml"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                # Add XML declaration
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write(process_content)
            
            files_created += 1
            print(f"Created: {filepath}")
        
        print(f"Total process files created: {files_created}")
        return
    
    files_created = 0
    # Process each process element
    for process in processes:
        # Get process ID or name
        process_id = None
        if 'id' in process.attrib:
            process_id = process.attrib['id']
        elif 'name' in process.attrib:
            process_id = process.attrib['name']
        else:
            # Try to find id or name in child elements
            id_elem = process.find('.//id') or process.find('.//bp:id', namespaces)
            name_elem = process.find('.//name') or process.find('.//bp:name', namespaces)
            
            if id_elem is not None and id_elem.text:
                process_id = id_elem.text
            elif name_elem is not None and name_elem.text:
                process_id = name_elem.text
            else:
                process_id = f"unknown_process_{files_created}"
        
        # Clean up process_id to use as filename
        filename = f"process_{process_id.replace(' ', '_').replace('/', '_')}.xml"
        filepath = os.path.join(output_dir, filename)
        
        # Create new XML document with the process
        process_xml = prettify_xml(process)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(process_xml)
        
        files_created += 1
        print(f"Created: {filepath}")
    
    print(f"Total process files created: {files_created}")

def process_xml_file(input_file, output_dir="process_files", temp_file="temp_output.xml"):
    """
    Main function that processes the XML file:
    1. Removes headers and footers
    2. Splits by process ID
    3. Creates individual XML files
    
    Args:
        input_file (str): Path to the input XML file
        output_dir (str): Directory where output files will be saved
        temp_file (str): Path for temporary file
    """
    print(f"Processing file: {input_file}")
    
    # Step 1: Remove headers
    remove_xml_headers(input_file, temp_file)
    
    # Step 2: Split by process
    split_by_process(temp_file, output_dir)
    
    # Optional: Clean up temporary file
    try:
        os.remove(temp_file)
        print(f"Temporary file {temp_file} removed.")
    except Exception as e:
        print(f"Note: Could not remove temporary file: {e}")
    
    print(f"Processing complete. Individual process files are in the '{output_dir}' directory.")

if __name__ == "__main__":
    # Get input file from user or use default
    input_file = input("Enter path to the XML file (or press Enter to use default 'Process.xml'): ")
    if not input_file:
        input_file = "Process.xml"
    
    # Get output directory from user or use default
    output_dir = input("Enter output directory name (or press Enter to use default 'process_files'): ")
    if not output_dir:
        output_dir = "process_files"
    
    # Process the file
    process_xml_file(input_file, output_dir) 