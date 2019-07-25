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
            os.mkdir(self.root + "/" + unique_id)
        
        if not self.check_if_a_folder_exists(self.root + "/" + unique_id, folder_name):
            os.mkdir(self.root + "/" + unique_id + "/" + folder_name)
            return True
        return False
    
    def create_folder_for_table(self, unique_id, table_name, db_name):
        if self.check_if_a_folder_exists(self.root, unique_id):
            if self.check_if_a_folder_exists(self.root + "/" + unique_id, db_name):
                if not self.check_if_a_folder_exists(self.root + "/" + unique_id + "/" + db_name, table_name):
                    os.mkdir(self.root + "/" + unique_id + "/" + db_name + "/" + table_name)
                    return {"msg": "Successfully created the table", "flag": True}
                return {"msg": "Provided table name already exists in the DB", "flag": False}
            return {"msg": "Provided DB does not exist", "flag": False}
        return {"msg": "There are no records for this user, so he cannot create a table", "flag": False}
    
    