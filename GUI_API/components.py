from tkinter import filedialog
import os

from GUI_API.config import *

class Item:
    """represents a GUI-Item"""
    keywords_list = []  # static variable that tracks all created items

    def __init__(self,item_type,keyword=None):
        """initiates type, keyword and frames
        :param item_type: the type of the item
        :param keyword: the keyword that represent the item (for non-field item - it's generated)
        """

        self.frames = None
        self.type = item_type
        if keyword: # keyword is defined (a field)
            self.keyword = keyword
        else: #pure item
            #generates an item keyword, example: '$title_1'
            num = max([int(key.split('_')[-1]) for key in Item.keywords_list if item_type in key],default=1)
            num = num+1 if num else 1
            self.keyword=f'${item_type}_{num}'
            Item.keywords_list.append(self.keyword)


    def setFrames(self,frames):
        self.frames = (frame for frame in frames if frame)

    def calcHeight(self):
        return sum(cont['height'] for cont in self.frames)

    def destroy(self):
        if self.keyword[0]=='$': #is a pure item
            Item.keywords_list.remove(self.keyword)

        for frame in self.frames:
            frame.destroy()


class Field (Item):
    """represents a Field GUI-Item"""

    def __init__(self, keyword, field_type, field_label):
        """
        :param keyword: the keyword that represent the field (will be the kwarg in the action_function)
        :param field_type: the type of the field, one of 'entry' or 'combobox' or 'checkbox' or 'file'
        :param field_label: title of the field. for UI purposes.
        """
        super().__init__(field_type,keyword)

        self.label = field_label

        self.view = None
        self.variable = None
        self.values = None
        # frames inherited from Item
        self.var_state = None

    def setParams(self, view, variable, frames, values=None, var_state=None):
        """
        :param view: the tkinter object of the field
        :param variable: the dynamic variable (=object) that represents the value of the field
        :param frames: the containers (=iterable of tkinter objects) of the field element
        :param values: list of values that defines the field
                        for 'combobox' - the list of options; for 'file' - the list of
        :param var_state: dynamic variable represents the state of the field. for UI purposes.
        """
        super().setFrames(frames)

        self.view = view
        self.variable = variable

        if values:
            self.values = values
        if var_state:
            self.var_state = var_state


    def get(self):
        if self.type == 'file':
            return self.variable
        if self.type =='combobox':
            return self.values.get(self.variable.get()) #translate chosen key by given map

        return self.variable.get()

    def openFileDialog(self):
        if self.type != 'file':
            raise Exception("Can't call 'openFileDialog' on non-file type")
        self.variable = filedialog.askopenfilename(title=self.label, filetypes=self.values)  # initialdir = '/'
        filename = os.path.basename(self.variable) if os.path.basename(self.variable) else BROWSE_FILE
        self.var_state.set(filename)


