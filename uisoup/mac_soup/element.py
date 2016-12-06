# !/usr/bin/env python

#    Copyright (c) 2014 Max Beloborodko.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

__author__ = 'f1ashhimself@gmail.com'

from ..interfaces.i_element import IElement
import atomac
from ..utils.mac_utils import MacUtils
from .. import TooSaltyUISoupException
from .mouse import MacMouse


class MacElement(IElement):

    _acc_role_name_map = {
        'AXWindow': u'frm',
        'AXTextArea': u'txt',
        'AXTextField': u'txt',
        'AXButton': u'btn',
        'AXStaticText': u'lbl',
        'AXRadioButton': u'rbtn',
        'AXSlider': u'sldr',
        'AXCell': u'tblc',
        'AXImage': u'img',
        'AXToolbar': u'tbar',
        'AXScrollBar': u'scbr',
        'AXMenuItem': u'mnu',
        'AXMenu': u'mnu',
        'AXMenuBar': u'mnu',
        'AXMenuBarItem': u'mnu',
        'AXCheckBox': u'chk',
        'AXTabGroup': u'ptl',
        'AXList': u'lst',
        'AXMenuButton': u'cbo',
        'AXRow': u'tblc',
        'AXColumn': u'col',
        'AXTable': u'tbl',
        'AXScrollArea': u'sar',
        'AXOutline': u'otl',
        'AXValueIndicator': u'val',
        'AXDisclosureTriangle': u'dct',
        'AXGroup': u'grp',
        'AXPopUpButton': u'pubtn',
        'AXApplication': u'app',
        'AXDocItem': u'doc',
        'AXHeading': u'tch',
        'AXGenericElement': u'gen',
        'AXLink': u'lnk'
    }

    _mouse = MacMouse()

    def __init__(self, atomac_object, process_name, process_id):
        """
        Constructor.

        Arguments:
            - atomac_object: string, object selector.
        """

        self._element = atomac_object
        self._proc_name = process_name
        self._proc_id = process_id
        self._cached_children = set()
        self._cached_properties = None

    @property
    def _properties(self):
        """
        Property for element properties.
        """

        if not self._cached_properties:
            self._cached_properties = \
                MacUtils.ApplescriptExecutor.get_element_properties(self._element)

        return self._cached_properties

    @property
    def _role(self):
        """
        Property for element role.
        """

        return self._properties.get('AXRole', None)

    def _find_windows_by_same_proc(self):
        """
        Find window by same process id.

        Arguments:
            - None

        Returns:
            - list of windows.
        """

        app = atomac.getAppRefByPid(self.proc_id)
        app.activate()
        return app.windowsR()

    def click(self, x_offset=None, y_offset=None):
        x, y, w, h = self.acc_location
        x += x_offset if x_offset is not None else int(w / 2)
        y += y_offset if y_offset is not None else int(h / 2)

        self._mouse.click(x, y)
        self._cached_properties = None

    def right_click(self, x_offset=0, y_offset=0):
        x, y, w, h = self.acc_location
        x += x_offset if x_offset is not None else w / 2
        y += y_offset if y_offset is not None else h / 2

        self._mouse.click(x, y, self._mouse.RIGHT_BUTTON)
        self._cached_properties = None

    def double_click(self, x_offset=0, y_offset=0, click_interval=0.5):
        x, y, w, h = self.acc_location
        x += x_offset if x_offset is not None else w / 2
        y += y_offset if y_offset is not None else h / 2

        self._mouse.double_click(x, y, click_interval=click_interval)
        self._cached_properties = None

    def drag_to(self, x, y, x_offset=None, y_offset=None, smooth=True):
        el_x, el_y, el_w, el_h = self.acc_location
        el_x += x_offset if x_offset is not None else el_w / 2
        el_y += y_offset if y_offset is not None else el_h / 2

        self._mouse.drag(el_x, el_y, x, y, smooth)
        self._cached_properties = None

    @property
    def proc_id(self):
        return self._proc_id

    @property
    def is_top_level_window(self):
        return self._properties.get('AXParent', 'false') == 'false'

    @property
    def is_selected(self):
        result = False
        if self.acc_role_name == self._acc_role_name_map['AXRadioButton'] and \
                self._properties.get('AXValue', 'false') == 'true':
            result = True

        return result

    @property
    def is_checked(self):
        result = False
        if self.acc_role_name == self._acc_role_name_map['AXCheckBox'] and \
                self._properties.get('AXValue', 'false') == 'true':
            result = True

        return result

    @property
    def is_visible(self):
        return True  # We can't work with invisible elements under Mac OS.

    @property
    def is_enabled(self):
        return bool(self._properties.get('AXEnabled', False))

    @property
    def acc_parent_count(self):
        return 0

    @property
    def acc_child_count(self):
        return len(self._properties.get('AXChildren'))

    @property
    def acc_name(self):
        result = self._properties.get('AXDescription') or \
            self._properties.get('AXTitle') or \
            self._properties.get('AXValue')

        return MacUtils.replace_inappropriate_symbols(result or '')

    def set_focus(self):
        # TODO:
        MacUtils.ApplescriptExecutor.set_element_attribute_value(
            self._object_selector, 'AXFocused', 'true', self._proc_name, False)

    @property
    def acc_c_name(self):
        return self.acc_role_name + self.acc_name if self.acc_name else ''

    @property
    def acc_location(self):
        x, y = self._element.AXPosition
        w, h = self._element.AXSize

        return map(int, [x, y, w, h])

    @property
    def acc_value(self):
        return self._properties.get('AXValue', None)

    def set_value(self, value):
        # TODO:
        MacUtils.ApplescriptExecutor.set_element_attribute_value(
            self._object_selector, 'AXValue', value, self._proc_name)
        self._cached_properties = None

    @property
    def acc_description(self):
        return self._properties.get('AXDescription', None)

    @property
    def acc_parent(self):
        result = None
        if self.acc_parent_count > 0:
            result = \
                MacElement(self._element.AXParent,
                           self._proc_name,
                           self._proc_id)

        return result

    @property
    def acc_selection(self):
        return self._properties.get('AXSelectedText', None)

    @property
    def acc_focused_element(self):
        childs = self.findall()

        result = None
        for element in childs:
            if self._properties.get('AXFocused', 'false') == 'true':
                result = element
                break

        return result

    @property
    def acc_role_name(self):
        return self._acc_role_name_map.get(self._role, 'unknown')

    def __iter__(self):
        children_elements = self._properties.get('AXChildren', [])

        # children = children_elements[0]

        if not len(children_elements):
            raise StopIteration()

        for element in children_elements:
            yield MacElement(element.AXChildren,
                             self._proc_name, self.proc_id)

    def __findcacheiter(self, only_visible, **kwargs):
        """
        Find child element in the cache.

        Arguments:
            - only_visible: bool, flag that indicates will we search only

        Returns:
            - Yield found element.
        """

        for obj_element in self._cached_children:
            if obj_element._match(only_visible, **kwargs):
                yield obj_element

    def _finditer(self, only_visible, **kwargs):
        """
        Find child element.

        Arguments:
            - only_visible: bool, flag that indicates will we search only

        Returns:
            - Yield found element.
        """

        lst_queue = list(self)

        if self.is_top_level_window:
            lst_queue.extend(self._find_windows_by_same_proc())

        while lst_queue:
            obj_element = lst_queue.pop(0)
            self._cached_children.add(obj_element)

            if obj_element._match(only_visible, **kwargs):
                yield obj_element

            if obj_element.acc_child_count:
                childs = [el for el in list(obj_element)]
                lst_queue[:0] = childs

    def find(self, **kwargs):
        result = self._element.findFirstR(**kwargs)

        if not result:
            attrs = ['%s=%s' % (k, v) for k, v in kwargs.iteritems()]
            raise TooSaltyUISoupException(
                'Can\'t find object with attributes "%s".' %
                '; '.join(attrs))
        return MacElement(result, self._proc_name, self.proc_id)

    def findall(self, only_visible=True, **kwargs):
        result = self._element.findAllR(**kwargs)

        if not result:
            attrs = ['%s=%s' % (k, v) for k, v in kwargs.iteritems()]
            raise TooSaltyUISoupException(
                'Can\'t find object with attributes "%s".' %
                '; '.join(attrs))
        return MacElement(result, self._proc_name, self.proc_id)

    def is_object_exists(self, **kwargs):
        try:
            self.find(**kwargs)
            return True
        except TooSaltyUISoupException:
            return False
