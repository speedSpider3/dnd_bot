class Player:

    def __init__(self,player_name,class_type):
        self.player_name = player_name
        self.class_type = class_type

    def get_class(self):
        return self.class_type.to_string()

    def get_player_name(self):
        return self.player_name

    def to_string(self):
        return self.get_player_name() + ": " + self.get_class()