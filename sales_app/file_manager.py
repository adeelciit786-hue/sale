import os
import json
from pathlib import Path
from werkzeug.utils import secure_filename

class FileManager:
    """Handles file operations: uploads, deletions, persistence."""
    
    def __init__(self, data_dir='./data'):
        self.data_dir = Path(data_dir)
        self.historical_dir = self.data_dir / 'historical'
        self.current_dir = self.data_dir / 'current'
        self.targets_file = self.data_dir / 'targets.json'
        
        # Ensure directories exist
        self.historical_dir.mkdir(parents=True, exist_ok=True)
        self.current_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save_historical_file(self, file, filename):
        """
        Save historical data file. Replaces if exists.
        
        Args:
            file: Flask file object
            filename: Safe filename
            
        Returns:
            tuple: (success, message, filepath)
        """
        try:
            filename = secure_filename(filename)
            filepath = self.historical_dir / filename
            
            # Delete existing file if present
            if filepath.exists():
                try:
                    filepath.unlink()
                except Exception as e:
                    return False, f"Could not delete existing file: {str(e)}", None
            
            # Save new file
            file.save(str(filepath))
            return True, f"Historical file '{filename}' saved successfully", str(filepath)
            
        except Exception as e:
            return False, f"Error saving historical file: {str(e)}", None
    
    def save_current_month_file(self, file, filename):
        """
        Save current month file. Replaces any existing current file.
        
        Args:
            file: Flask file object
            filename: Safe filename
            
        Returns:
            tuple: (success, message, filepath)
        """
        try:
            filename = secure_filename(filename)
            
            # Delete any existing current file
            try:
                for existing_file in self.current_dir.glob('*'):
                    if existing_file.is_file():
                        existing_file.unlink()
            except Exception as e:
                pass  # Ignore deletion errors
            
            # Save new file
            filepath = self.current_dir / filename
            file.save(str(filepath))
            return True, f"Current month file saved successfully", str(filepath)
            
        except Exception as e:
            return False, f"Error saving current month file: {str(e)}", None
    
    def delete_historical_file(self, filename):
        """
        Delete historical file.
        
        Returns:
            tuple: (success, message)
        """
        try:
            filename = secure_filename(filename)
            filepath = self.historical_dir / filename
            
            if filepath.exists():
                filepath.unlink()
                return True, f"File '{filename}' deleted successfully"
            else:
                return True, f"File '{filename}' not found (already deleted)"
                
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"
    
    def delete_current_month_file(self):
        """Delete current month file."""
        try:
            for file in self.current_dir.glob('*'):
                if file.is_file():
                    file.unlink()
            return True, "Current month file deleted"
        except Exception as e:
            return False, f"Error deleting current file: {str(e)}"
    
    def get_historical_files(self):
        """
        Get all historical files.
        
        Returns:
            list: [(filename, filepath), ...]
        """
        try:
            files = []
            if self.historical_dir.exists():
                for file in self.historical_dir.glob('*.xlsx'):
                    files.append((file.name, str(file)))
            return sorted(files)
        except Exception as e:
            print(f"Error listing historical files: {e}")
            return []
    
    def get_current_month_file(self):
        """
        Get current month file if exists.
        
        Returns:
            tuple: (filename, filepath) or (None, None)
        """
        try:
            if self.current_dir.exists():
                files = list(self.current_dir.glob('*.xlsx'))
                if files:
                    file = files[0]
                    return file.name, str(file)
            return None, None
        except Exception as e:
            print(f"Error getting current month file: {e}")
            return None, None
    
    def save_targets(self, targets_dict):
        """
        Save targets to JSON file.
        
        Args:
            targets_dict: {month_identifier: target_value, ...}
            
        Returns:
            tuple: (success, message)
        """
        try:
            with open(self.targets_file, 'w') as f:
                json.dump(targets_dict, f, indent=2)
            return True, "Targets saved successfully"
        except Exception as e:
            return False, f"Error saving targets: {str(e)}"
    
    def load_targets(self):
        """
        Load targets from JSON file.
        
        Returns:
            dict: {month_identifier: target_value, ...}
        """
        try:
            if self.targets_file.exists():
                with open(self.targets_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading targets: {e}")
            return {}
    
    def get_target_for_current_month(self, current_filename):
        """
        Get target for current month based on filename.
        
        Args:
            current_filename: Filename of current month file
            
        Returns:
            float: Target value or 0
        """
        if not current_filename:
            return 0
        
        targets = self.load_targets()
        # Use filename (without extension) as key
        key = Path(current_filename).stem
        return float(targets.get(key, 0))
    
    def save_target_for_current_month(self, current_filename, target_value):
        """
        Save target for current month.
        
        Args:
            current_filename: Filename of current month file
            target_value: Target amount
            
        Returns:
            tuple: (success, message)
        """
        try:
            if not current_filename:
                return False, "No current month file loaded"
            
            targets = self.load_targets()
            key = Path(current_filename).stem
            targets[key] = float(target_value)
            
            return self.save_targets(targets)
        except Exception as e:
            return False, f"Error saving target: {str(e)}"
