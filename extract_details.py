import xml.etree.ElementTree as ET
import re
import os
import glob

def extract_process_details(xml_file):
    """
    Extracts enhanced information from a Blue Prism process XML file
    """
    with open(xml_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Decode XML entities
    content = content.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    
    # Extract subsheetid values
    subsheet_pattern = r'<stage[^>]*subsheetid="([^"]+)"'
    subsheet_ids = set(re.findall(subsheet_pattern, content))
    
    # Enhanced stage pattern to capture more details
    stage_pattern = r'<stage\s+stageid="([^"]+)"\s+name="([^"]+)"\s+type="([^"]+)"[^>]*>(.*?)</stage>'
    stages = []
    
    for match in re.finditer(stage_pattern, content, re.DOTALL):
        stage_id = match.group(1)
        name = match.group(2)
        stage_type = match.group(3)
        stage_content = match.group(4)
        
        # Base stage info
        stage_info = {
            'stageid': stage_id,
            'name': name,
            'type': stage_type,
            'onsuccess': None
        }
        
        # Extract onsuccess
        onsuccess_match = re.search(r'<onsuccess>([^<]+)</onsuccess>', stage_content)
        if onsuccess_match:
            stage_info['onsuccess'] = onsuccess_match.group(1)
        
        # Extract type-specific information
        if stage_type == "Decision":
            expr_match = re.search(r'<decision expression="([^"]+)"', stage_content)
            ontrue_match = re.search(r'<ontrue>([^<]+)</ontrue>', stage_content)
            onfalse_match = re.search(r'<onfalse>([^<]+)</onfalse>', stage_content)
            
            stage_info.update({
                'expression': expr_match.group(1) if expr_match else None,
                'ontrue': ontrue_match.group(1) if ontrue_match else None,
                'onfalse': onfalse_match.group(1) if onfalse_match else None
            })
        
        elif stage_type == "Calculation":
            calc_match = re.search(r'<calculation expression="([^"]+)"\s+stage="([^"]+)"', stage_content)
            if calc_match:
                stage_info.update({
                    'expression': calc_match.group(1),
                    'calculation_stage': calc_match.group(2)
                })
        
        elif stage_type == "Exception":
            # Extract all exception attributes using a more comprehensive pattern
            exc_pattern = r'<exception\s+(?:localized="([^"]+)")?\s*(?:type="([^"]+)")?\s*(?:detail="([^"]+)")?\s*(?:usecurrent="([^"]+)")?\s*/?>'
            exc_match = re.search(exc_pattern, stage_content, re.DOTALL)
            
            if exc_match:
                stage_info.update({
                    'localized': exc_match.group(1) if exc_match.group(1) else '',
                    'exception_type': exc_match.group(2) if exc_match.group(2) else '',
                    'exception_detail': exc_match.group(3) if exc_match.group(3) else '',
                    'usecurrent': exc_match.group(4) if exc_match.group(4) else ''
                })
        elif stage_type == "MultipleCalculation":
            calculations = []
            steps_match = re.search(r'<steps>(.*?)</steps>', stage_content, re.DOTALL)
            if steps_match:
                steps_content = steps_match.group(1)
                for calc_match in re.finditer(r'<calculation expression="([^"]+)"\s+stage="([^"]+)"', steps_content):
                    calculations.append({
                        'expression': calc_match.group(1),
                        'stage': calc_match.group(2)
                    })
            stage_info['calculations'] = calculations
        
        stages.append(stage_info)
    
    return {
        'subsheet_ids': list(subsheet_ids),
        'stages': stages
    }

def export_to_csv(results, output_file, folder_outputs):
    """
    Exports the enhanced results to CSV files
    """
    import csv
    
    # Create subdirectories
    subsheets_dir = os.path.join(folder_outputs, 'subsheets')
    stages_dir = os.path.join(folder_outputs, 'stages')
    os.makedirs(subsheets_dir, exist_ok=True)
    os.makedirs(stages_dir, exist_ok=True)
    
    # Export subsheet IDs (unchanged)
    with open(os.path.join(subsheets_dir, f"{output_file}_subsheets.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'SubsheetID'])
        for idx, subsheet_id in enumerate(results['subsheet_ids'], 1):
            writer.writerow([idx, subsheet_id])
    
    # Export enhanced stages information
    with open(os.path.join(stages_dir, f"{output_file}_stages.csv"), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Enhanced headers
        headers = ['Index', 'StageID', 'Name', 'Type', 'OnSuccess', 
                  'Expression', 'OnTrue', 'OnFalse',  # For Decision
                  'Calculation_Stage',  # For Calculation
                  'Exception_Type', 'Exception_Detail', 'Localized', 'UseCurrent',  # For Exception
                  'Multiple_Calculations']  # For MultipleCalculation
        
        writer.writerow(headers)
        
        for idx, stage in enumerate(results['stages'], 1):
            row = [
                idx,
                stage['stageid'],
                stage['name'],
                stage['type'],
                stage['onsuccess'] or '',
                stage.get('expression', ''),
                stage.get('ontrue', ''),
                stage.get('onfalse', ''),
                stage.get('calculation_stage', ''),
                stage.get('exception_type', ''),
                stage.get('exception_detail', ''),
                stage.get('localized', ''),
                stage.get('usecurrent', ''),
                str(stage.get('calculations', '')) if stage.get('calculations') else ''
            ]
            writer.writerow(row)

def find_xml_file(file_name, directory='.', folder_inputs='process_files'):
    """
    Find the XML file in the specified directory or subdirectories
    
    Args:
        file_name (str): Name of the file to find
        directory (str): Directory to start the search
        
    Returns:
        str: Path to the XML file if found, None otherwise
    """
    
    # Check if file exists in process_files directory
    process_dir = os.path.join(directory, folder_inputs)
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
    folder_inputs = 'process_files'
    folder_outputs = 'extract_information'
    
    # Try to find the file
    file_path = find_xml_file(target_file, folder_inputs)
    
    if not file_path:
        # If file not found, list available XML files
        print(f"Error: Could not find '{target_file}'")
        print("Available XML files in process_files directory:")
        
        if os.path.exists(folder_inputs):
            xml_files = glob.glob(os.path.join(folder_inputs, '*.xml'))
            if xml_files:
                total_files = len(xml_files)
                for file_path in xml_files:
                    print(f"\nProcessing: {file_path}")
                    # Extract and process the information
                    try:
                        results = extract_process_details(file_path)
                        
                        # Export to CSV files
                        output_prefix = os.path.splitext(os.path.basename(file_path))[0] + "_details"
                        export_to_csv(results, output_prefix, folder_outputs)
                        
                        print(f"\nResults exported to {output_prefix}_subsheets.csv and {output_prefix}_stages.csv")
                    except Exception as e:
                        print(f"Error processing file: {str(e)}")
                
                print(f"\nCompleted processing {len(xml_files)} files.")
                exit()
            else:
                print("  No XML files found in process_files directory.")
                exit()
        else:
            print(f"  '{folder_inputs}' directory does not exist.")
            exit()
