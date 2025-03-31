import xml.etree.ElementTree as ET
import os
import csv

def get_calendar_info(xml_file):
    """
    Extract calendar information from XML file
    
    Args:
        xml_file (str): Path to the calendar XML file
    
    Returns:
        dict: Dictionary containing calendar information
    """
    try:
        # Parse XML file
        print(f"Debug: Starting to parse {xml_file}")
        tree = ET.parse(xml_file)
        root = tree.getroot()
        print(f"Debug: XML Root tag: {root.tag}")
        
        # Define namespaces
        namespaces = {
            'ns0': 'http://www.blueprism.co.uk/product/calendar'
        }
        
        # Dictionary to store calendar info
        calendar_info = {
            'file_name': os.path.basename(xml_file),
            'id': '',
            'name': '',
            'working_week': ''
        }
        
        # Get id and name from root element
        calendar_info['id'] = root.get('id', '')
        calendar_info['name'] = root.get('name', '')
        
        # Get schedule-calendar information
        schedule_calendar = root.find('.//ns0:schedule-calendar', namespaces)
        if schedule_calendar is not None:
            calendar_info['working_week'] = schedule_calendar.get('working-week', '')
        
        return calendar_info
    
    except ET.ParseError as e:
        print(f"Error parsing XML file {xml_file}: {e}")
        return None
    except Exception as e:
        print(f"Error processing calendar information for {xml_file}: {e}")
        return None

def process_calendar_folder(folder_path, output_csv):
    """
    Process all XML files in the specified folder and save to CSV
    """
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' not found")
        return
    
    # List to store all calendar information
    all_calendars = []
    total_files = len([f for f in os.listdir(folder_path) if f.endswith('.xml')])
    processed_files = 0
    
    # Process each XML file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            xml_path = os.path.join(folder_path, filename)
            processed_files += 1
            print(f"Processing: {filename} ({processed_files}/{total_files})")
            
            calendar_info = get_calendar_info(xml_path)
            if calendar_info:
                all_calendars.append(calendar_info)
    
    # Write to CSV if we have any data
    if all_calendars:
        try:
            with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'file_name',
                    'id',
                    'name',
                    'working_week'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for calendar in all_calendars:
                    writer.writerow(calendar)
                
            print(f"\nSuccessfully created CSV file: {output_csv}")
            print(f"Processed {len(all_calendars)} calendar files")
            
        except Exception as e:
            print(f"Error writing to CSV file: {e}")
    else:
        print("No calendar information found to write to CSV")

def main():
    # Base path
    base_path = r"C:\Users\Admin\Desktop\My first Brick\Lowcode_to_code"
    
    # Define paths
    calendar_folder = os.path.join(base_path, "element_files", "calendar")
    summary_folder = os.path.join(base_path, "summary")
    
    # Set output CSV file path in the summary folder
    output_csv = os.path.join(summary_folder, "calendar_summary.csv")
    
    # Create summary folder if it doesn't exist
    if not os.path.exists(summary_folder):
        os.makedirs(summary_folder)
        print(f"Created summary folder: {summary_folder}")
    
    # Process all files
    process_calendar_folder(calendar_folder, output_csv)

if __name__ == "__main__":
    main()
