from typing import List, Optional
from abc import ABC, abstractmethod
import yaml
import os
import shutil
from typing import List

baseRepoDir = "/data/generated_repos/githubRepo"

class YmlFile(ABC):
    def __init__(self, id: str, name: str, description: Optional[str] = None):
        if not id or not name or not id.strip() or not name.strip():
            raise ValueError("ID and name are required")
        
        self.id = str(id).lower()
        self.name = name
        self.description = description

    def __str__(self) -> str:
        result = f"id: {self.id}\nname: {self.name}\n"
        return result

class RepositoryLevelYmlFile(YmlFile):
    def __init__(self, id: str, name: str, description: str, type: str = "",
                 password: str = "", award: str = "", image: str = "", 
                 modules: List[str] = None):
        super().__init__(id, name, description)
        
        if not modules:
            raise ValueError("Modules cannot be empty")
        
        if any(not module or not module.strip() for module in modules):
            raise ValueError("Invalid module name")
            
        self.type = "more" if type==None else type
        self.password = password
        self.award = award
        self.image = "pwncollege/challenge-simple" if not image.strip() else image
        self.modules = modules

    def __str__(self) -> str:
        result = super().__str__()
        result += f"type: {self.type}\n"
        
        if self.password and self.password.strip():
            result += f"password: {self.password}\n"
            
        if self.award.strip():
            result += f"award:\n emoji: {self.award}\n"
            
        result += f"image: {self.image}\n"
        result += "modules:\n"
        
        for module in self.modules:
            result += f" - id: {module}\n"
        return result

class Challenge:
    def __init__(self, id: str, name: str, files: List[str], parent = None):
        self.id = str(id).lower()
        self.name = name
        self.files = files
        self.parent = parent

    def __str__(self) -> str:
        return f"  - id: {self.id}\n    name: {self.name}\n"

class ModuleLevelYml(YmlFile):
    def __init__(self, id: str, name: str, description: str, 
                 challenges: List[Challenge]):
        super().__init__(id, name, description)
        self.challenges = challenges

    def __str__(self) -> str:
        result = f"name: {self.name}\n"
        result += "challenges:\n"
        for challenge in self.challenges:
            result += str(challenge)
        return result



def build_repo_yml(input_source) -> RepositoryLevelYmlFile:
    #print("Hello! I'm here to help you build your command line CTF.\n")
    #print("What should its ID be? It must be unique (different from the other available CTFs).")
    id = input_source["id"]
    print("id")
    #print("What would you like the name of your CTF to be?")
    name = input_source["name"]
    print("name")
    #print("Would you like a description? If not, press enter")
    description = input_source["description"]
    print("desc")
    #print("What will the type be? [course/topic/hidden] or just press enter.")
    type = input_source["type"]
    print("type")
    
    #print("Would you like a password? If not, press enter.")
    password = input_source["password"]
    print("pw")
    #print("What would you like the award to be? Please enter an emoji")
    award = input_source["award"]
    print("award")
    #print("What would you like the image path to be? Press enter for default.")
    image = ""
    try:
        image = input_source["image"]
        if image == None:
            image = ""
    except:
        print("no image")
    #print("Please enter the names of your modules 1 at a time. Submit a blank name when done.")
    modules = []
    if  input_source["modules"] == None:
        raise ValueError("Modules are required")
    for arr in input_source["modules"]:
        modules.append(arr[0])
    
    return RepositoryLevelYmlFile(id, name, description, type, password, award, image, modules)

def get_code(input_source, modules: List[ModuleLevelYml], repoDir):
    try:
        for m in modules:
            for c in m.challenges:
                #print(f'For your module named "{m.name}", what files would you like to use? Input a blank when done.')
                file_paths = c.files
                if not file_paths:
                    break
                for file_path in file_paths:
                    source = os.path.abspath(file_path)
                    dest_dir = os.path.join(repoDir, m.name.lower(), c.id)
                    dest = os.path.join(dest_dir, os.path.basename(source))
                    print(source)
                    try:
                        shutil.copy2(source, dest)
                    except:
                        shutil.rmtree(dest, ignore_errors=True)
                        shutil.copytree(source, dest)
    except Exception as e:
        print(f"Error: {e}")

def get_module_level(input_source, rlyf: RepositoryLevelYmlFile) -> List[ModuleLevelYml]:
    module_level_ymls = []
    
    for module in input_source["modules"]:
        #print(f'For your module named "{module}", what would you like its ID to be?')
        id = module[1]
        
        #print("Would you like a description? If not, press enter")
        description = module[2]
        
        #print("Please enter the names of your challenges 1 at a time. Submit a blank name when done.")
        challenges = []
        if(len(module[3])) == 0:
            raise ValueError("Must have challenges in your module")
        for chal in module[3]:
            if(chal[0] == None or chal[1] == None):
                raise ValueError("Must have a name for your challenges")
            for file in chal[1]:
                try:
                    open(file, "r")
                except :
                    os.listdir(file)
                
            challenges.append(Challenge(chal[0].lower(), chal[0], chal[1]))

        
        module_level_ymls.append(ModuleLevelYml(id, module[0], description, challenges))
    
    return module_level_ymls

def write_to_files(rlyf: RepositoryLevelYmlFile, module_level_ymls: List[ModuleLevelYml], repoDir):
    try:
        # Create main directory
        os.makedirs(repoDir, exist_ok=True)
        
        # Create module directories and their challenge subdirectories
        for mod in module_level_ymls:
            mod_path = os.path.join(repoDir, mod.name.lower())
            os.makedirs(mod_path, exist_ok=True)
            for c in mod.challenges:
                os.makedirs(os.path.join(mod_path, c.id), exist_ok=True)
        
        # Write repository level YAML
        with open(f"{repoDir}/dojo.yml", "w") as repo_out:
            repo_out.write(str(rlyf))
        
        if rlyf.description:
            with open(f"{repoDir}/DESCRIPTION.md", "w") as repo_out:
                repo_out.write(rlyf.description)
        
        # Write module level YAMLs
        for mod in module_level_ymls:
            with open(f"{repoDir}/{mod.name}/module.yml", "w") as mod_out:
                mod_out.write(str(mod))
                if(mod.description): 
                    with open(f"{repoDir}/{mod.name}/DESCRIPTION.md", "w") as desc_out:
                        desc_out.write(mod.description)
                
    except Exception as e:
        print(f"Error: {e}")

def main(filename):
    import sys
    # Handle input source (file or stdin)
    with open(sys.argv[1], "r") as file:
        input_source = yaml.safe_load(file)
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], "r") as file:
                input_source = yaml.safe_load(file)
        except Exception as e:
            if filename:
                input_source = open(filename, 'r')
            else:
                input_source = sys.stdin
        if len(sys.argv) > 2:
            baseRepoDir = sys.argv[2]
            os.makedirs(baseRepoDir, exist_ok=True)
    
    
    print(input_source)
    rlyf = build_repo_yml(input_source)
    module_level_ymls = get_module_level(input_source, rlyf)
    write_to_files(rlyf, module_level_ymls, baseRepoDir)
    get_code(input_source, module_level_ymls, baseRepoDir)

    
            

if __name__ == "__main__":
    main(None)
