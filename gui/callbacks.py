"""Callback functions & State info for Sewing Pattern Configurator """

# NOTE: PySimpleGUI reference: https://github.com/PySimpleGUI/PySimpleGUI/blob/master/docs/call%20reference.md

# TODO allow changing window size? https://stackoverflow.com/questions/66379808/how-do-i-respond-to-window-resize-in-pysimplegui
# https://stackoverflow.com/questions/63686020/pysimplegui-how-to-achieve-elements-frames-columns-to-align-to-the-right-and-r
# TODO Colorscheme

import os.path
from copy import copy
from pathlib import Path
from datetime import datetime
import yaml
import shutil 
import numpy as np
import PySimpleGUI as sg


# Custom 
from assets.garment_programs.meta_garment import MetaGarment

# GUI Elements
def Collapsible(layout, key, title='', arrows=(sg.SYMBOL_DOWN, sg.SYMBOL_RIGHT), collapsed=True):
    """
    User Defined Element
    A "collapsable section" element. Like a container element that can be collapsed and brought back
    :param layout:Tuple[List[sg.Element]]: The layout for the section
    :param key:Any: Key used to make this section visible / invisible
    :param title:str: Title to show next to arrow
    :param arrows:Tuple[str, str]: The strings to use to show the section is (Open, Closed).
    :param collapsed:bool: If True, then the section begins in a collapsed state
    :return:sg.Column: Column including the arrows, title and the layout that is pinned

    # NOTE: from https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Column_Collapsible_Sections.py

    """
    return sg.Column([[sg.T((arrows[1] if collapsed else arrows[0]), enable_events=True, k=key+'-BUTTON'),
                       sg.T(title, enable_events=True, key=key+'-TITLE')],
                      [sg.pin(sg.Column(layout, key=key, visible=not collapsed, metadata=arrows))]], pad=(0,0))

icon_image_b64 = b'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'

# Utils
# TODO Probably don't belong here
# https://stackoverflow.com/a/37704379
def nested_get(dic, keys):    
    for key in keys:
        dic = dic[key]
    return dic

def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value

def nested_del(dic, keys):
    for key in keys[:-1]:
        dic = dic[key]
    del dic[keys[-1]]

def vertical_text(title):
    """ "verticalize" the text string (with newlines)

        Ref: https://github.com/PySimpleGUI/PySimpleGUI/issues/2713#issue-586409727
    """
    new_title = ""
    for letter in title:
        new_title += f"{letter}\n"
    return new_title


# State of GUI
class GUIPattern():
    def __init__(self) -> None:
        self.save_path = os.path.abspath('./')   # TODO Use Path()
        self.png_path = None
        self.tmp_path = os.path.abspath('./tmp')
        # create tmp path
        Path(self.tmp_path).mkdir(parents=True, exist_ok=True)

        self.ui_id = None   # ID of current object in the interface
        self.body_bottom = None   # Location of body center in the current png representation of a garment

        self.body_file = None
        self.design_file = None
        self.new_body_file(
            os.path.abspath('./assets/body_measurments/f_smpl_avg.yaml')
        )
        self.new_design_file(
            os.path.abspath('./assets/design_params/base.yaml')
        )

    # Info
    def isReady(self):
        """Check if the State is correct to load and save garments"""
        return self.body_file is not None and self.design_file is not None

    # Updates
    def new_body_file(self, path):
        self.body_file = path
        with open(path, 'r') as f:
            body = yaml.safe_load(f)['body']
            # TODO The following should not be here. 
            # TODO Needs to be updated when interface updates
            body['waist_level'] = body['height'] - body['head_l'] - body['waist_line']
        self.body_params = body
        self.reload_garment()

    def new_design_file(self, path):
        self.design_file = path
        with open(path, 'r') as f:
            des = yaml.safe_load(f)['design']
        self.design_params = des
        self.reload_garment()

    def reload_garment(self):
        """Reload sewing pattern with current body and design parameters"""
        if self.isReady():
            self.sew_pattern = MetaGarment('Configured_design', self.body_params, self.design_params)
            self._view_serialize()

    def _view_serialize(self):
        """Save a sewing pattern svg/png representation to tmp folder be used for display"""

        # Clear up the folder from previous version -- it's not needed any more
        self.clear_tmp()
        pattern = self.sew_pattern()
        # Save as json file
        folder = pattern.serialize(
            self.tmp_path, 
            tag='_' + datetime.now().strftime("%y%m%d-%H-%M-%S"), 
            to_subfolder=True, 
            with_3d=False, with_text=False, view_ids=False)
        
        self.body_bottom = np.asarray(pattern.body_bottom_shift)
        self.png_size = pattern.png_size

        # get PNG file!
        root, _, files = next(os.walk(folder))
        for filename in files:
            if 'pattern.png' in filename and '3d' not in filename:
                self.png_path = os.path.join(root, filename)
                break

    def clear_tmp(self, root=False):
        """Clear tmp folder"""
        shutil.rmtree(self.tmp_path)
        if not root:
            Path(self.tmp_path).mkdir(parents=True, exist_ok=True)

    # Current state
    def save(self):
        """Save current garment design to self.save_path """

        pattern = self.sew_pattern()

        # Save as json file
        folder = pattern.serialize(
            self.save_path, 
            tag='_' + datetime.now().strftime("%y%m%d-%H-%M-%S"), 
            to_subfolder=True, 
            with_3d=True, with_text=False, view_ids=False)

        with open(Path(folder) / 'body_measurements.yaml', 'w') as f:
            yaml.dump(
                {'body': self.body_params}, 
                f,
                default_flow_style=False
            )

        with open(Path(folder) / 'design_params.yaml', 'w') as f:
            yaml.dump(
                {'design': self.design_params}, 
                f,
                default_flow_style=False,
                sort_keys=False
            )

        print(f'Success! {self.sew_pattern.name} saved to {folder}')


