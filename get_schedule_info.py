import xml.etree.ElementTree as ET
import os
import csv
from datetime import datetime

def get_schedule_info(xml_file):
    """
    Extract schedule information from XML file
    
    Args:
        xml_file (str): Path to the schedule XML file
    
    Returns:
        dict: Dictionary containing schedule information
    """
    try:
        # Parse XML file
        print(f"Debug: Starting to parse {xml_file}")
        tree = ET.parse(xml_file)
        root = tree.getroot()
        print(f"Debug: XML Root tag: {root.tag}")
        
        # Define namespaces - note the ns0 namespace from your XML
        namespaces = {
            'ns0': 'http://www.blueprism.co.uk/product/schedule'
        }
        
        # Dictionary to store schedule info
        schedule_info = {
            'file_name': os.path.basename(xml_file),
            'id': '',
            'name': '',
            'trigger_info': {}
        }
        
        # Get id and name from root element
        schedule_info['id'] = root.get('id', '')
        schedule_info['name'] = root.get('name', '')
        
        # Find the user trigger
        user_trigger = root.find('.//ns0:trigger[@user-trigger="true"]', namespaces)
        if user_trigger is not None:
            schedule_info['trigger_info'] = {
                'priority': user_trigger.get('priority', ''),
                'unit_type': user_trigger.get('unit-type', ''),
                'start_date': user_trigger.get('start-date', ''),
                'end_date': user_trigger.get('end-date', ''),
                'start_point': user_trigger.get('start-point', ''),
                'end_point': user_trigger.get('end-point', ''),
                'period': user_trigger.get('period', ''),
                'calendar': user_trigger.get('calendar', '')
            }
        
        return schedule_info
    
    except ET.ParseError as e:
        print(f"Error parsing XML file {xml_file}: {e}")
        return None
    except Exception as e:
        print(f"Error processing schedule information for {xml_file}: {e}")
        return None

def print_schedule_info(schedule_info):
    """
    Print schedule information in a formatted way
    
    Args:
        schedule_info (dict): Dictionary containing schedule information
    """
    if not schedule_info:
        print("No schedule information available")
        return
    
    print("\n=== Schedule Information ===")
    print(f"ID: {schedule_info['id']}")
    print(f"Name: {schedule_info['name']}")
    
    if schedule_info['trigger_info']:
        print("\n--- Trigger Information ---")
        trigger = schedule_info['trigger_info']
        print(f"Start Date: {trigger['start_date']}")
        print(f"Priority: {trigger['priority']}")
        print(f"Unit Type: {trigger['unit_type']}")
        print(f"End Point: {trigger['end_point']}")
        print(f"Calendar: {trigger['calendar']}")

def process_schedule_folder(folder_path, output_csv):
    """
    Process all XML files in the specified folder and save to CSV
    
    Args:
        folder_path (str): Path to folder containing XML files
        output_csv (str): Path to output CSV file
    """
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' not found")
        return
    
    # List to store all schedule information
    all_schedules = []
    total_files = len([f for f in os.listdir(folder_path) if f.endswith('.xml')])
    processed_files = 0
    
    # Process each XML file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            xml_path = os.path.join(folder_path, filename)
            processed_files += 1
            print(f"Processing: {filename} ({processed_files}/{total_files})")
            
            schedule_info = get_schedule_info(xml_path)
            if schedule_info:
                all_schedules.append(schedule_info)
    
    # Write to CSV if we have any data
    if all_schedules:
        try:
            with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV headers
                fieldnames = [
                    'file_name', 
                    'id', 
                    'name', 
                    'trigger_start_date',
                    'trigger_end_date',
                    'trigger_priority', 
                    'trigger_unit_type',
                    'trigger_start_point',
                    'trigger_end_point',
                    'trigger_period',
                    'trigger_calendar'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write each schedule to CSV
                for schedule in all_schedules:
                    row = {
                        'file_name': schedule['file_name'],
                        'id': schedule['id'],
                        'name': schedule['name'],
                        'trigger_start_date': schedule['trigger_info'].get('start_date', ''),
                        'trigger_end_date': schedule['trigger_info'].get('end_date', ''),
                        'trigger_priority': schedule['trigger_info'].get('priority', ''),
                        'trigger_unit_type': schedule['trigger_info'].get('unit_type', ''),
                        'trigger_start_point': schedule['trigger_info'].get('start_point', ''),
                        'trigger_end_point': schedule['trigger_info'].get('end_point', ''),
                        'trigger_period': schedule['trigger_info'].get('period', ''),
                        'trigger_calendar': schedule['trigger_info'].get('calendar', '')
                    }
                    writer.writerow(row)
                
            print(f"\nSuccessfully created CSV file: {output_csv}")
            print(f"Processed {len(all_schedules)} schedule files")
            
        except Exception as e:
            print(f"Error writing to CSV file: {e}")
    else:
        print("No schedule information found to write to CSV")

def main():
    # Base path
    base_path = r"C:\Users\Admin\Desktop\My first Brick\Lowcode_to_code"
    
    # Define paths
    schedule_folder = os.path.join(base_path, "element_files", "schedule")
    summary_folder = os.path.join(base_path, "summary")
    
    # Set output CSV file path in the summary folder
    output_csv = os.path.join(summary_folder, "schedule_summary.csv")
    
    # Create summary folder if it doesn't exist
    if not os.path.exists(summary_folder):
        os.makedirs(summary_folder)
        print(f"Created summary folder: {summary_folder}")
    
    # Process all files
    process_schedule_folder(schedule_folder, output_csv)

if __name__ == "__main__":
    main()
