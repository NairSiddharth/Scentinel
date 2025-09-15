#!/usr/bin/env python3
from nicegui import ui
from scentinel.database import Database, Cologne, WearHistory
from scentinel.tabs.settings_tab import SettingsTab
from scentinel.tabs.collection_tab import CollectionTab
from scentinel.tabs.analytics_tab import AnalyticsTab
from scentinel.tabs.welcome_tab import WelcomeTab
from datetime import datetime, timedelta
from typing import List, Optional, Any, Dict

class ScentinelApp:
    def navigate_to_tab(self, tab_name: str):
        """Navigate to a specific tab and ensure content is shown"""
        ui.run_javascript(f'window.location.hash = "{tab_name}";')
        if self.hidden_tabs:
            self.hidden_tabs.value = tab_name
            self.on_tab_change(tab_name)

    def show_add_cologne_dialog(self, *args, **kwargs):
        """Delegate to CollectionTab's dialog"""
        if hasattr(self, 'collection_tab') and hasattr(self.collection_tab, 'show_add_cologne_dialog'):
            self.collection_tab.show_add_cologne_dialog()

    def show_log_wear_dialog(self, *args, **kwargs):
        """Delegate to CollectionTab's dialog"""
        if hasattr(self, 'collection_tab') and hasattr(self.collection_tab, 'show_log_wear_dialog'):
            self.collection_tab.show_log_wear_dialog()


    def toggle_dark_mode(self):
        """Toggle dark mode and update UI"""
        self.dark_mode = not self.dark_mode
        # Update body class
        mode = 'dark-mode' if self.dark_mode else 'light-mode'
        ui.run_javascript(f'''
            document.body.classList.remove('dark-mode', 'light-mode');
            document.body.classList.add('{mode}');
        ''')
        # Update header gradient
        if self.header_container:
            if self.dark_mode:
                self.header_container.classes(remove='header-gradient-light', add='header-gradient-dark')
            else:
                self.header_container.classes(remove='header-gradient-dark', add='header-gradient-light')
        # Update footer gradient
        if self.footer_container:
            if self.dark_mode:
                self.footer_container.classes(remove='footer-gradient-light', add='footer-gradient-dark')
            else:
                self.footer_container.classes(remove='footer-gradient-dark', add='footer-gradient-light')
        ui.notify(f'Switched to {"dark" if self.dark_mode else "light"} mode', type='info')

    def __init__(self):
        self.db = Database()

        # Initialize modular tabs
        self.settings_tab = SettingsTab(self.db)
        self.collection_tab = CollectionTab(self.db, self.settings_tab)
        self.analytics_tab = AnalyticsTab(self.db)
        self.welcome_tab = WelcomeTab(self)

        # Set up data change callbacks
        self.settings_tab.set_data_change_callback(self.on_data_changed)
        self.collection_tab.set_data_change_callback(self.on_data_changed)

        # UI containers
        self.header_container = None
        self.footer_container = None
        self.nav_buttons = {}
        self.hidden_tabs = None

        # Accessibility settings
        self.dark_mode = False
        self.font_size = 'medium'  # small, medium, large, extra-large
        self.high_contrast = False
        self.reduced_motion = False

    def on_data_changed(self):
        """Called when data changes - refresh UI components"""
        if hasattr(self, 'collection_tab'):
            self.collection_tab.refresh_data()
        if hasattr(self, 'analytics_tab'):
            self.analytics_tab.refresh_data()

    def setup_ui(self):
        """Set up the main UI, navigation, and tab panels using modular tab classes."""
        ui.page_title('Scentinel - Cologne Tracker')
        ui.add_head_html('''
        <style>
            :root {
                --header-light: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                --header-dark: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
                --footer-light: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
                --footer-dark: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
            }
            .nav-active {
                background: #ffffff40 !important;
                color: #ffffff !important;
                font-weight: 600 !important;
                border: 1px solid #ffffff60 !important;
            }
            .nav-inactive {
                background: transparent !important;
                color: #ffffffb3 !important;
                border: 1px solid transparent !important;
            }
            .nav-inactive:hover {
                background: #ffffff20 !important;
                color: #ffffff !important;
                border: 1px solid #ffffff40 !important;
            }
            .header-gradient-light { background: var(--header-light); }
            .header-gradient-dark { background: var(--header-dark); }
            .footer-gradient-light { background: var(--footer-light); }
            .footer-gradient-dark { background: var(--footer-dark); }
            .glass-card {
                background: #ffffffcc;
                border: 1px solid #ffffff33;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .glass-card-dark {
                background: #1f2937cc;
                border: 1px solid #4b556350;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }
            .smooth-transition {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .hover-lift:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            }
            body.dark-mode {
                background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
                min-height: 100vh;
            }
            body.light-mode {
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                min-height: 100vh;
            }
            /* Accessibility Features */
            .font-small { font-size: 0.875rem; }
            .font-medium { font-size: 1rem; }
            .font-large { font-size: 1.125rem; }
            .font-extra-large { font-size: 1.25rem; }
            .high-contrast {
                filter: contrast(150%) brightness(1.2);
            }
            .reduced-motion * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
            .footer-btn {
                background: #ffffff20 !important;
                transition: background 0.2s ease;
            }
            .footer-btn:hover {
                background: #ffffff30 !important;
            }
            .accessibility-menu {
                position: fixed;
                bottom: 80px; /* Above footer height + padding */
                right: 20px;
                z-index: 1000;
            }
        </style>
        ''')
        # Set up dark mode and tab restore logic
        ui.add_head_html('''
        <script>
        document.addEventListener("DOMContentLoaded", function() {
            document.body.className = "light-mode";
            // Hybrid tab restore: open last tab or default to home
            let lastTab = localStorage.getItem('scentinel_last_tab');
            let hash = window.location.hash.replace('#', '');

            // If no hash in URL, restore from localStorage or default to home
            if (!hash || hash === '') {
                if (lastTab && lastTab !== '' && lastTab !== 'home') {
                    // Returning user - restore their last tab
                    window.location.hash = lastTab;
                } else {
                    // First time visitor or returning to home - default to home
                    localStorage.setItem('scentinel_last_tab', 'home');
                    window.location.hash = '';
                    // Ensure home tab is visible
                    setTimeout(() => {
                        const homeTab = document.querySelector('[data-tab="home"]');
                        if (homeTab) homeTab.click();
                    }, 100);
                }
            }
        });
        // Save tab on hash change
        window.addEventListener('hashchange', function() {
            let tab = window.location.hash.replace('#', '');
            // Save tab to localStorage (empty hash = home)
            localStorage.setItem('scentinel_last_tab', tab || 'home');
        });
        </script>
        ''')

        self.nav_buttons = {}
        self.header_container = ui.header(elevated=True).classes('header-gradient-light smooth-transition px-6 py-3')
        with self.header_container:
            with ui.row().classes('w-full items-center justify-between'):
                # Left: Logo
                with ui.row().classes('items-center gap-3 cursor-pointer').on('click', lambda: self.navigate_to_home()):
                    ui.image('data/images/cologne.png').classes('w-8 h-8 drop-shadow-sm')
                    ui.label('Scentinel').classes('text-2xl font-bold text-white tracking-wide drop-shadow-sm')

                # Center: Navigation Tabs
                with ui.row().classes('items-center gap-2'):
                    nav_items = [
                        ('collection', 'Collection', 'inventory_2'),
                        ('analytics', 'Analytics', 'analytics'),
                        ('settings', 'Settings', 'settings')
                    ]
                    for tab_id, tab_name, tab_icon in nav_items:
                        btn = ui.button('', on_click=(lambda tab=tab_id: lambda *_: self.navigate_to_tab(tab))()).props('flat')
                        with btn:
                            with ui.row().classes('items-center gap-2'):
                                ui.icon(tab_icon).classes('text-xl')
                                ui.label(tab_name).classes('font-medium')
                        self.nav_buttons[tab_id] = btn
                        btn.classes('px-4 py-2 rounded-lg smooth-transition nav-inactive')

                # Right: Quick Actions Menu
                with ui.button(icon='add', on_click=lambda: None).classes(
                    'text-white font-medium px-4 py-2 rounded-lg smooth-transition hover-lift'
                ).style('background: #ffffff30; border: 1px solid #ffffff50;').props('flat'):
                    ui.label('Quick Actions').classes('ml-2')
                    with ui.menu().props('auto-close'):
                        ui.menu_item('Add Cologne', on_click=self.show_add_cologne_dialog).props('icon=add')
                        ui.menu_item('Log Wear', on_click=self.show_log_wear_dialog).props('icon=event_note')
                        ui.separator()
                        ui.menu_item('Export Data', on_click=lambda: self.settings_tab.export_collection()).props('icon=download')
                        ui.menu_item('Import Data', on_click=lambda: self.settings_tab.show_import_dialog()).props('icon=upload')

        # Hidden tabs for routing
        with ui.element('div').classes('hidden'):
            def home_alias_mapper(x):
                val = x.split('#')[-1]
                if val in ('', 'home'):
                    return 'home'
                return val
            with ui.tabs().bind_value_from(ui.context.client, 'url_hash', home_alias_mapper) as tabs:
                self.hidden_tabs = tabs
                tabs.value = 'home'  # Set initial value to home
            tabs.on_value_change(self.on_tab_change)

        # Main tab panels
        self.main_container = ui.tab_panels(self.hidden_tabs).classes('w-full min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 smooth-transition main-tab-container')
        with self.main_container:
            with ui.tab_panel('home').classes('p-0'):
                self.welcome_tab.setup_tab_content()
            with ui.tab_panel('collection').classes('p-0'):
                collection_container = ui.column().classes('w-full')
                self.collection_tab.setup_tab_content(collection_container)
            with ui.tab_panel('analytics').classes('p-0'):
                analytics_container = ui.column().classes('w-full')
                self.analytics_tab.setup_tab_content(analytics_container)
            with ui.tab_panel('settings').classes('p-0'):
                settings_container = ui.column().classes('w-full')
                self.settings_tab.setup_tab_content(settings_container)

        self.setup_footer()
        self.setup_accessibility_menu()

    def navigate_to_home(self):
        """Navigate to home/welcome page (now a tab panel)"""
        # Clear localStorage and remove hash for clean home state
        ui.run_javascript('localStorage.setItem("scentinel_last_tab", "home");')
        ui.run_javascript('history.replaceState(null, null, window.location.pathname + window.location.search);')
        if self.hidden_tabs:
            self.hidden_tabs.value = 'home'
            self.on_tab_change('home')

    def on_tab_change(self, event):
        """Handle tab change event and refresh tab content"""
        tab_value = event.value if hasattr(event, 'value') else event
        self.update_nav_active_state(tab_value)

        # Refresh tab content when switching
        if tab_value == 'collection' and hasattr(self, 'collection_tab'):
            self.collection_tab.refresh_data()
        elif tab_value == 'analytics' and hasattr(self, 'analytics_tab'):
            self.analytics_tab.refresh_data()
        elif tab_value == 'settings' and hasattr(self, 'settings_tab'):
            self.settings_tab.refresh_data()

    def update_nav_active_state(self, active_tab):
        """Update navigation button states to show active tab"""
        if not hasattr(self, 'nav_buttons'):
            return

        for tab_id, button in self.nav_buttons.items():
            if tab_id == active_tab:
                button.classes(remove='nav-inactive', add='nav-active')
            else:
                button.classes(remove='nav-active', add='nav-inactive')

    def setup_footer(self):
        """Setup footer with gradient styling, full width, and useful app info/actions."""
        APP_VERSION = "v1.0.0"  # Update as needed or load dynamically
        self.footer_container = ui.element('footer').classes(
            'footer-gradient-light smooth-transition w-full fixed bottom-0 left-0 right-0 py-4 px-6 z-50'
        )
        with self.footer_container:
            with ui.row().classes('max-w-7xl mx-auto w-full items-center justify-between'):
                # Left: Logo, app name, version, privacy
                with ui.row().classes('items-center gap-3'):
                    ui.image('data/images/cologne.png').classes('w-4 h-4 opacity-90')
                    ui.label('Scentinel').classes('text-white text-base font-semibold opacity-90')
                    ui.label(APP_VERSION).classes('text-white text-xs opacity-60 ml-2')
                    ui.label('• All data stored locally').classes('text-white text-xs opacity-60 ml-2')
                # Center: Quick actions
                with ui.row().classes('gap-3'):
                    ui.button('Export Data', on_click=lambda: self.settings_tab.export_collection()).props('flat').classes('text-white text-xs rounded-md px-3 py-1 footer-btn')
                    ui.button('Import Data', on_click=lambda: self.settings_tab.show_import_dialog()).props('flat').classes('text-white text-xs rounded-md px-3 py-1 footer-btn')
                # Right: Help, feedback, credits
                with ui.row().classes('items-center gap-2'):
                    ui.button('Help', on_click=lambda: self.navigate_to_tab('settings')).props('flat').classes('text-white text-xs rounded-md px-3 py-1 footer-btn')
                    ui.button('Send Feedback', on_click=lambda: ui.notify('Send feedback to: your@email.com')).props('flat').classes('text-white text-xs rounded-md px-3 py-1 footer-btn')
                    ui.label('Made with ❤️ using NiceGUI').classes('text-white text-xs opacity-75 ml-2')

    def setup_accessibility_menu(self):
        """Setup floating accessibility menu in bottom right corner"""
        with ui.element('div').classes('accessibility-menu'):
            with ui.button(icon='accessibility', on_click=lambda: None).classes(
                'bg-blue-600 hover:bg-blue-700 text-white rounded-full p-3 shadow-lg hover:shadow-xl smooth-transition'
            ).props('flat'):
                with ui.menu().props():
                    with ui.menu_item('Dark Mode').props('icon=dark_mode'):
                        with ui.item_section().props('side'):
                            ui.switch(value=self.dark_mode, on_change=lambda: self.toggle_dark_mode())
                    ui.separator()

                    # Font Size submenu
                    with ui.menu_item('Font Size', auto_close=False).props('icon=text_fields'):
                        with ui.item_section().props('side'):
                            ui.icon('keyboard_arrow_left')
                        with ui.menu().props('anchor="top end" self="top start" auto-close'):
                            ui.menu_item('Small', on_click=lambda: self.set_font_size('small')).props('icon=text_decrease')
                            ui.menu_item('Medium', on_click=lambda: self.set_font_size('medium')).props('icon=text_fields')
                            ui.menu_item('Large', on_click=lambda: self.set_font_size('large')).props('icon=text_increase')
                            ui.menu_item('Extra Large', on_click=lambda: self.set_font_size('extra-large')).props('icon=zoom_in')

                    # Contrast submenu
                    with ui.menu_item('Contrast', auto_close=False).props('icon=contrast'):
                        with ui.item_section().props('side'):
                            ui.icon('keyboard_arrow_left')
                        with ui.menu().props('anchor="top end" self="top start" auto-close'):
                            ui.menu_item('Normal Contrast', on_click=lambda: self.set_contrast_mode('normal')).props('icon=visibility')
                            ui.menu_item('High Contrast', on_click=lambda: self.set_contrast_mode('high')).props('icon=contrast')

                    # Motion submenu
                    with ui.menu_item('Motion', auto_close=False).props('icon=motion_photos_on'):
                        with ui.item_section().props('side'):
                            ui.icon('keyboard_arrow_left')
                        with ui.menu().props('anchor="top end" self="top start" auto-close'):
                            ui.menu_item('Normal Motion', on_click=lambda: self.set_motion_mode('normal')).props('icon=motion_photos_on')
                            ui.menu_item('Reduced Motion', on_click=lambda: self.set_motion_mode('reduced')).props('icon=motion_photos_off')

                    ui.separator()
                    ui.menu_item('Reset All', on_click=self.reset_accessibility).props('icon=refresh')


    def set_font_size(self, size: str):
        """Set the application font size"""
        self.font_size = size
        # Remove existing font classes
        ui.run_javascript('''
            document.body.classList.remove('font-small', 'font-medium', 'font-large', 'font-extra-large');
        ''')
        # Add new font class
        ui.run_javascript(f'document.body.classList.add("font-{size}");')
        ui.notify(f'Font size set to {size.replace("-", " ")}', type='info')

    def set_contrast_mode(self, mode: str):
        """Set the application contrast mode"""
        if mode == 'normal':
            self.high_contrast = False
            ui.run_javascript('document.body.classList.remove("high-contrast");')
            ui.notify('Normal contrast enabled', type='info')
        elif mode == 'high':
            self.high_contrast = True
            ui.run_javascript('document.body.classList.add("high-contrast");')
            ui.notify('High contrast enabled', type='info')

    def set_motion_mode(self, mode: str):
        """Set the application motion mode"""
        if mode == 'normal':
            self.reduced_motion = False
            ui.run_javascript('document.body.classList.remove("reduced-motion");')
            ui.notify('Normal motion enabled', type='info')
        elif mode == 'reduced':
            self.reduced_motion = True
            ui.run_javascript('document.body.classList.add("reduced-motion");')
            ui.notify('Reduced motion enabled', type='info')


    def reset_accessibility(self):
        """Reset all accessibility settings to defaults"""
        self.dark_mode = False
        self.font_size = 'medium'
        self.high_contrast = False
        self.reduced_motion = False

        ui.run_javascript('''
            document.body.className = "light-mode font-medium";
        ''')

        # Update header gradient back to light using class manipulation
        if self.header_container:
            self.header_container.classes(remove='header-gradient-dark', add='header-gradient-light')

        # Update footer gradient back to light
        if self.footer_container:
            self.footer_container.classes(remove='footer-gradient-dark', add='footer-gradient-light')

        ui.notify('All accessibility settings reset to defaults', type='positive')

def main():
    app_instance = ScentinelApp()
    app_instance.setup_ui()
    ui.run(title='Scentinel', reload=False, native=True, favicon='data/images/cologne.png', show_welcome_message=False, window_size=(1200, 800)) 

if __name__ in {"__main__", "__mp_main__"}:
    main()