class GUIState():
    """State of GUI-related objects"""
    def __init__(self) -> None:
        self.window = None

        # Pattern
        self.pattern_state = GUIPattern()

        # Pattern display
        self.min_margin = 10
        self.default_body_img_margins = [125, 20]   # TODO Adjust after fixing location issues
        self.body_img_margins = copy(self.default_body_img_margins)
        self.body_img_id = None
        self.back_img_id = None
        self.def_canvas_size = (1385, 805)   # TODO Adjust after fixing location issues

        # Last option needed to finalize GUI initialization and allow modifications
        self.theme()
        self.window = sg.Window(
            'Sewing Pattern Configurator', 
            self.def_layout(self.pattern_state, self.def_canvas_size), 
            icon=icon_image_b64,
            finalize=True)
        
        # Modifiers after window finalization
        self.input_text_on_enter('BODY-')
        self.input_text_on_enter('DESIGN-')
        self.prettify_sliders()
        self.init_canvas_background()
        self.init_body_silhouette()

        # Draw initial pattern
        self.upd_pattern_visual()

    def __del__(self):
        """Clenup"""
        self.pattern_state.clear_tmp(root=True)
        self.window.close()

    # Pretty stuff
    def theme(self):
        """Define and apply custom theme"""
        # Native demo https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Simple_Material_Feel.py
        # https://stackoverflow.com/a/74625488

        gui_theme = {
            "BACKGROUND": sg.COLOR_SYSTEM_DEFAULT,  #'#FFF9E7', 
            "TEXT": sg.COLOR_SYSTEM_DEFAULT, 
            "INPUT": sg.COLOR_SYSTEM_DEFAULT,
            "TEXT_INPUT": sg.COLOR_SYSTEM_DEFAULT, 
            "SCROLL": sg.COLOR_SYSTEM_DEFAULT,
            "BUTTON":  ('#505050', '#CECECE'),  # sg.COLOR_SYSTEM_DEFAULT, # ('#A714FF', '#F6E7FF'),  # sg.OFFICIAL_PYSIMPLEGUI_BUTTON_COLOR, 
            "PROGRESS": sg.COLOR_SYSTEM_DEFAULT, 
            "BORDER": 0,
            "SLIDER_DEPTH": 0.5, 
            "PROGRESS_DEPTH": 0
        }

        sg.theme_add_new('SewPatternsTheme', gui_theme)
        sg.theme('SewPatternsTheme')

    # Layout initialization / updates
    def def_layout(self, pattern, canvas_size=(500, 500)):

        # First the window layout in 2 columns

        body_layout = self.def_body_layout(pattern)

        design_layout = [
            [
                sg.Text('Design parameters: '),
            ],
            [
                sg.In(
                    default_text=self.pattern_state.design_file,
                    size=(25, 1), 
                    enable_events=True, 
                    key='DESIGNFILE'
                ),
                sg.FileBrowse(initial_folder=os.path.dirname(self.pattern_state.design_file))
            ],
            [
                sg.Column(self.def_design_tabs())
            ]
            
        ]

        # For now will only show the name of the file that was chosen
        viewer_column = [
            [
                sg.Push(),
                sg.Checkbox(
                    'Display Reference Silhouette', 
                    default=True,
                    key='BODYDISPLAY',
                    enable_events=True
                )
            ],
            [
                sg.Graph(
                    canvas_size=canvas_size, 
                    graph_bottom_left=(0, canvas_size[1]), 
                    graph_top_right=(canvas_size[0], 0), 
                    background_color='white', 
                    key='CANVAS')
            ],      
            [
                sg.Text('Output Folder:'),
                sg.In(
                    default_text=self.pattern_state.save_path, 
                    expand_x=True, 
                    enable_events=True, 
                    key='FOLDER-OUT', ),
                sg.FolderBrowse(initial_folder=self.pattern_state.save_path),
                sg.Button('Save', size=6, key='SAVE')
            ]   
        ]

        
        # ----- Full layout -----
        layout = [
            [
                sg.TabGroup(
                    [[
                        sg.Tab('Design', design_layout), 
                        sg.Tab('Body', body_layout)
                    ]], 
                    expand_y=True, 
                    tab_border_width=0, 
                    border_width=0,
                    size=(550, 1100) 
                ),
                sg.Column(viewer_column),
            ]
        ]
        return layout

    def def_body_layout(self, guipattern:GUIPattern):
        """Add fields to control body measurements"""

        param_input_col = []

        body = guipattern.body_params
        for param in body:
            param_input_col.append([
                sg.Text(
                    param + ':', 
                    justification='right', 
                    expand_x=True), 

                sg.Input(
                    str(body[param]), 
                    enable_events=False,  # Events enabled outside: only on Enter 
                    key=f'BODY-{param}', 
                    size=7) 
                ])
            
        layout = [
            [
                sg.Text('Body Mesurements: '),
            ],
            [
                sg.In(
                    default_text=self.pattern_state.body_file,
                    size=(25, 1), 
                    enable_events=True,  
                    key='BODYFILE'
                ),
                sg.FileBrowse(initial_folder=os.path.dirname(self.pattern_state.body_file))
            ],
            [
                sg.Column(param_input_col)
            ]
        ]

        return layout

    def def_flat_design_layout(self, design_params, pre_key='DESIGN', use_collapsible=False):
        """Add fields to control design parameters"""

        # TODO Unused/non-relevant fields  # Low-priority

        text_size = max([len(param) for param in design_params])

        fields = []
        for param in design_params:
            if 'v' in design_params[param]:

                p_type = design_params[param]['type']

                if 'select' in p_type:
                    values = design_params[param]['range']
                    if 'null' in p_type:
                        values.append(None)

                    in_field = sg.Combo(
                        values=design_params[param]['range'], 
                        default_value=design_params[param]['v'],
                        enable_events=True,
                        key=f'{pre_key}-{param}',
                    )
                elif p_type == 'bool':
                    in_field = sg.Checkbox(
                        param, 
                        default=design_params[param]['v'], 
                        key=f'{pre_key}-{param}',
                        enable_events=True, 
                        expand_x=True)
                elif p_type == 'int' or p_type == 'float':
                    in_field = sg.Slider( 
                        design_params[param]['range'], 
                        default_value=design_params[param]['v'],  
                        orientation='horizontal',
                        relief=sg.RELIEF_FLAT, 
                        resolution=1 if p_type == 'int' else 0.05, 
                        key=f'{pre_key}-{param}', 
                        enable_events=True
                    )
                else:
                    print(f'GUI::WARNING::Unknown parameter type: {p_type}')
                    in_field = sg.Input(
                        str(design_params[param]['v']), 
                        enable_events=False,  # Events enabled outside: only on Enter 
                        key=f'{pre_key}-{param}', 
                        size=7) 

                fields.append(
                    [
                        sg.Text(
                            param + ':', 
                            justification='right', 
                            size=text_size + 1
                        ), 
                        in_field
                    ])
                
                
            else:  # subsets of params
                if use_collapsible:
                    fields.append(
                        [ 
                            Collapsible(
                                self.def_flat_design_layout(
                                    design_params[param], 
                                    pre_key=f'{pre_key}-{param}'
                                ), 
                                title=param,
                                key=f'COLLAPSE-{pre_key}-{param}'
                            )
                        ])
                else:
                    fields.append(
                        [ 
                            sg.Frame(
                                param,
                                self.def_flat_design_layout(
                                    design_params[param], 
                                    pre_key=f'{pre_key}-{param}'
                                ), 
                                key=f'COLLAPSE-{pre_key}-{param}',
                                expand_x=True
                            )
                        ])
        
        return fields

    def def_design_tabs(self, pre_key='DESIGN'):
        """Top level categories into tabs"""

        design_params = self.pattern_state.design_params
        tabs = []
        for param in design_params:
            if 'v' in design_params[param]:
                sg.popup_error_with_traceback(
                    f'Leaf parameter on top level of design hierarchy: {param}!!'
                )
                continue
            # Tab
            tabs.append(
                sg.Tab(
                    param, 
                    self.def_flat_design_layout(
                        design_params[param], 
                        pre_key=f'{pre_key}-{param}', 
                        use_collapsible=(param == 'left')
                    ))
            )

        return [[sg.TabGroup(
                    [tabs], 
                    tab_location='lefttop', 
                    tab_border_width=0, 
                    border_width=0
                )]]


    def init_canvas_background(self):
        '''Add base background image to output canvas'''
        # https://stackoverflow.com/a/71816897

        if self.back_img_id is not None:
            self.window['CANVAS'].delete_figure(self.back_img_id)
        
        self.back_img_id = self.window['CANVAS'].draw_image(
            filename='assets/img/millimiter_paper_1500_900.png', location=(0, 0))

    def init_body_silhouette(self):
        """Add body figure to canvas"""
        if self.body_img_id is not None:
            self.window['CANVAS'].delete_figure(self.body_img_id)
        self.body_img_id = self.window['CANVAS'].draw_image(
            filename='assets/img/body_30_opacity.png', location=self.body_img_margins)

    # Updates
    def upd_canvas_size(self, new):
        """Update size of canvas (visualization window)
        
            NOTE: Nothing is updated if the size is the same
        """

        # https://github.com/PySimpleGUI/PySimpleGUI/issues/2842#issuecomment-890049683
        upd_canvas_size = (
            max(new[0], self.def_canvas_size[0]),
            max(new[1], self.def_canvas_size[1])
        )
        if upd_canvas_size == self.window['CANVAS'].get_size():
            # Don't do anything if the size didn't actually change
            return
        
        # DEBUG
        print(f'GUI::Resizing::{upd_canvas_size} from {self.window["CANVAS"].get_size()}')

        # UPD canvas
        self.window['CANVAS'].set_size(upd_canvas_size)
        self.window['CANVAS'].change_coordinates(
            (0, upd_canvas_size[1]), (upd_canvas_size[0], 0))

    def upd_pattern_visual(self):

        print(f'GUI::Info::New Pattern')  # DEBUG
        if self.pattern_state.ui_id is not None:
            self.window['CANVAS'].delete_figure(self.pattern_state.ui_id)
            self.pattern_state.ui_id = None

        # Image body center with the body center of a body silhouette
        png_body = self.pattern_state.body_bottom
        real_b_bottom = np.asarray([
            429/2 + self.default_body_img_margins[0], 
            530 + self.default_body_img_margins[1]
        ])   # Not the very bottom  # TODO avoid hardcoding the size..
        location = real_b_bottom - png_body

        # Adjust the body location (margins) to fit the pattern
        if location[0] < 0: 
            self.body_img_margins[0] = self.default_body_img_margins[0] - location[0]
            self.body_img_margins[1] = self.default_body_img_margins[1]
            location[0] = 0
        else: 
            self.body_img_margins[:] = self.default_body_img_margins
        
        # Change canvas size to fit a pattern (if needed)
        self.upd_canvas_size((
            location[0] + self.pattern_state.png_size[0] + self.min_margin,
            location[1] + self.pattern_state.png_size[1] + self.min_margin
        ))
        # Align body with the pattern
        if self.body_img_id is not None:
            self.window['CANVAS'].relocate_figure(self.body_img_id, *self.body_img_margins)

        # Display the pattern
        self.pattern_state.ui_id = self.window['CANVAS'].draw_image(
            filename=self.pattern_state.png_path, location=location.tolist())

    def upd_fields_body(self):
        """Update current values of the fields 
            if they were loaded from a file
        """
        fields = self.get_keys_by_instance_tag(sg.Input, 'BODY-')
        for elem in fields:
            param = elem.split('-')[1]
            self.window[elem].update(self.pattern_state.body_params[param])
    
    def upd_fields_design(self, design_params, pre_key='DESIGN'):
        """Update current values of the fields 
            if they were loaded from a file
        """
        for param in design_params:
            if 'v' in design_params[param]:
                self.window[f'{pre_key}-{param}'].update(design_params[param]['v'])
            else:
                self.upd_fields_design(
                    design_params[param], 
                    f'{pre_key}-{param}'
                )

    # Modifiers after window finalization
    def input_text_on_enter(self, tag):
        """Modify input text elements to only send events when Enter is pressed"""
        # https://stackoverflow.com/a/68528658

        # All body updates
        fields = self.get_keys_by_instance_tag(sg.Input, tag)
        for key in fields:
            self.window[key].bind('<Return>', '-ENTER')

    def prettify_sliders(self):
        """ Make slider knowbs flat and small
            A bit of hack accessing lower level library (Tkinter) to reach the needed setting
            NOTE: It needs to be executed after window finalization
        """
        # https://github.com/PySimpleGUI/PySimpleGUI/issues/10#issuecomment-997426666
        # https://www.tutorialspoint.com/python/tk_scale.htm
        # https://tkdocs.com/pyref/scale.html
        window = self.window
        slider_keys = self.get_keys_by_instance(sg.Slider)
        for key in slider_keys:
            window[key].Widget.config(sliderlength=10)
            window[key].Widget.config(sliderrelief=sg.RELIEF_FLAT)
            # window[key].Widget.config(background='#000000') # slider button
            # window[key].Widget.config(troughcolor='#FFFFFF')  

    # Utils
    def get_keys_by_instance(self, instance_type):
        # https://github.com/PySimpleGUI/PySimpleGUI/issues/10#issuecomment-997426666
        return [key for key, value in self.window.key_dict.items() if isinstance(value, instance_type)]

    def get_keys_by_instance_tag(self, instance_type, tag):
        # https://github.com/PySimpleGUI/PySimpleGUI/issues/10#issuecomment-997426666
        return [key for key, value in self.window.key_dict.items() if isinstance(value, instance_type) and tag in key]

    # Main loop
    def event_loop(self):
        while True:
            event, values = self.window.read()

            # --- Window layout actions ---
            if event == 'Exit' or event == sg.WIN_CLOSED:
                break
            elif event.startswith('COLLAPSE'):
                field = event.removesuffix('-BUTTON').removesuffix('-TITLE')
                # Visibility
                self.window[field].update(visible=not self.window[field].visible)
                # UPD graphic
                self.window[field + '-BUTTON'].update(
                    self.window[field].metadata[0] if self.window[field].visible else self.window[field].metadata[1])
            elif event == 'BODYDISPLAY':
                # Toggle display of body figure
                if self.body_img_id is not None:
                    # Already diplayed
                    self.window['CANVAS'].delete_figure(self.body_img_id)
                    self.body_img_id = None
                else:
                    self.init_body_silhouette()
                    # rearrange images correctly 
                    self.window['CANVAS'].send_figure_to_back(self.body_img_id)
                    self.window['CANVAS'].send_figure_to_back(self.back_img_id)

            # ----- Garment-related actions -----
            try: 
                if event == 'BODYFILE':
                    file = values['BODYFILE']
                    self.pattern_state.new_body_file(file)

                    self.upd_fields_body()
                    self.upd_pattern_visual()

                elif event.startswith('BODY-') and '-ENTER' in event:
                    # Updated body parameter:
                    param = event.split('-')[1]
                    new_value = values[event.removesuffix('-ENTER')]

                    try:   # https://stackoverflow.com/a/67432444
                        self.pattern_state.body_params[param] = float(new_value)
                    except: # check numerical
                        sg.popup(
                            'Only numerical values are supported (int, float)',
                            icon=icon_image_b64
                        )
                    else:
                        self.pattern_state.reload_garment()
                        self.upd_pattern_visual()

                elif event.startswith('DESIGN-'): 
                    # Updated body parameter:
                    event_name = event.removesuffix('-ENTER')
                    param_ids = event_name.split('-')[1:]
                    new_value = values[event_name]

                    # DEBUG
                    print('NEW DESIGN EVENT: ', event, new_value, type(new_value))

                    # TODO Is it needed?
                    try:   # https://stackoverflow.com/a/67432444
                        conv_value = float(new_value)
                    except: # check non-numericals
                        conv_value = new_value
                    finally:
                        nested_set(self.pattern_state.design_params, param_ids + ['v'], conv_value)
                        self.pattern_state.reload_garment()
                        self.upd_pattern_visual()

                elif event == 'DESIGNFILE':  # A file was chosen from the listbox
                    file = values['DESIGNFILE']
                    self.pattern_state.new_design_file(file)

                    self.upd_fields_design(self.pattern_state.design_params)
                    self.upd_pattern_visual()

                elif event == 'SAVE':
                    self.pattern_state.save()

                elif event == 'FOLDER-OUT':
                    self.pattern_state.save_path = values['FOLDER-OUT']

                    print('PatternConfigurator::INFO::New output path: ', self.pattern_state.save_path)
            
            except BaseException as e:
                sg.popup_error_with_traceback(
                    'Application ERROR detected (see below)', 
                    str(e)
                )

