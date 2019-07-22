import pickle
import os

class FileHandler:
    def get_immediate_subdirectories(self, path):
        return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

    def check_if_a_folder_exists(self, folder_name):
        dbs = self.get_immediate_subdirectories("../db")
        if folder_name in dbs:
            return True
        return False
    
    def create_folder(self, folder_name):
        if not self.check_if_a_folder_exists(folder_name):
            os.mkdir("../db/" + folder_name)
            return True
        return False