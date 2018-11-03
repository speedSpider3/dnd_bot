class Player_Class:

    def __init__(self,class_name,subclass_name):
        self.class_name = class_name
        self.subclass_name = subclass_name

    def get_name(self):
        return self.class_name

    def get_subclass(self):
        return self.subclass_name

    def to_string(self):
        return self.get_name() + " (" + self.get_subclass() + ")"