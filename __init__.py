from calibre.customize import InterfaceActionBase

class QuickSwitchLibraryPluginInterface(InterfaceActionBase):
    name = 'Quick Switch Library Plugin'
    author = 'Andrea Bisognin'
    version = (1,0,0)
    supported_platforms = ['windows','osx','linux']
   
    actual_plugin = 'calibre_plugins.quick_switch_library.ui:QuickSwitchLibraryPlugin'

    def is_customizable(self):
        return False

    
