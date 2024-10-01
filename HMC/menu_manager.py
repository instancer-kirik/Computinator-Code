from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction

from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction
from .action_handlers import ActionHandlers

from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction
from .action_handlers import ActionHandlers

import logging
from PyQt6.QtCore import QObject

class MenuManager:
    def __init__(self, main_window, cccore):
        self.main_window = main_window
        self.cccore = cccore
        self.action_handlers = ActionHandlers(main_window)

    def create_menu_bar(self):
        menubar = QMenuBar(self.main_window)
        
        menus = {
            "File": self.create_file_menu(),
            "Edit": self.create_edit_menu(),
            "View": self.create_view_menu(),
            "Tools": self.create_tools_menu(),
            "Vault": self.create_vault_menu(),
            "Workspace": self.create_workspace_menu(),
            "Help": self.create_help_menu()
        }

        for menu_name, menu in menus.items():
            menubar.addMenu(menu)

        return menubar

    def create_file_menu(self):
        file_menu = QMenu("&File", self.main_window)
        file_menu.addAction("New", self.action_handlers.new_file)
        file_menu.addAction("Open", self.action_handlers.open_file)
        file_menu.addAction("Save", self.action_handlers.save_file)
        file_menu.addAction("Save As", self.action_handlers.save_file_as)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.main_window.close)
        return file_menu

    def create_edit_menu(self):
        edit_menu = QMenu("&Edit", self.main_window)
        edit_menu.addAction("Undo", self.action_handlers.undo)
        edit_menu.addAction("Redo", self.action_handlers.redo)
        edit_menu.addSeparator()
        edit_menu.addAction("Cut", self.action_handlers.cut_document)
        edit_menu.addAction("Copy", self.action_handlers.copy_document)
        edit_menu.addAction("Paste", self.action_handlers.paste_document)
        edit_menu.addAction("Theme Builder", self.main_window.widget_manager.show_theme_builder)
        return edit_menu

    def create_view_menu(self):
        view_menu = QMenu("View", self.main_window)
        for dock_name, dock_widget in self.cccore.widget_manager.dock_widgets.items():
            action = view_menu.addAction(dock_name)
            action.setCheckable(True)
            try:
                if dock_widget and isinstance(dock_widget, QObject):
                    parent = dock_widget.parent()
                    is_visible = dock_widget.isVisible()
                    action.setChecked(is_visible)
                    action.triggered.connect(lambda checked, w=dock_widget: self.toggle_dock_visibility(w, checked))
                else:
                    action.setEnabled(False)
                    logging.warning(f"Dock widget '{dock_name}' is not a valid QObject.")
            except RuntimeError:
                action.setEnabled(False)
                logging.warning(f"Dock widget '{dock_name}' has been deleted or is invalid.")
            except Exception as e:
                action.setEnabled(False)
                logging.error(f"Unexpected error with dock widget '{dock_name}': {str(e)}")
        return view_menu

    def toggle_dock_visibility(self, dock_widget, checked):
        try:
            dock_widget.setVisible(checked)
        except RuntimeError:
            logging.warning(f"Failed to set visibility for a dock widget. It may have been deleted.")
        except Exception as e:
            logging.error(f"Unexpected error toggling dock visibility: {str(e)}")

    def create_tools_menu(self):
        tools_menu = QMenu("&Tools", self.main_window)
        actions = [
            ("Plugin Manager", self.action_handlers.show_plugin_manager),
            ("Settings", self.action_handlers.show_settings),
            ("Theme Manager", self.action_handlers.show_theme_manager),
            ("Workspace Manager", self.action_handlers.show_workspace_manager),
            ("Model Manager", self.action_handlers.show_model_manager),
            ("Download Manager", self.action_handlers.show_download_manager),
            ("Load Layout", self.action_handlers.load_layout)
        ]
        
        for action_name, handler in actions:
            action = tools_menu.addAction(action_name)
            if callable(handler):
                action.triggered.connect(handler)
                logging.debug(f"Connected {action_name} to {handler.__name__}")
            else:
                logging.error(f"Handler for {action_name} is not callable")
        
        return tools_menu
    def create_vault_menu(self):
        vault_menu = QMenu("&Vault", self.main_window)
        vault_menu.addAction("Add Vault Directory", self.action_handlers.add_vault_directory)
        vault_menu.addAction("Remove Vault Directory", self.action_handlers.remove_vault_directory)
        vault_menu.addAction("Set Default Vault", self.action_handlers.set_default_vault)
        return vault_menu

    def create_workspace_menu(self):
        workspace_menu = QMenu("&Workspace", self.main_window)
        workspace_menu.addAction("Create Workspace", self.main_window.create_workspace)
        workspace_menu.addAction("Switch Workspace", self.main_window.switch_workspace)
        return workspace_menu

    def create_help_menu(self):
        help_menu = QMenu("&Help", self.main_window)
        help_menu.addAction("About", self.action_handlers.show_about)
        return help_menu

    def add_toggle_view_action(self, menu, title, dock_widget):
        if dock_widget is None:
            logging.warning(f"Cannot add toggle view action for '{title}' as the dock widget is None")
            return
        
        action = QAction(title, self.main_window, checkable=True)
        action.setChecked(dock_widget.isVisible())
        action.triggered.connect(dock_widget.setVisible)
        dock_widget.visibilityChanged.connect(action.setChecked)
        menu.addAction(action)
