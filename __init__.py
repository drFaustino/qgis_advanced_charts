# __init__.py

def classFactory(iface):
    from .advanced_charts_plugin import AdvancedChartsPlugin
    return AdvancedChartsPlugin(iface)
