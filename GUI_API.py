import math
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import *
import enum
import os
from ctypes import windll

windll.shcore.SetProcessDpiAwareness(1)

# CONSTANT:
DEFAULT_WIDTH = 420
SUBMIT_TEXT = 'Confirm'
BROWSE_FILE = 'Browse...'


class Field:

    def __init__(self, keyword, field_type, field_label):
        """
        :param keyword: the keyword that represent the field (will be the kwarg in the action_function)
        :param field_type: the type of the field, one of 'entry' or 'combobox' or 'checkbox' or 'file'
        :param field_label: title of the field. for UI purposes.
        """
        self.keyword = keyword
        self.type = field_type
        self.label = field_label

        self.view = None
        self.variable = None
        self.frames = None
        self.values = None
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

        self.view = view
        self.variable = variable

        self.frames = (frame for frame in frames if frame)

        if values:
            self.values = values
        if var_state:
            self.var_state = var_state

    def calcHeight(self):
        return sum(cont["height"] for cont in self.frames)

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
        filename = os.path.basename(self.value) if os.path.basename(self.value) else BROWSE_FILE
        self.var_state.set(filename)

    def destroy(self):
        for frame in self.frames:
            frame.destroy()


class GUIApp(Tk):
    def __init__(self, action_func, output_type=None, title='App', resizable=False, width=DEFAULT_WIDTH):
        """
        :param action_func: the function to be called on submit,
                            its keyword-arguments are the input-fields defined in the app
                            *note: all arguments will be from type str
        :param output_type: determines the behavior on-submit and post-action_func call.
                            could be one of None, 'messagebox', 'inwindow'
                            None - destroys self on submit
                            'messagebox' - pops a message with the value returned from 'action_func'.
                            'inwindow' - prints in the app the value returned from 'action_func'.
        :param title: window's definition
        :param resizable: window's definition
        :param width: window's definition
        """
        # Error checks:
        if output_type not in (None, 'messagebox', 'inwindow'):
            raise Exception("argument value of 'output_type' is  invalid")

        super().__init__()  # calls
        super().title(title)
        super().resizable(resizable, resizable)
        self.width = width
        self.height = 0  # to be calculated
        self.accu_height = 0  # additional accumulative height for the later calculation

        self.fields_dict = {}
        self.action_func = action_func
        self.output_type = output_type

        if output_type is None or output_type == 'messagebox':
            self.body_height_ratio = 0.9
            self.body = Frame(self)
            self.body.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=self.body_height_ratio)
        elif output_type == 'inwindow':
            # with footer for output
            self.body_height_ratio = 0.7
            self.body = Frame(self)
            self.body.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=self.body_height_ratio)
            self.footer = Frame(self)
            self.footer.place(relx=0.05, rely=0.77, relwidth=0.9, relheight=0.2)
            self.output_label = Label(self.footer, text="  ", padding=10,
                                      anchor='center', background='#d2d4d2')
            self.output_label.pack(fill='both')

    def setField(self, keyword, field_type, **field_data):
        """
        :param keyword: unique name of the field, used as the id of the field,
                        also the *keyword* to be delivered to the action-function after submit
        :param field_type: type of the field, one of 'entry' or 'combobox' or 'checkbox' or 'file'
        :param field_data: data required (or optional) to create the field.
               *for 'entry' or 'checkbox':  'label' (optional) - the name of the field (will be the keyword by default),
                                            'desc' (optional) - a description attached to the field.
                                            'default' (optional) - default value for the field
               *for 'combobox' add: 'values' - dict of keys (str!, to be shown to user) mapped to values (to be delivered later)
                                                to select from (i.e. : str->any).
                                                OR list of keys (str!) to be mapped to themselves.
               *for 'file' add: 'values' - the filetypes of the needed file. example: [('Images','*.png'),('All Files','*.*')]

        :returns Adds a field to the app

         *the fields are packed in the order of insertion
         *note the return value types of the fields:
            entry -> str, checkbox -> str, combobox -> value mapped in 'values' argument, file -> str (path)
        """
        #valitidy checks and conversions
        if not field_data.get('label'):
            field_data['label'] = keyword.title()
        if field_type == 'combobox' and type(field_data.get('values')) == list:
            field_data['values']={key:key for key in field_data['values']}
        if field_type == 'combobox' and field_data.get('values') and field_data.get('default'):
            if field_data['default'] not in field_data['values']:
                raise Exception(f"invalid 'default' argument @setField:{keyword}")
        if keyword in self.fields_dict:
            raise Exception(f"Keyword '{keyword}' is already used by another field in the app")



        # initiate the Object that will represent the field
        field_obj = Field(keyword, field_type, field_data['label'])

        field = Frame(self.body, height=35)
        field.pack(padx=5, pady=0, fill='both')

        # label:
        label = Label(field, text=f"{field_data.get('label')}:")
        label.place(relwidth=0.35, relheight=1, relx=0, rely=0)

        # field input:
        input_field, var_field, var_state = None, None, None
        if field_type == 'entry':
            var_field = StringVar()
            input_field = Entry(field, textvariable=var_field)
        elif field_type == 'checkbox':
            var_field = BooleanVar()
            input_field = Checkbutton(field, onvalue=True, offvalue=False, variable=var_field)
        elif field_type == 'combobox' and field_data.get('values'):
            var_field = StringVar()
            input_field = Combobox(field, values=list(field_data['values'].keys()), state='readonly',
                                   textvariable=var_field)
        elif field_type == 'file' and field_data.get('values'):
            var_state = StringVar(value=BROWSE_FILE)
            input_field = Button(field, textvariable=var_state, command=lambda: field_obj.openFileDialog())
        else:
            raise Exception(f"Check validity of 'field_data' parameter (read the documentation) @setField:{keyword}")
        if field_data.get('default'):
            var_field.set(field_data['default'])
        input_field.place(relwidth=0.62, relx=0.38, rely=0, relheight=1)

        # description:
        field_desc_height = 0
        field_desc = None
        if field_data.get('desc'):
            field_desc_height = 27 * (field_data['desc'].count('\n') + 1)
            field_desc = Frame(self.body, height=field_desc_height)
            field_desc.pack(padx=5, pady=0, fill='both')
            label_desc = Label(field_desc, text=field_data['desc'])
            label_desc.place(relx=0.4, y=3, relwidth=0.58)

        # margin-bottom (cosmetics)
        margin_bottom = Frame(self.body, height=30)
        margin_bottom.pack(fill='both')

        # updates the field object:
        field_obj.setParams(view=input_field, variable=var_field, frames=[field, field_desc, margin_bottom],
                            values=field_data.get('values'), var_state=var_state)
        self.fields_dict[keyword] = field_obj

    def setInnerTitle(self, text):
        """sets title (packed in the order of insertion)"""
        field = Frame(self.body, height=26)
        field.pack(padx=5, pady=0, fill='both')
        label = Label(field, text=text, anchor='center', font=('Helvetica', 10, 'bold'))
        label.place(relwidth=1, relheight=1, relx=0, rely=0)

        # margin-bottom (cosmetics)
        margin_bottom = Frame(self.body, height=20)
        margin_bottom.pack(fill='both')

        self.accu_height += 26 + 20

    def submit_func(self):
        """triggered on submit click, wraps 'action_func'"""
        kargs = {}
        for key, field_obj in self.fields_dict.items():
            kargs[key] = field_obj.get()
        if self.output_type is None:
            self.destroy()
            return self.action_func(**kargs)
        else:
            output_text = str(self.action_func(**kargs))
            if self.output_type == 'inwindow':
                self.output_label.configure(text=output_text)
            if self.output_type == 'messagebox':
                messagebox.showinfo('Result', output_text)

    def run(self):
        """calls the (tkinter's) main loop and opens the window"""
        submit = Button(self.body, text=SUBMIT_TEXT, padding=5, command=self.submit_func)
        submit.pack(side='bottom')

        self.height = 40 + self.accu_height  # submit button
        self.height += sum(f.calcHeight() for f in self.fields_dict.values())
        self.height = round(self.height / self.body_height_ratio)
        self.geometry(f'{self.width}x{self.height}')

        self.mainloop()

    def deleteField(self, keyword):
        """deletes given field from the context (entirely)"""
        if keyword not in self.fields_dict:
            raise Exception('Keyword is not used as a field')
        self.fields_dict.pop(keyword).destroy()

    def destroy(self):
        super().destroy()
