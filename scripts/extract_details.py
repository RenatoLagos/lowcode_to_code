import xml.etree.ElementTree as ET
import re
import os
import glob

def extract_process_details(xml_file):
    """
    Extracts information from a Blue Prism process XML file:
    - subsheetid list
    - stageid list with onsuccess value, name, and type
    
    Args:
        xml_file (str): Path to the XML process file
    
    Returns:
        dict: Dictionary containing extracted information
    """
    # Read the XML file
    with open(xml_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The XML may have encoded entities, decode them
    content = content.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    
    # Extract subsheetid values using regex
    subsheet_pattern = r'<stage[^>]*subsheetid="([^"]+)"'
    subsheet_ids = set(re.findall(subsheet_pattern, content))
    
    # Extract stage information using regex
    stage_pattern = r'<stage\s+stageid="([^"]+)"\s+name="([^"]+)"\s+type="([^"]+)"[^>]*(?:onsuccess="([^"]+)")?[^>]*>'
    stages = []
    
    for match in re.finditer(stage_pattern, content):
        stage_id = match.group(1)
        name = match.group(2)
        stage_type = match.group(3)
        onsuccess = match.group(4) if match.group(4) else None
        
        stages.append({
            'stageid': stage_id,
            'name': name,
            'type': stage_type,
            'onsuccess': onsuccess
        })
    
    # Compile results
    results = {
        'subsheet_ids': list(subsheet_ids),
        'stages': stages
    }
    
    return results

def print_results(results):
    """
    Prints the extracted information in a readable format
    
    Args:
        results (dict): Results from extract_process_details
    """
    print("SUBSHEET IDs:")
    print("=============")
    for idx, subsheet_id in enumerate(results['subsheet_ids'], 1):
        print(f"{idx}. {subsheet_id}")
    
    print("\nSTAGES:")
    print("=======")
    for idx, stage in enumerate(results['stages'], 1):
        print(f"{idx}. Stage ID: {stage['stageid']}")
        print(f"   Name: {stage['name']}")
        print(f"   Type: {stage['type']}")
        if stage['onsuccess']:
            print(f"   OnSuccess: {stage['onsuccess']}")
        print()

def export_to_csv(results, output_file):
    """
    Exports the results to a CSV file
    
    Args:
        results (dict): Results from extract_process_details
        output_file (str): Path to save the CSV file
    """
    import csv
    
    # Export subsheet IDs
    with open(f"{output_file}_subsheets.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'SubsheetID'])
        for idx, subsheet_id in enumerate(results['subsheet_ids'], 1):
            writer.writerow([idx, subsheet_id])
    
    # Export stages
    with open(f"{output_file}_stages.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'StageID', 'Name', 'Type', 'OnSuccess'])
        for idx, stage in enumerate(results['stages'], 1):
            writer.writerow([
                idx,
                stage['stageid'],
                stage['name'],
                stage['type'],
                stage['onsuccess'] if stage['onsuccess'] else ''
            ])

def find_xml_file(file_name, directory='.'):
    """
    Find the XML file in the specified directory or subdirectories
    
    Args:
        file_name (str): Name of the file to find
        directory (str): Directory to start the search
        
    Returns:
        str: Path to the XML file if found, None otherwise
    """
    # Check if file exists in current directory
    if os.path.exists(file_name):
        return file_name
    
    # Check if file exists in process_files directory
    process_dir = os.path.join(directory, 'process_files')
    if os.path.exists(process_dir):
        file_path = os.path.join(process_dir, file_name)
        if os.path.exists(file_path):
            return file_path
    
    # Search for the file in process_files directory
    if os.path.exists(process_dir):
        for file in os.listdir(process_dir):
            if file == file_name or file.endswith('.xml'):
                return os.path.join(process_dir, file)
    
    return None

if __name__ == "__main__":
    # Define the target file name
    target_file = "process_531accd6-be30-4087-a44e-d7edd3571402.xml"
    
    # Try to find the file
    file_path = find_xml_file(target_file)
    
    if not file_path:
        # If file not found, list available XML files
        print(f"Error: Could not find '{target_file}'")
        print("Available XML files in process_files directory:")
        
        process_dir = 'process_files'
        if os.path.exists(process_dir):
            xml_files = glob.glob(os.path.join(process_dir, '*.xml'))
            if xml_files:
                for idx, xml_file in enumerate(xml_files, 1):
                    print(f"  {idx}. {os.path.basename(xml_file)}")
                
                # Allow user to select a file
                choice = input("\nEnter the number of the file to process (or press Enter to exit): ")
                if choice and choice.isdigit() and 1 <= int(choice) <= len(xml_files):
                    file_path = xml_files[int(choice) - 1]
                else:
                    print("Exiting.")
                    exit()
            else:
                print("  No XML files found in process_files directory.")
                exit()
        else:
            print(f"  '{process_dir}' directory does not exist.")
            exit()
    
    output_prefix = os.path.splitext(os.path.basename(file_path))[0] + "_details"
    
    print(f"Processing file: {file_path}")
    
    # Extract and process the information
    try:
        results = extract_process_details(file_path)
        
        # Print results to console
        print_results(results)
        
        # Export to CSV files
        export_to_csv(results, output_prefix)
        
        print(f"\nResults exported to {output_prefix}_subsheets.csv and {output_prefix}_stages.csv")
    except Exception as e:
        print(f"Error processing file: {str(e)}")
