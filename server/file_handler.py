import pickle
import os

class FileHandler:
    def __init__(self):
        self.root = "../db"

    def get_immediate_subdirectories(self, path):
        return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

    def check_if_a_folder_exists(self, root, folder_name):
        dbs = self.get_immediate_subdirectories(root)
        if folder_name in dbs:
            return True
        return False
    
    def create_folder(self, unique_id, folder_name):
        if not self.check_if_a_folder_exists(self.root, unique_id):
            os.mkdir("../db/" + unique_id)
        
        if not self.check_if_a_folder_exists(self.root + "/" + unique_id, folder_name):
            os.mkdir("../db/" + unique_id + "/" + folder_name)
            return True
        return False
    
    