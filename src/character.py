class Character:

    def __init__(self,name,class_name,subclass_name=""):
        self.name = name
        self.class_name = class_name
        self.subclass_name = subclass_name

    def set_subclass(self, subclass):
        self.subclass_name = subclass

    def get_class(self):
        str_name = self.class_name
        if not self.subclass_name == "":
            str_name += " (" + self.subclass_name + ")"
        return str_name

    def get_name(self):
        return self.name

    def to_string(self):
        return self.get_name() + ": " + self.get_class()