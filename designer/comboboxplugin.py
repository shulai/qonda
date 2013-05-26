

from PyQt4.QtDesigner import QPyDesignerCustomWidgetPlugin
from qonda.widgets import ComboBox


class ComboBoxPlugin(QPyDesignerCustomWidgetPlugin):

    def __init__(self, parent=None):

        QPyDesignerCustomWidgetPlugin.__init__(self)
        self.initialized = False

    def initialize(self, formEditor):

        if self.initialized:
            return
        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def createWidget(self, parent):
        return ComboBox(parent)

    def name(self):
        return "ComboBox"

    def group(self):
        return "Qonda widgets"

    #def icon(self):
        #return QtGui.QIcon(_logo_pixmap)

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    # Returns True if the custom widget acts as a container for other widgets;
    # otherwise returns False. Note that plugins for custom containers also
    # need to provide an implementation of the QDesignerContainerExtension
    # interface if they need to add custom editing support to Qt Designer.
    def isContainer(self):
        return False

    # Returns an XML description of a custom widget instance that describes
    # default values for its properties. Each custom widget created by this
    # plugin will be configured using this description.
    def domXml(self):
        return (
            '<widget class="ComboBox" name="comboBox">\n'
            '  <property name="allowEmpty">\n'
            '    <bool>True</bool>\n'
            '  </property>\n'
            '</widget>')

    # Returns the module containing the custom widget class. It may include
    # a module path.
    def includeFile(self):
        return "qonda.widgets"
