PYQT_VERSION = 5
# Compatibility workaround: Older versions of Qonda
# ignored "errors should never pass silently" principle
# because callbacks could be fired during __init__ when object
# state is not fully built and attributes could be missing.
# Newer Qonda raises AttributeError, unless
# IGNORE_ATTRIBUTE_ERRORS_ON_CALLBACKS is set to True
IGNORE_ATTRIBUTE_ERRORS_ON_CALLBACKS = False