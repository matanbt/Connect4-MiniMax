from GUI_API.components import *
from GUI_API.config import *

from tkinter import *
from tkinter import messagebox, scrolledtext
from tkinter.ttk import *
import datetime

from ctypes import windll

# fixes sharpness issue
windll.shcore.SetProcessDpiAwareness(1)


class FormGUI(Tk):
    """Builds form-like GUI with some output options, to drive an 'action_func' """



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
        if output_type not in output_types:
            raise Exception("argument value of 'output_type' is  invalid")

        super().__init__()
        super().title(title)
        super().resizable(resizable, resizable)
        self.width = width
        self.additional_height = 0
        self.height = 0  # to be calculated

        self.items_dict = {}  # contains all the items packed in the app, with keyword '$non_field'
        self.action_func = action_func
        self.output_type = output_type

        self.body_height_ratio = 0.9
        self.body = Frame(self)
        self.body.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=self.body_height_ratio)

        if output_type == 'inwindow':
            self.output_label = Label(self.body, text="  ", padding=10,
                                      anchor='center', background='#d2d4d2')
            self.output_label.pack(side='bottom', fill='both')
            self.additional_height += 70

        # submit button:
        submit = Button(self.body, text=SUBMIT_TEXT, padding=5, command=self.submit_func)
        submit.pack(side='bottom', pady=15)
        self.additional_height += 40

    def setField(self, keyword, field_type, **field_data):
        """
        :param keyword: unique name of the field, used as the id of the field,
                        also the *keyword* to be delivered to the action-function after submit
        :param field_type: type of the field, one of 'entry' or 'combobox' or 'checkbox' or 'file'
        :param field_data: (kargs) data required (or optional) to create the field.
                                            possible arguments:
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
            entry -> str; checkbox -> str; combobox -> return the mapped value from 'values'; file -> str (path)
        """
        # validity checks and conversions
        if not field_data.get('label'):
            field_data['label'] = keyword.title()
        if field_type == 'combobox' and type(field_data.get('values')) == list:
            field_data['values'] = {key: key for key in field_data['values']}
        if field_type == 'combobox' and field_data.get('values') and field_data.get('default'):
            if field_data['default'] not in field_data['values']:
                raise Exception(f"invalid 'default' argument @setField:{keyword}")
        if keyword in self.items_dict:
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
        self.items_dict[keyword] = field_obj

    def setItem(self, item_type, text):
        """
        sets title (packed in the order of insertion)
        :param item_type: one of 'title'
        :param text:
        :return:
        """

        # initiate the Object that will represent the field
        item_obj = Item(item_type)

        if item_type == 'title':
            field = Frame(self.body, height=26)
            field.pack(padx=5, pady=0, fill='both')
            label = Label(field, text=text, anchor='center', font=('Helvetica', 10, 'bold'))
            label.place(relwidth=1, relheight=1, relx=0, rely=0)

            # margin-bottom (cosmetics)
            margin_bottom = Frame(self.body, height=20)
            margin_bottom.pack(fill='both')

            # updates the field object:
            item_obj.setFrames([field, margin_bottom])
            self.items_dict[item_obj.keyword] = item_obj

    def getFields(self):
        """return a list with keyword,field-object pairs (with the fields only)"""
        return [pair for pair in self.items_dict.items() if pair[0][0] != '$']

    def submit_func(self):
        """triggered on submit click, wraps 'action_func'"""
        kargs = {}
        for key, field_obj in self.getFields():
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

        self.height = sum(f.calcHeight() for f in self.items_dict.values()) + self.additional_height
        self.height = round(self.height / self.body_height_ratio)
        self.geometry(f'{self.width}x{self.height}')

        self.mainloop()

    def deleteItem(self, obj):
        """deletes given item instance (returned on setItem/setField function) from the context (entirely)"""
        self.items_dict.pop(obj.keyword).destroy()

    def destroy(self):
        super().destroy()


class RunningScriptGUI(Tk):
    """
     ---- FEATURE ON-DEVELOPMENT ----
    GUI platform for a running script that prints messages (logs)
    :param: userStoppedScript - a flag indicates whether Stop button was clicked by user or not.
                                breaking the script is up to the developer
    """


    def __init__(self, script, title="App", resizable=True):
        super().__init__()
        super().title(title)
        super().resizable(resizable, resizable)
        super().geometry(f'{800}x{400}')
        self.script=script
        self.run_onopen=True#run_onopen

        self.body_height_ratio = 0.70
        self.margin_height_ratio = 0.10  # sum of margins
        self.body = Frame(self)
        self.body.place(relx=0.05, rely=0.05, relwidth=0.90, relheight=self.body_height_ratio)
        self.txt = scrolledtext.ScrolledText(self.body, wrap='word', font=('consolas', '12'),state=DISABLED)
        self.txt.pack(expand=True, fill='both')

        self.footer = Frame(self)
        self.footer.place(relx=0.05, rely=self.body_height_ratio+self.margin_height_ratio, relwidth=0.90,
                          relheight=1 - self.body_height_ratio - self.margin_height_ratio*1.5)

        self.run_button = Button(self.footer, text=RUN_TEXT, padding=5,command=self.runScript)
        self.userStoppedScript=False
        self.stop_button = Button(self.footer, text=STOP_TEXT, padding=5,command=self.setStopScript)
        self.run_button.place(relx=0.8, rely=0.1, relheight=0.9, relwidth=0.2)
        self.stop_button.place(relx=0.6, rely=0.1, relheight=0.9, relwidth=0.18)


    def print(self, text):
        """
        display given message with the time it was sent
        :param text: message to display in the screen
        :return:
        """
        self.txt['state'] = NORMAL
        self.txt.insert(END,(datetime.datetime.now()).strftime('%x-%X'))
        self.txt.insert(END, '  ')
        self.txt.insert(END, text)
        self.txt.insert(END, '\n')
        self.txt['state'] = DISABLED
        self.txt.update_idletasks()  #enter main loop and keeps display updated while script's running
        self.txt.see(END)


    def setStopScript(self):
        self.userStoppedScript=True

    def runScript(self):
        self.userStoppedScript=False
        self.script(self)

    def run(self):
        """calls the (tkinter's) main loop and opens the window"""
        self.mainloop()
