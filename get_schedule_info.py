import xml.etree.ElementTree as ET
import os
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
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Define namespaces if needed
        namespaces = {
            'bpr': 'http://www.blueprism.co.uk/product/release',
            'bp': 'http://www.blueprism.co.uk/product/process'
        }
        
        # Dictionary to store schedule info
        schedule_info = {
            'name': '',
            'description': '',
            'start_date': '',
            'end_date': '',
            'frequency': '',
            'status': '',
            'last_run': '',
            'next_run': '',
            'processes': []
        }
        
        # Extract basic schedule information
        schedule = root.find('.//schedule', namespaces) or root
        
        if schedule is not None:
            # Get basic attributes
            schedule_info['name'] = schedule.get('name', '')
            schedule_info['description'] = schedule.findtext('description', '')
            schedule_info['status'] = schedule.get('status', '')
            
            # Get dates if they exist
            start_date = schedule.findtext('startDate', '')
            if start_date:
                schedule_info['start_date'] = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
                
            end_date = schedule.findtext('endDate', '')
            if end_date:
                schedule_info['end_date'] = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d')
            
            # Get frequency information
            frequency = schedule.find('frequency')
            if frequency is not None:
                schedule_info['frequency'] = {
                    'type': frequency.get('type', ''),
                    'interval': frequency.get('interval', ''),
                    'days': frequency.findtext('days', ''),
                    'time': frequency.findtext('time', '')
                }
            
            # Get process information
            processes = schedule.findall('.//process')
            for process in processes:
                process_info = {
                    'name': process.get('name', ''),
                    'id': process.get('id', ''),
                    'parameters': []
                }
                
                # Get process parameters if they exist
                params = process.findall('.//parameter')
                for param in params:
                    param_info = {
                        'name': param.get('name', ''),
                        'value': param.text or ''
                    }
                    process_info['parameters'].append(param_info)
                
                schedule_info['processes'].append(process_info)
        
        return schedule_info
    
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return None
    except Exception as e:
        print(f"Error processing schedule information: {e}")
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
    print(f"Name: {schedule_info['name']}")
    print(f"Description: {schedule_info['description']}")
    print(f"Status: {schedule_info['status']}")
    print(f"Start Date: {schedule_info['start_date']}")
    print(f"End Date: {schedule_info['end_date']}")
    
    if schedule_info['frequency']:
        print("\n--- Frequency ---")
        freq = schedule_info['frequency']
        print(f"Type: {freq['type']}")
        print(f"Interval: {freq['interval']}")
        print(f"Days: {freq['days']}")
        print(f"Time: {freq['time']}")
    
    if schedule_info['processes']:
        print("\n--- Processes ---")
        for proc in schedule_info['processes']:
            print(f"\nProcess: {proc['name']} (ID: {proc['id']})")
            if proc['parameters']:
                print("Parameters:")
                for param in proc['parameters']:
                    print(f"  - {param['name']}: {param['value']}")

def main():
    # Get input file from user or use default
    xml_file = input("Enter path to the schedule XML file (or press Enter to use default 'schedule.xml'): ")
    if not xml_file:
        xml_file = "schedule.xml"
    
    if not os.path.exists(xml_file):
        print(f"Error: File '{xml_file}' not found")
        return
    
    # Get and print schedule information
    schedule_info = get_schedule_info(xml_file)
    print_schedule_info(schedule_info)

if __name__ == "__main__":
    main()
