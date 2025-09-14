#!/usr/bin/env python3
from nicegui import ui
from .database import Database, Cologne, WearHistory
from datetime import datetime, timedelta
from typing import List, Optional, Any
import csv
import io
import plotly.express as px
import plotly.graph_objects as go


# ...existing code...

class ScentinelApp:


    def navigate_to_home(self):
        """Navigate to home/welcome page (now a tab panel)"""
        # Remove hash completely for a blank URL
        ui.run_javascript('history.replaceState(null, null, window.location.pathname + window.location.search);')
        if hasattr(self, 'hidden_tabs'):
            self.hidden_tabs.value = 'home'
            self.on_tab_change('home')

    def on_tab_change(self, event):
        """Handle tab change event and refresh tab content"""
        tab_value = event.value if hasattr(event, 'value') else event
        self.update_nav_active_state(tab_value)
        if hasattr(self, 'collection_tab_container') and tab_value == 'collection':
            self.collection_tab_container.clear()
            self.setup_collection_tab()
        elif hasattr(self, 'analytics_tab_container') and tab_value == 'analytics':
            self.analytics_tab_container.clear()
            self.setup_analytics_tab()
        elif hasattr(self, 'settings_tab_container') and tab_value == 'settings':
            self.settings_tab_container.clear()
            self.setup_settings_tab()

    def update_nav_active_state(self, active_tab: str):
        """Update the visual state of navigation buttons"""
        for tab_id, button in self.nav_buttons.items():
            if tab_id == active_tab:
                button.classes(remove='text-white/70 nav-inactive', add='text-white nav-active')
            else:
                button.classes(remove='text-white nav-active', add='text-white/70 nav-inactive')
    def __init__(self):
        self.db = Database()
        self.cologne_table = None
        self.recent_wears_container: Optional[Any] = None
        self.recommendation_card: Optional[Any] = None
        self.search_input: Optional[Any] = None
        self.cologne_table_container: Optional[Any] = None
        self.dark_mode = False
        self.header_container: Optional[Any] = None
        self.main_container: Optional[Any] = None
        self.footer_container: Optional[Any] = None

    def setup_ui(self):
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
        background: rgba(255, 255, 255, 0.25) !important;
        color: white !important;
        font-weight: 600 !important;
    }
    .nav-inactive:hover {
                        with ui.tabs().bind_value_from(ui.context.client, 'url_hash', lambda x: (x.split('#')[-1] if x.split('#')[-1] else 'home')) as tabs:
                            self.hidden_tabs = tabs
                        tabs.on_value_change(self.on_tab_change)
        --ag-font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        --ag-font-size: 14px;
        --ag-header-height: 48px;
        --ag-row-height: 42px;
        --ag-border-radius: 8px;
        --ag-header-background-color: #f8fafc;
        --ag-header-foreground-color: #374151;
        --ag-odd-row-background-color: #ffffff;
        --ag-even-row-background-color: #f9fafb;
        --ag-row-hover-color: #e0e7ff;
        --ag-selected-row-background-color: #dbeafe;
        --ag-border-color: #e5e7eb;
    }
    .dark .ag-theme-alpine {
        --ag-header-background-color: #374151;
        --ag-header-foreground-color: #f3f4f6;
        --ag-odd-row-background-color: #1f2937;
        --ag-even-row-background-color: #111827;
        --ag-row-hover-color: #374151;
        --ag-selected-row-background-color: #1e40af;
        --ag-border-color: #4b5563;
        --ag-foreground-color: #f3f4f6;
        --ag-background-color: #1f2937;
    }
    .header-gradient-light {
        background: var(--header-light);
    }
    .header-gradient-dark {
        background: var(--header-dark);
    }
    .footer-gradient-light {
        background: var(--footer-light);
    }
    .footer-gradient-dark {
        background: var(--footer-dark);
    }
    .glass-card {
        backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .glass-card-dark {
        backdrop-filter: blur(10px);
        background: rgba(31, 41, 55, 0.8);
        border: 1px solid rgba(75, 85, 99, 0.3);
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
    /* Slide animation for continuity between home and tabs */
    .slide-anim {
        position: relative;
        left: 100vw;
        opacity: 0;
        transition: left 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 2;
    }
    .slide-anim.show {
        left: 0;
        opacity: 1;
    }
    .slide-anim.hide {
        left: -100vw;
        opacity: 0;
    }
</style>
''')
        ui.add_head_html('<script>document.addEventListener("DOMContentLoaded", function() { document.body.className = "light-mode"; });</script>')
        self.nav_buttons = {}
        self.header_container = ui.header(elevated=True).classes('header-gradient-light smooth-transition items-center justify-between px-6 py-3')
        with self.header_container:
            with ui.row().classes('items-center gap-6'):
                with ui.row().classes('items-center gap-3 cursor-pointer').on('click', lambda: self.navigate_to_home()):
                    ui.image('data/images/cologne.png').classes('w-8 h-8 drop-shadow-sm')
                    ui.label('Scentinel').classes('text-2xl font-bold text-white tracking-wide drop-shadow-sm')
                ui.element('div').classes('w-px h-8 bg-white/30')
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
                        btn.classes('text-white/70 px-4 py-2 rounded-lg smooth-transition nav-inactive')
            with ui.row().classes('items-center gap-3'):
                ui.button('Add Cologne', on_click=self.show_add_cologne_dialog).classes('bg-white bg-opacity-20 hover:bg-opacity-30 text-white font-medium px-4 py-2 rounded-lg backdrop-blur-sm border border-white border-opacity-30 smooth-transition hover-lift').props('flat icon=add')
                ui.button('Log Wear', on_click=self.show_log_wear_dialog).classes('bg-white bg-opacity-20 hover:bg-opacity-30 text-white font-medium px-4 py-2 rounded-lg backdrop-blur-sm border border-white border-opacity-30 smooth-transition hover-lift').props('flat icon=event_note')
                with ui.row().classes('items-center gap-2 ml-4'):
                    ui.icon('light_mode').classes('text-white text-xl')
                    self.dark_mode_toggle = ui.switch('', value=self.dark_mode, on_change=self.toggle_dark_mode)
                    ui.icon('dark_mode').classes('text-white text-xl')
        with ui.element('div').classes('hidden'):
            # Treat '', '#', and 'home' as the home tab; otherwise use the hash value
            def home_alias_mapper(x):
                val = x.split('#')[-1]
                if val in ('', 'home'):
                    return 'home'
                return val
            with ui.tabs().bind_value_from(ui.context.client, 'url_hash', home_alias_mapper) as tabs:
                self.hidden_tabs = tabs
            tabs.on_value_change(self.on_tab_change)
        self.main_container = ui.tab_panels(self.hidden_tabs).classes('w-full min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 smooth-transition main-tab-container')
        with self.main_container:
            with ui.tab_panel('home').classes('p-0'):
                self.setup_welcome_landing_page()
            with ui.tab_panel('collection').classes('p-0'):
                self.collection_tab_container = ui.column().classes('w-full')
                self.setup_collection_tab()
            with ui.tab_panel('analytics').classes('p-0'):
                self.analytics_tab_container = ui.column().classes('w-full')
                self.setup_analytics_tab()
            with ui.tab_panel('settings').classes('p-0'):
                self.settings_tab_container = ui.column().classes('w-full')
                self.setup_settings_tab()
        self.setup_footer()



    # Removed setup_welcome_logic and check_initial_hash; welcome is now a tab panel

    def setup_welcome_landing_page(self):
        """Setup the welcome landing page for new users"""
        with ui.column().classes('w-full min-h-screen'):
            # Hero Section
            with ui.element('section').classes(
                'w-full bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 '
                'text-white py-20 px-6 text-center relative overflow-hidden'
            ):
                # Background pattern overlay
                ui.add_head_html('''
                <style>
                    .hero-pattern::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
                        pointer-events: none;
                    }
                </style>
                ''')

                with ui.column().classes('max-w-4xl mx-auto relative z-10 items-center'):
                    # Logo and title - perfectly centered
                    with ui.row().classes('items-center gap-4 mb-8'):
                        ui.image('data/images/cologne.png').classes('w-16 h-16 drop-shadow-2xl')
                        ui.label('Scentinel').classes(
                            'text-6xl font-bold tracking-tight drop-shadow-lg'
                        )

                    # Main tagline - centered
                    ui.label('Your Intelligent Fragrance Companion').classes(
                        'text-3xl font-light mb-6 opacity-95'
                    )

                    # Subtitle - centered with better spacing
                    ui.label('Track, analyze, and discover your perfect scent rotation with AI-powered insights').classes(
                        'text-xl text-blue-100 mb-12 max-w-3xl leading-relaxed'
                    )

                    # Primary CTA buttons
                    with ui.row().classes('gap-6'):
                        ui.button(
                            'Start Your Fragrance Journey',
                            on_click=lambda: self.navigate_to_tab('collection')
                        ).classes(
                            'bg-white text-purple-600 hover:bg-gray-100 font-semibold px-8 py-4 '
                            'rounded-xl shadow-xl hover:shadow-2xl smooth-transition hover-lift text-lg'
                        )

                        ui.button(
                            'Import Collection',
                            on_click=lambda: self.navigate_to_tab('settings')
                        ).classes(
                            'border-2 border-white text-white hover:bg-white hover:text-purple-600 '
                            'font-semibold px-8 py-4 rounded-xl smooth-transition hover-lift text-lg'
                        ).props('outline')

            
            # Stats bar with responsive grid
            with ui.element('section').classes(
                'w-full bg-white dark:bg-gray-800 py-12 px-6 shadow-lg'
            ):
                with ui.element('div').classes(
                    'max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8'
                ):
                    stats_items = [
                        ('inventory_2', 'Unlimited Collection', 'Track every bottle in your collection'),
                        ('analytics', 'Advanced Analytics', 'Deep insights into your preferences'),
                        ('psychology', 'Smart Recommendations', 'AI-powered fragrance suggestions'),
                        ('cloud_sync', 'Data Management', 'Import, export, and backup your data')
                    ]

                    for icon, title, desc in stats_items:
                        with ui.column().classes('items-center text-center'):
                            ui.icon(icon, size='2.5em').classes('text-purple-600 dark:text-purple-400 mb-4')
                            ui.label(title).classes(
                                'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2'
                            )
                            ui.label(desc).classes(
                                'text-gray-600 dark:text-gray-400 text-sm'
                            )

           # Feature showcase
            with ui.element('section').classes('w-full py-20 px-6'):
                with ui.column().classes('max-w-6xl mx-auto items-center'):
                    # Section header
                    ui.label('Everything You Need to Master Your Collection').classes(
                        'text-4xl font-bold text-gray-800 dark:text-gray-200 mb-4'
                    )
                    ui.label('Comprehensive tools for fragrance enthusiasts').classes(
                        'text-xl text-gray-600 dark:text-gray-400 mb-16'
                    )

                    # Feature grid - Changed to 2x2 grid for equal sizing
                    with ui.element('div').classes('w-full grid grid-cols-1 lg:grid-cols-2 gap-8'):
                        # Smart Collection Management card
                        with ui.card().classes(
                            'p-8 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/50 dark:to-blue-800/50 '
                            'border border-blue-200 dark:border-blue-700/50 hover:shadow-xl smooth-transition hover-lift'
                        ):
                            ui.icon('inventory_2', size='3em').classes('text-blue-600 dark:text-blue-400 mb-4')
                            ui.label('Smart Collection Management').classes(
                                'text-2xl font-bold text-blue-900 dark:text-blue-100 mb-4'
                            )
                            ui.label('Track your entire fragrance library with detailed metadata:').classes(
                                'text-blue-800 dark:text-blue-200 mb-4'
                            )
                            features = [
                                'Fragrance notes and accords',
                                'Brand and classification tracking',
                                'CSV import for bulk additions',
                                'Smart search across all fields'
                            ]
                            for feature in features:
                                with ui.row().classes('items-center gap-3 mb-2'):
                                    ui.icon('check_circle', size='1.2em').classes('text-blue-600 dark:text-blue-400')
                                    ui.label(feature).classes('text-blue-700 dark:text-blue-300')

                        # AI-Powered Recommendations card
                        with ui.card().classes(
                            'p-8 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/50 dark:to-green-800/50 '
                            'border border-green-200 dark:border-green-700/50 hover:shadow-xl smooth-transition hover-lift'
                        ):
                            ui.icon('psychology', size='3em').classes('text-green-600 dark:text-green-400 mb-4')
                            ui.label('AI-Powered Recommendations').classes(
                                'text-2xl font-bold text-green-900 dark:text-green-100 mb-4'
                            )
                            ui.label('Get personalized suggestions based on:').classes(
                                'text-green-800 dark:text-green-200 mb-4'
                            )
                            rec_features = [
                                'Your rating patterns and preferences',
                                'Seasonal and occasion matching',
                                'Neglected bottle alerts',
                                'Similar fragrance discovery'
                            ]
                            for feature in rec_features:
                                with ui.row().classes('items-center gap-3 mb-2'):
                                    ui.icon('auto_awesome', size='1.2em').classes('text-green-600 dark:text-green-400')
                                    ui.label(feature).classes('text-green-700 dark:text-green-300')

                        # Advanced Analytics Dashboard card
                        with ui.card().classes(
                            'p-8 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/50 dark:to-purple-800/50 '
                            'border border-purple-200 dark:border-purple-700/50 hover:shadow-xl smooth-transition hover-lift'
                        ):
                            ui.icon('analytics', size='3em').classes('text-purple-600 dark:text-purple-400 mb-4')
                            ui.label('Advanced Analytics Dashboard').classes(
                                'text-2xl font-bold text-purple-900 dark:text-purple-100 mb-4'
                            )
                            ui.label('Discover patterns in your fragrance journey:').classes(
                                'text-purple-800 dark:text-purple-200 mb-4'
                            )
                            analytics_features = [
                                'Seasonal preference analysis',
                                'Usage frequency insights',
                                'Rating distribution charts',
                                'Brand and note preferences'
                            ]
                            for feature in analytics_features:
                                with ui.row().classes('items-center gap-3 mb-2'):
                                    ui.icon('trending_up', size='1.2em').classes('text-purple-600 dark:text-purple-400')
                                    ui.label(feature).classes('text-purple-700 dark:text-purple-300')

                        # Professional Data Management card
                        with ui.card().classes(
                            'p-8 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/50 dark:to-orange-800/50 '
                            'border border-orange-200 dark:border-orange-700/50 hover:shadow-xl smooth-transition hover-lift'
                        ):
                            ui.icon('cloud_sync', size='3em').classes('text-orange-600 dark:text-orange-400 mb-4')
                            ui.label('Professional Data Management').classes(
                                'text-2xl font-bold text-orange-900 dark:text-orange-100 mb-4'
                            )
                            ui.label('Keep your data safe and accessible:').classes(
                                'text-orange-800 dark:text-orange-200 mb-4'
                            )
                            data_features = [
                                'Complete JSON export/import',
                                'CSV bulk import support',
                                'Data integrity validation',
                                'Backup and restore functionality'
                            ]
                            for feature in data_features:
                                with ui.row().classes('items-center gap-3 mb-2'):
                                    ui.icon('security', size='1.2em').classes('text-orange-600 dark:text-orange-400')
                                    ui.label(feature).classes('text-orange-700 dark:text-orange-300')
                        
            # Getting Started section
            with ui.element('section').classes(
                'w-full bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 py-20 px-6'
            ):
                with ui.column().classes('max-w-4xl mx-auto items-center'):
                    ui.label('Ready to Start Your Fragrance Journey?').classes(
                        'text-4xl font-bold text-gray-800 dark:text-gray-200 mb-8'
                    )

                    with ui.row().classes('w-full gap-8 justify-center mb-12'):
                        # Step cards
                        steps = [
                            ('1', 'add_circle', 'Add Your Collection', 'Import your fragrances or add them manually'),
                            ('2', 'event_note', 'Log Your Wears', 'Track when and how you rate each fragrance'),
                            ('3', 'insights', 'Discover Patterns', 'Explore analytics and get recommendations')
                        ]

                        for number, icon, title, desc in steps:
                            with ui.card().classes(
                                'p-6 bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                                'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift max-w-xs'
                            ):
                                with ui.column().classes('items-center'):
                                    ui.label(number).classes(
                                        'text-3xl font-bold text-purple-600 dark:text-purple-400 mb-3'
                                    )
                                    ui.icon(icon, size='2em').classes('text-gray-600 dark:text-gray-400 mb-3')
                                    ui.label(title).classes(
                                        'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2'
                                    )
                                    ui.label(desc).classes(
                                        'text-gray-600 dark:text-gray-400 text-sm text-center'
                                    )

                    # Final CTA
                    with ui.row().classes('gap-6'):
                        ui.button(
                            'Add Your First Fragrance',
                            on_click=self.show_add_cologne_dialog
                        ).classes(
                            'bg-purple-600 hover:bg-purple-700 text-white font-semibold px-8 py-4 '
                            'rounded-xl shadow-lg hover:shadow-xl smooth-transition hover-lift text-lg'
                        )

                        ui.button(
                            'Explore the Dashboard',
                            on_click=lambda: self.navigate_to_tab('collection')
                        ).classes(
                            'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 '
                            'hover:bg-gray-300 dark:hover:bg-gray-600 font-semibold px-8 py-4 '
                            'rounded-xl smooth-transition hover-lift text-lg'
                        )

    def navigate_to_tab(self, tab_name: str):
        """Navigate to a specific tab and ensure content is shown"""
        ui.run_javascript(f'window.location.hash = "{tab_name}";')
        if hasattr(self, 'hidden_tabs'):
            self.hidden_tabs.value = tab_name
            self.on_tab_change(tab_name)

    def setup_collection_tab(self):
        with self.collection_tab_container:
            with ui.row().classes('w-full gap-6 p-6'):
                # Left column - Collection table
                with ui.column().classes('flex-1'):
                    ui.label('Your Cologne Collection').classes(
                        'text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4'
                    )
                    self.search_input = ui.input('Search colognes...', on_change=self.filter_colognes).classes(
                        'w-full mb-4 px-4 py-3 border border-gray-300 dark:border-gray-600 '
                        'rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent '
                        'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 '
                        'placeholder-gray-500 dark:placeholder-gray-400 smooth-transition'
                    )
                    ui.upload(on_upload=self.handle_csv_upload, multiple=False).props('flat accept=".csv"').classes(
                        'mb-4 bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 '
                        'rounded-lg px-4 py-2 text-blue-700 dark:text-blue-300 hover:bg-blue-100 '
                        'dark:hover:bg-blue-800 smooth-transition'
                    ).tooltip('Upload CSV with columns: name, brand, notes (semicolon separated), classifications (semicolon separated)')
                    self.cologne_table_container = ui.column().classes(
                        'w-full bg-white dark:bg-gray-800 rounded-xl shadow-lg border '
                        'border-gray-200 dark:border-gray-700 overflow-hidden smooth-transition'
                    )
                    self.refresh_cologne_table()
                with ui.column().classes('w-96 gap-6'):
                    with ui.card().classes(
                        'w-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                        'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift'
                    ):
                        with ui.card_section().classes('p-6'):
                            ui.label('Recent Wears').classes(
                                'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4'
                            )
                            self.recent_wears_container = ui.column().classes('w-full gap-3')
                            self.refresh_recent_wears()
                    with ui.card().classes(
                        'w-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                        'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift'
                    ):
                        with ui.card_section().classes('p-6'):
                            ui.label('Today\'s Recommendation').classes(
                                'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4'
                            )
                            with ui.row().classes('w-full gap-2 mb-4'):
                                ui.button('Regenerate', on_click=self.refresh_recommendation).classes(
                                    'bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 '
                                    'rounded-lg shadow-md hover:shadow-lg smooth-transition hover-lift'
                                ).props('size=sm')
                                ui.button('Custom', on_click=self.show_custom_recommendation_dialog).classes(
                                    'border border-blue-600 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900 '
                                    'font-medium px-4 py-2 rounded-lg smooth-transition hover-lift'
                                ).props('size=sm outline')
                            self.recommendation_card = ui.column().classes('w-full')
                            self.refresh_recommendation()

    def setup_analytics_tab(self):
        with self.analytics_tab_container:
            with ui.column().classes('w-full p-6'):
                with ui.row().classes('w-full items-center justify-between mb-6'):
                    ui.label('Fragrance Analytics Dashboard').classes(
                        'text-3xl font-bold text-gray-800 dark:text-gray-200'
                    )
                    ui.button('Refresh Analytics', on_click=self.refresh_analytics, icon='refresh').classes(
                        'bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 '
                        'rounded-lg shadow-md hover:shadow-lg smooth-transition hover-lift'
                    )
                self.analytics_container = ui.column().classes('w-full gap-6')
                self.refresh_analytics()

    def setup_settings_tab(self):
        with self.settings_tab_container:
            with ui.column().classes('w-full max-w-2xl mx-auto p-6 gap-6'):
                ui.label('Settings & Data Management').classes(
                    'text-3xl font-bold text-gray-800 dark:text-gray-200 mb-6 text-center'
                )
                with ui.card().classes(
                    'w-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                    'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift'
                ):
                    with ui.card_section().classes('p-6'):
                        ui.label('Export Collection').classes(
                            'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2'
                        )
                        ui.label('Download your complete collection as JSON backup').classes(
                            'text-gray-600 dark:text-gray-400 mb-4'
                        )
                        ui.button('Export Collection', on_click=self.export_collection, icon='download').classes(
                            'bg-green-600 hover:bg-green-700 text-white font-medium px-6 py-3 '
                            'rounded-lg shadow-md hover:shadow-lg smooth-transition hover-lift'
                        )
                with ui.card().classes(
                    'w-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                    'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift'
                ):
                    with ui.card_section().classes('p-6'):
                        ui.label('Import Collection').classes(
                            'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2'
                        )
                        ui.label('Import from JSON backup file').classes(
                            'text-gray-600 dark:text-gray-400 mb-4'
                        )
                        ui.button('Import Collection', on_click=self.show_import_dialog, icon='upload').classes(
                            'bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 '
                            'rounded-lg shadow-md hover:shadow-lg smooth-transition hover-lift'
                        )
                with ui.card().classes(
                    'w-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                    'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift'
                ):
                    with ui.card_section().classes('p-6'):
                        ui.label('CSV Import').classes(
                            'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2'
                        )
                        ui.label('Import colognes from CSV file (basic data only)').classes(
                            'text-gray-600 dark:text-gray-400 mb-4'
                        )
                        ui.upload(on_upload=self.handle_csv_upload, multiple=False).props('flat accept=".csv"').classes(
                            'bg-orange-50 dark:bg-orange-900 border-2 border-dashed border-orange-300 '
                            'dark:border-orange-700 rounded-lg p-6 text-orange-700 dark:text-orange-300 '
                            'hover:bg-orange-100 dark:hover:bg-orange-800 smooth-transition'
                        ).tooltip('Upload CSV with columns: name, brand, notes (semicolon separated), classifications (semicolon separated)')

    def refresh_analytics(self):
        """Refresh analytics dashboard with latest data"""
        if hasattr(self, 'analytics_container'):
            self.analytics_container.clear()

        try:
            analytics_data = self.db.get_analytics_data()

            with self.analytics_container:
                # Collection Overview Cards with enhanced styling
                with ui.row().classes('w-full gap-6 mb-8'):
                    overview = analytics_data['collection_overview']

                    with ui.card().classes(
                        'flex-1 bg-gradient-to-br from-blue-500 to-blue-600 text-white '
                        'shadow-lg hover:shadow-xl smooth-transition hover-lift border-0'
                    ):
                        with ui.card_section().classes('p-6 text-center'):
                            ui.label(f"{overview['total_colognes']}").classes(
                                'text-4xl font-bold mb-2 drop-shadow-sm'
                            )
                            ui.label('Total Colognes').classes('text-blue-100 font-medium')

                    with ui.card().classes(
                        'flex-1 bg-gradient-to-br from-green-500 to-green-600 text-white '
                        'shadow-lg hover:shadow-xl smooth-transition hover-lift border-0'
                    ):
                        with ui.card_section().classes('p-6 text-center'):
                            ui.label(f"{overview['total_wears']}").classes(
                                'text-4xl font-bold mb-2 drop-shadow-sm'
                            )
                            ui.label('Total Wears').classes('text-green-100 font-medium')

                    with ui.card().classes(
                        'flex-1 bg-gradient-to-br from-purple-500 to-purple-600 text-white '
                        'shadow-lg hover:shadow-xl smooth-transition hover-lift border-0'
                    ):
                        with ui.card_section().classes('p-6 text-center'):
                            ui.label(f"{overview['usage_rate']}%").classes(
                                'text-4xl font-bold mb-2 drop-shadow-sm'
                            )
                            ui.label('Usage Rate').classes('text-purple-100 font-medium')

                    with ui.card().classes(
                        'flex-1 bg-gradient-to-br from-orange-500 to-orange-600 text-white '
                        'shadow-lg hover:shadow-xl smooth-transition hover-lift border-0'
                    ):
                        with ui.card_section().classes('p-6 text-center'):
                            ui.label(f"{overview['recent_wears_30d']}").classes(
                                'text-4xl font-bold mb-2 drop-shadow-sm'
                            )
                            ui.label('Recent Wears (30d)').classes('text-orange-100 font-medium')

                # Charts in grid layout with enhanced cards
                with ui.row().classes('w-full gap-6'):
                    # Left column
                    with ui.column().classes('flex-1 gap-6'):
                        # Wear timeline in card
                        if analytics_data['wear_timeline']['dates']:
                            with ui.card().classes(
                                'w-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                                'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift'
                            ):
                                wear_fig = px.line(
                                    x=analytics_data['wear_timeline']['dates'],
                                    y=analytics_data['wear_timeline']['counts'],
                                    title='Fragrance Usage Over Time'
                                )
                                wear_fig.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
                                ui.plotly(wear_fig).classes('w-full')

                        # Seasonal breakdown in card
                        if analytics_data['seasonal_breakdown']['seasons']:
                            with ui.card().classes(
                                'w-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                                'border border-gray-200 dark:border-gray-700 smooth-transition hover-lift'
                            ):
                                seasonal_fig = px.pie(
                                    values=analytics_data['seasonal_breakdown']['counts'],
                                    names=analytics_data['seasonal_breakdown']['seasons'],
                                    title='Seasonal Preferences'
                                )
                                seasonal_fig.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
                                ui.plotly(seasonal_fig).classes('w-full')

                    # Right column
                    with ui.column().classes('flex-1 gap-4'):
                        # Top fragrances
                        if analytics_data['top_fragrances']['names']:
                            top_fig = px.bar(
                                x=analytics_data['top_fragrances']['wear_counts'],
                                y=analytics_data['top_fragrances']['names'],
                                orientation='h',
                                title='Most Worn Fragrances'
                            )
                            top_fig.update_layout(height=300)
                            ui.plotly(top_fig).classes('w-full')

                        # Rating distribution
                        if analytics_data['rating_stats']['distribution']['ratings']:
                            rating_fig = px.histogram(
                                x=analytics_data['rating_stats']['distribution']['ratings'],
                                nbins=10,
                                title=f"Rating Distribution (Avg: {analytics_data['rating_stats']['stats']['average']:.1f})"
                            )
                            rating_fig.update_layout(height=300)
                            ui.plotly(rating_fig).classes('w-full')

                # Additional charts row
                with ui.row().classes('w-full gap-4 mt-4'):
                    # Brand analysis
                    if analytics_data['brand_stats']['brands']:
                        brand_fig = px.bar(
                            x=analytics_data['brand_stats']['brands'],
                            y=analytics_data['brand_stats']['wear_counts'],
                            title='Most Worn Brands'
                        )
                        brand_fig.update_layout(height=300)
                        ui.plotly(brand_fig).classes('w-full flex-1')

                    # Note preferences
                    if analytics_data['note_preferences']['notes']:
                        notes_fig = px.bar(
                            x=analytics_data['note_preferences']['notes'][:10],  # Top 10
                            y=analytics_data['note_preferences']['wear_counts'][:10],
                            title='Most Worn Fragrance Notes'
                        )
                        notes_fig.update_layout(height=300)
                        ui.plotly(notes_fig).classes('w-full flex-1')

                # Wear Frequency Insights Section
                ui.label('Wear Frequency Insights').classes(
                    'text-2xl font-semibold text-gray-800 dark:text-gray-200 mt-8 mb-4'
                )

                frequency_insights = analytics_data.get('wear_frequency_insights', {})
                if frequency_insights:
                    with ui.row().classes('w-full gap-6'):
                        # Neglected fragrances
                        if frequency_insights.get('neglected'):
                            with ui.card().classes(
                                'flex-1 bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                                'border border-gray-200 dark:border-gray-700 smooth-transition'
                            ):
                                with ui.card_section().classes('p-6'):
                                    with ui.row().classes('items-center gap-3 mb-4'):
                                        ui.icon('schedule', size='1.5em').classes('text-orange-500')
                                        ui.label('Neglected Bottles').classes(
                                            'text-lg font-semibold text-gray-800 dark:text-gray-200'
                                        )

                                    for cologne in frequency_insights['neglected'][:5]:
                                        with ui.row().classes('items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700'):
                                            with ui.column():
                                                ui.label(f"{cologne['name']}").classes(
                                                    'font-medium text-gray-800 dark:text-gray-200'
                                                )
                                                ui.label(f"{cologne['brand']}").classes(
                                                    'text-sm text-gray-600 dark:text-gray-400'
                                                )
                                            ui.label(f"{cologne['days_since_worn']} days ago").classes(
                                                'text-sm text-orange-600 dark:text-orange-400'
                                            )

                        # Well-rotated fragrances
                        if frequency_insights.get('balanced'):
                            with ui.card().classes(
                                'flex-1 bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl '
                                'border border-gray-200 dark:border-gray-700 smooth-transition'
                            ):
                                with ui.card_section().classes('p-6'):
                                    with ui.row().classes('items-center gap-3 mb-4'):
                                        ui.icon('balance', size='1.5em').classes('text-green-500')
                                        ui.label('Well-Rotated').classes(
                                            'text-lg font-semibold text-gray-800 dark:text-gray-200'
                                        )

                                    for cologne in frequency_insights['balanced'][:5]:
                                        with ui.row().classes('items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700'):
                                            with ui.column():
                                                ui.label(f"{cologne['name']}").classes(
                                                    'font-medium text-gray-800 dark:text-gray-200'
                                                )
                                                ui.label(f"{cologne['brand']}").classes(
                                                    'text-sm text-gray-600 dark:text-gray-400'
                                                )
                                            ui.label(f"⭐ {cologne['avg_rating']:.1f}").classes(
                                                'text-sm text-green-600 dark:text-green-400'
                                            )

                # Seasonal Deep Dive Section
                ui.label('Seasonal Deep Dive').classes(
                    'text-2xl font-semibold text-gray-800 dark:text-gray-200 mt-8 mb-4'
                )

                seasonal_data = analytics_data.get('seasonal_deep_dive', {})
                if seasonal_data and seasonal_data.get('seasonal_breakdown'):
                    with ui.row().classes('w-full gap-6 mb-6'):
                        # Seasonal activity overview
                        breakdown = seasonal_data['seasonal_breakdown']
                        for season in ['spring', 'summer', 'fall', 'winter']:
                            season_data = breakdown.get(season, {})
                            color_map = {
                                'spring': 'from-green-400 to-green-600',
                                'summer': 'from-yellow-400 to-orange-500',
                                'fall': 'from-orange-400 to-red-600',
                                'winter': 'from-blue-400 to-blue-600'
                            }

                            with ui.card().classes(
                                f'flex-1 bg-gradient-to-br {color_map[season]} text-white '
                                'shadow-lg hover:shadow-xl smooth-transition hover-lift border-0'
                            ):
                                with ui.card_section().classes('p-4 text-center'):
                                    ui.label(season.title()).classes('text-lg font-semibold mb-2')
                                    ui.label(f"{season_data.get('total_wears', 0)}").classes('text-2xl font-bold')
                                    ui.label('wears').classes('text-sm opacity-90')
                                    if season_data.get('diversity_score', 0) > 0:
                                        ui.label(f'Diversity: {season_data["diversity_score"]}').classes('text-xs opacity-75 mt-1')

                    # Seasonal favorites
                    if seasonal_data.get('seasonal_favorites'):
                        ui.label('Seasonal Favorites').classes(
                            'text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4'
                        )

                        with ui.row().classes('w-full gap-4'):
                            for season, favorites in seasonal_data['seasonal_favorites'].items():
                                if favorites:
                                    with ui.card().classes(
                                        'flex-1 bg-white dark:bg-gray-800 shadow-lg '
                                        'border border-gray-200 dark:border-gray-700'
                                    ):
                                        with ui.card_section().classes('p-4'):
                                            ui.label(f'{season.title()} Favorites').classes(
                                                'text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3'
                                            )

                                            for fav in favorites[:3]:
                                                with ui.row().classes('items-center justify-between py-1'):
                                                    with ui.column().classes('flex-1'):
                                                        ui.label(fav['name']).classes(
                                                            'text-sm font-medium text-gray-800 dark:text-gray-200'
                                                        )
                                                        ui.label(f"{fav['brand']} • {fav['wears']} wears").classes(
                                                            'text-xs text-gray-600 dark:text-gray-400'
                                                        )

        except Exception as e:
            with self.analytics_container:
                ui.label(f'Error loading analytics: {str(e)}').classes('text-negative p-4')
                if analytics_data.get('collection_overview', {}).get('total_wears', 0) == 0:
                    ui.label('Add some wear history to see analytics!').classes('text-body2 p-4')

    def refresh_cologne_table(self, search_term: str = ''):
        if self.cologne_table_container:
            self.cologne_table_container.clear()
        
        colognes = self.db.get_colognes()
        
        # Filter by search term
        if search_term:
            search_lower = search_term.lower()
            colognes = [c for c in colognes if 
                       search_lower in str(c.name).lower() or 
                       search_lower in str(c.brand).lower() or
                       any(search_lower in str(note.name).lower() for note in c.notes) or
                       any(search_lower in str(classification.name).lower() for classification in c.classifications)]
        
        if not colognes:
            if self.cologne_table_container:
                with self.cologne_table_container:
                    self.show_welcome_message()
            return
        
        # Create table data
        table_data = []
        for cologne in colognes:
            notes = ', '.join([str(note.name) for note in cologne.notes])
            classifications = ', '.join([str(c.name) for c in cologne.classifications])
            
            # Get last worn date
            recent_wear = self.db.session.query(WearHistory).filter_by(cologne_id=cologne.id).order_by(WearHistory.date_worn.desc()).first()
            last_worn = recent_wear.date_worn.strftime('%Y-%m-%d') if recent_wear else 'Never'
            
            table_data.append({
                'name': str(cologne.name),
                'brand': str(cologne.brand), 
                'notes': notes,
                'classifications': classifications,
                'last_worn': last_worn
            })
        
        if self.cologne_table_container:
            with self.cologne_table_container:
                # Configure AG Grid columns with advanced features
                column_defs = [
                    {
                        'headerName': 'Name',
                        'field': 'name',
                        'sortable': True,
                        'filter': True,
                        'resizable': True,
                        'width': 200,
                        'cellStyle': {'fontWeight': 'bold'}
                    },
                    {
                        'headerName': 'Brand',
                        'field': 'brand',
                        'sortable': True,
                        'filter': True,
                        'resizable': True,
                        'width': 150
                    },
                    {
                        'headerName': 'Notes',
                        'field': 'notes',
                        'sortable': True,
                        'filter': True,
                        'resizable': True,
                        'flex': 1,
                        'wrapText': True,
                        'autoHeight': True
                    },
                    {
                        'headerName': 'Classifications',
                        'field': 'classifications',
                        'sortable': True,
                        'filter': True,
                        'resizable': True,
                        'width': 180,
                        'wrapText': True
                    },
                    {
                        'headerName': 'Last Worn',
                        'field': 'last_worn',
                        'sortable': True,
                        'filter': 'agDateColumnFilter',
                        'resizable': True,
                        'width': 120,
                        'cellStyle': {
                            'textAlign': 'center'
                        }
                    }
                ]

                # Create AG Grid with professional features
                ui.aggrid({
                    'columnDefs': column_defs,
                    'rowData': table_data,
                    'defaultColDef': {
                        'sortable': True,
                        'filter': True,
                        'resizable': True,
                        'minWidth': 100
                    },
                    'enableRangeSelection': True,
                    'enableClipboard': True,
                    'pagination': True,
                    'paginationPageSize': 20,
                    'domLayout': 'autoHeight',
                    'theme': 'alpine',  # Clean professional theme
                    'suppressMenuHide': True,
                    'animateRows': True,
                    'rowSelection': 'single',
                    'enableCellTextSelection': True
                }).classes('w-full ag-theme-alpine')

    def refresh_recent_wears(self):
        if self.recent_wears_container:
            self.recent_wears_container.clear()
        
        recent_wears = self.db.get_wear_history()[:5]  # Last 5 wears
        
        if not recent_wears:
            if self.recent_wears_container:
                with self.recent_wears_container:
                    ui.label('No wear history yet').classes('text-center p-2')
            return
        
        if self.recent_wears_container:
            with self.recent_wears_container:
                for wear in recent_wears:
                    cologne = wear.cologne
                    with ui.card().classes('w-full mb-2'):
                        with ui.card_section():
                            ui.label(str(cologne.name)).classes('text-weight-bold')
                            ui.label(f'{cologne.brand}').classes('text-caption')
                            
                            # Show notes and classifications below
                            if cologne.notes:
                                notes_text = ', '.join([str(note.name) for note in cologne.notes[:3]])  # Show max 3 notes
                                ui.label(f'Notes: {notes_text}').classes('text-caption text-grey-7')
                            
                            if cologne.classifications:
                                class_text = ', '.join([str(c.name) for c in cologne.classifications])
                                ui.label(f'Type: {class_text}').classes('text-caption text-grey-7')
                            
                            ui.label(f'{wear.season.title()} • {wear.occasion.title()}').classes('text-caption')
                            ui.label(wear.date_worn.strftime('%m/%d/%Y')).classes('text-caption text-grey-6')

    def refresh_recommendation(self):
        if self.recommendation_card:
            self.recommendation_card.clear()
        
        # Get current season (simplified)
        month = datetime.now().month
        if month in [12, 1, 2]:
            season = 'winter'
        elif month in [3, 4, 5]:
            season = 'spring'
        elif month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'fall'
        
        recommendations = self.db.get_recommendations(season=season)
        
        if self.recommendation_card:
            with self.recommendation_card:
                if recommendations:
                    cologne = recommendations[0]  # Top recommendation
                    with ui.card().classes('w-full'):
                        with ui.card_section():
                            ui.label(str(cologne.name)).classes('text-h6 text-weight-bold')
                            ui.label(str(cologne.brand)).classes('text-subtitle2 text-grey-7')
                            
                            if cologne.notes:
                                notes_text = ', '.join([str(note.name) for note in cologne.notes])
                                ui.label(f'Notes: {notes_text}').classes('text-body2 mt-2')
                            
                            if cologne.classifications:
                                class_text = ', '.join([str(c.name) for c in cologne.classifications])
                                ui.label(f'Type: {class_text}').classes('text-body2')
                            
                            ui.button('Wear This', 
                                    on_click=lambda e: self.quick_log_wear(cologne.id)).classes('mt-2')
                else:
                    ui.label('Add more colognes to get recommendations!').classes('text-center p-4')

    def filter_colognes(self):
        search_term = self.search_input.value if self.search_input else ''
        self.refresh_cologne_table(search_term)

    def show_add_cologne_dialog(self):
        with ui.dialog() as dialog, ui.card():
            ui.label('Add New Cologne').classes('text-h6 mb-4')
            
            name_input = ui.input('Name').classes('w-full')
            brand_input = ui.input('Brand').classes('w-full')
            notes_input = ui.input('Notes (comma separated)').classes('w-full')
            classifications_input = ui.input('Classifications (comma separated)').classes('w-full')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Add', on_click=lambda e: self.add_cologne(
                    dialog, name_input.value, brand_input.value, 
                    notes_input.value, classifications_input.value))
        
        dialog.open()

    def add_cologne(self, dialog: Any, name: Optional[str], brand: Optional[str], notes_str: Optional[str], classifications_str: Optional[str]):
        if not name or not brand:
            ui.notify('Name and brand are required', type='negative')
            return
        
        notes = [n.strip() for n in notes_str.split(',') if n.strip()] if notes_str else None
        classifications = [c.strip() for c in classifications_str.split(',') if c.strip()] if classifications_str else None
        
        self.db.add_cologne(name, brand, notes, classifications)
        self.refresh_cologne_table()
        dialog.close()
        ui.notify(f'Added {name} by {brand}', type='positive')

    def show_log_wear_dialog(self):
        colognes = self.db.get_colognes()
        if not colognes:
            ui.notify('Add some colognes first!', type='warning')
            return
        
        with ui.dialog() as dialog, ui.card():
            ui.label('Log Cologne Wear').classes('text-h6 mb-4')
            
            cologne_select = ui.select(
                options={c.id: f'{str(c.name)} - {str(c.brand)}' for c in colognes},
                label='Cologne'
            ).classes('w-full')
            
            season_select = ui.select(
                options=['spring', 'summer', 'fall', 'winter'],
                label='Season'
            ).classes('w-full')
            
            occasion_select = ui.select(
                options=['casual', 'work', 'date', 'formal', 'exercise', 'special'],
                label='Occasion'  
            ).classes('w-full')
            
            rating_input = ui.number('Rating (1-5)', min=1, max=5, step=0.5).classes('w-full')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Log', on_click=lambda e: self.log_wear(
                    dialog, cologne_select.value, season_select.value, 
                    occasion_select.value, rating_input.value))
        
        dialog.open()

    def log_wear(self, dialog: Any, cologne_id: Optional[int], season: Optional[str], occasion: Optional[str], rating: Optional[float]):
        if not cologne_id or not season or not occasion:
            ui.notify('Please fill in all required fields', type='negative')
            return
        
        self.db.log_wear(cologne_id, season, occasion, rating)
        self.refresh_recent_wears()
        self.refresh_recommendation()
        dialog.close()
        ui.notify('Wear logged successfully!', type='positive')

    def quick_log_wear(self, cologne_id: Any):
        # Quick log with current season and casual occasion
        month = datetime.now().month
        if month in [12, 1, 2]:
            season = 'winter'
        elif month in [3, 4, 5]:
            season = 'spring'
        elif month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'fall'
        
        self.db.log_wear(cologne_id, season, 'casual')
        self.refresh_recent_wears()
        self.refresh_recommendation()
        ui.notify('Wear logged!', type='positive')

    def show_custom_recommendation_dialog(self):
        with ui.dialog() as dialog, ui.card():
            ui.label('Custom Recommendation').classes('text-h6 mb-4')
            
            season_select = ui.select(
                options=['spring', 'summer', 'fall', 'winter'],
                label='Season (optional)'
            ).classes('w-full')
            
            occasion_select = ui.select(
                options=['casual', 'work', 'date', 'formal', 'exercise', 'special'],
                label='Occasion (optional)'
            ).classes('w-full')
            
            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Get Recommendation', on_click=lambda e: self.get_custom_recommendation(
                    dialog, season_select.value, occasion_select.value))
        
        dialog.open()

    def get_custom_recommendation(self, dialog: Any, season: Optional[str], occasion: Optional[str]):
        recommendations = self.db.get_recommendations(season, occasion)
        dialog.close()
        
        if recommendations:
            cologne = recommendations[0]
            ui.notify(f'Recommended: {str(cologne.name)} by {str(cologne.brand)}', type='info')
            # Update the recommendation display
            if self.recommendation_card:
                self.recommendation_card.clear()
                with self.recommendation_card:
                    with ui.card().classes('w-full'):
                        with ui.card_section():
                            ui.label(str(cologne.name)).classes('text-h6 text-weight-bold')
                            ui.label(str(cologne.brand)).classes('text-subtitle2 text-grey-7')
                            
                            if cologne.notes:
                                notes_text = ', '.join([str(note.name) for note in cologne.notes])
                                ui.label(f'Notes: {notes_text}').classes('text-body2 mt-2')
                            
                            if cologne.classifications:
                                class_text = ', '.join([str(c.name) for c in cologne.classifications])
                                ui.label(f'Type: {class_text}').classes('text-body2')
                            
                            ui.button('Wear This', 
                                    on_click=lambda e: self.quick_log_wear(cologne.id)).classes('mt-2')
        else:
            ui.notify('No recommendations found for those criteria', type='warning')

    def handle_csv_upload(self, e: Any):
        try:
            content = e.content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))
            
            added_count = 0
            for row in csv_reader:
                name = row.get('name', '').strip()
                brand = row.get('brand', '').strip()
                
                if not name or not brand:
                    continue
                
                notes_str = row.get('notes', '')
                classifications_str = row.get('classifications', '')
                
                notes = [n.strip() for n in notes_str.split(';') if n.strip()] if notes_str else None
                classifications = [c.strip() for c in classifications_str.split(';') if c.strip()] if classifications_str else None
                
                self.db.add_cologne(name, brand, notes, classifications)
                added_count += 1
            
            self.refresh_cologne_table()
            ui.notify(f'Added {added_count} colognes from CSV', type='positive')
            
        except Exception as ex:
            ui.notify(f'Error uploading CSV: {str(ex)}', type='negative')

    def export_collection(self):
        try:
            json_data = self.db.export_to_json()

            # Create download link
            from datetime import datetime
            filename = f"scentinel_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            # Use NiceGUI's download functionality
            ui.download(json_data.encode('utf-8'), filename=filename)
            ui.notify('Collection exported successfully!', type='positive')

        except Exception as e:
            ui.notify(f'Error exporting collection: {str(e)}', type='negative')

    def show_import_dialog(self):
        with ui.dialog() as dialog, ui.card():
            ui.label('Import Collection from JSON').classes('text-h6 mb-4')
            ui.label('This will import colognes and wear history. Existing colognes with the same name and brand will be skipped.').classes('text-body2 mb-4')

            # File upload for JSON import
            upload_component = ui.upload(
                on_upload=lambda e: self.handle_json_import(e, dialog),
                multiple=False
            ).props('flat accept=".json"').classes('mb-4')
            upload_component.tooltip('Upload JSON export file')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')

        dialog.open()

    def handle_json_import(self, e: Any, dialog: Any):
        try:
            content = e.content.decode('utf-8')
            result = self.db.import_from_json(content)

            if result["success"]:
                # Refresh the UI
                self.refresh_cologne_table()
                self.refresh_recent_wears()
                self.refresh_recommendation()

                # Show success message with stats
                success_msg = f"Import successful! Added {result['colognes_added']} colognes and {result['wear_history_added']} wear records."
                if result["errors"]:
                    success_msg += f" {len(result['errors'])} items were skipped or had errors."

                ui.notify(success_msg, type='positive')

                # Show errors if any (in a separate notification)
                if result["errors"]:
                    error_summary = "Some items were skipped:\n" + "\n".join(result["errors"][:5])
                    if len(result["errors"]) > 5:
                        error_summary += f"\n...and {len(result['errors']) - 5} more"
                    ui.notify(error_summary, type='warning')

            else:
                ui.notify(f'Import failed: {result["error"]}', type='negative')

            dialog.close()

        except Exception as ex:
            ui.notify(f'Error importing JSON: {str(ex)}', type='negative')
            dialog.close()

    def toggle_dark_mode(self):
        """Toggle between light and dark mode"""
        self.dark_mode = not self.dark_mode

        # Update body class using a timer to ensure client is ready
        def update_body_class():
            if self.dark_mode:
                ui.run_javascript('document.body.className = "dark-mode";')
                ui.run_javascript('document.documentElement.classList.add("dark");')
            else:
                ui.run_javascript('document.body.className = "light-mode";')
                ui.run_javascript('document.documentElement.classList.remove("dark");')

        ui.timer(0.1, update_body_class, once=True)

        # Update header gradient - remove old class and add new one
        if self.header_container:
            # Get current classes
            current_classes = self.header_container._classes
            if self.dark_mode:
                # Switch to dark gradient
                new_classes = [cls for cls in current_classes if cls != 'header-gradient-light']
                new_classes.append('header-gradient-dark')
            else:
                # Switch to light gradient
                new_classes = [cls for cls in current_classes if cls != 'header-gradient-dark']
                new_classes.append('header-gradient-light')

            self.header_container._classes = new_classes
            self.header_container._apply_classes()

        # Update footer gradient
        if self.footer_container:
            current_classes = self.footer_container._classes
            if self.dark_mode:
                # Switch to dark gradient
                new_classes = [cls for cls in current_classes if cls != 'footer-gradient-light']
                new_classes.append('footer-gradient-dark')
            else:
                # Switch to light gradient
                new_classes = [cls for cls in current_classes if cls != 'footer-gradient-dark']
                new_classes.append('footer-gradient-light')

            self.footer_container._classes = new_classes
            self.footer_container._apply_classes()

        ui.notify(f'Switched to {"dark" if self.dark_mode else "light"} mode', type='info')

    def update_url_hash(self, event):
        """Update URL hash when tab changes"""
        tab_value = event.value if hasattr(event, 'value') else event
        ui.run_javascript(f'window.location.hash = "{tab_value}";')


    def show_welcome_message(self):
        """Show welcome message and instructions for new users"""
        with ui.column().classes('w-full p-8 items-center'):
            # Welcome header with cologne icon
            with ui.row().classes('items-center gap-4 mb-6'):
                ui.image('data/images/cologne.png').classes('w-12 h-12 drop-shadow-lg')
                ui.label('Welcome to Scentinel!').classes(
                    'text-4xl font-bold text-gray-800 dark:text-gray-200'
                )

            ui.label('Your personal fragrance tracking companion').classes(
                'text-xl text-gray-600 dark:text-gray-400 mb-8'
            )

            # Feature highlights in cards
            with ui.row().classes('w-full gap-6 mb-8 justify-center'):
                # Track Collection card
                with ui.card().classes(
                    'p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 '
                    'border border-blue-200 dark:border-blue-700 hover:shadow-lg smooth-transition'
                ):
                    with ui.column().classes('items-center'):
                        ui.icon('inventory_2', size='2em').classes('text-blue-600 dark:text-blue-400 mb-3')
                        ui.label('Track Your Collection').classes(
                            'text-lg font-semibold text-blue-800 dark:text-blue-200 mb-2'
                        )
                        ui.label('Add colognes with notes, brands, and classifications').classes(
                            'text-blue-700 dark:text-blue-300 text-sm text-center'
                        )

                # Log Wears card
                with ui.card().classes(
                    'p-6 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 '
                    'border border-green-200 dark:border-green-700 hover:shadow-lg smooth-transition'
                ):
                    with ui.column().classes('items-center'):
                        ui.icon('calendar_today', size='2em').classes('text-green-600 dark:text-green-400 mb-3')
                        ui.label('Log Your Wears').classes(
                            'text-lg font-semibold text-green-800 dark:text-green-200 mb-2'
                        )
                        ui.label('Track when and how you rate each fragrance').classes(
                            'text-green-700 dark:text-green-300 text-sm text-center'
                        )

                # Analytics card
                with ui.card().classes(
                    'p-6 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900 dark:to-purple-800 '
                    'border border-purple-200 dark:border-purple-700 hover:shadow-lg smooth-transition'
                ):
                    with ui.column().classes('items-center'):
                        ui.icon('analytics', size='2em').classes('text-purple-600 dark:text-purple-400 mb-3')
                        ui.label('Discover Insights').classes(
                            'text-lg font-semibold text-purple-800 dark:text-purple-200 mb-2'
                        )
                        ui.label('See patterns in your fragrance preferences').classes(
                            'text-purple-700 dark:text-purple-300 text-sm text-center'
                        )

            # Getting started section
            ui.label('Getting Started').classes(
                'text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-4'
            )

            with ui.column().classes('w-full max-w-2xl text-left bg-gray-50 dark:bg-gray-800 rounded-lg p-6 mb-8'):
                with ui.row().classes('items-start gap-4 mb-4'):
                    ui.label('1.').classes(
                        'text-2xl font-bold text-blue-600 dark:text-blue-400 w-8 text-center'
                    )
                    with ui.column().classes('flex-1'):
                        ui.label('Add your first cologne').classes(
                            'text-lg font-medium text-gray-800 dark:text-gray-200'
                        )
                        ui.label('Click "Add Cologne" in the header or upload a CSV file below').classes(
                            'text-gray-600 dark:text-gray-400 text-sm'
                        )

                with ui.row().classes('items-start gap-4 mb-4'):
                    ui.label('2.').classes(
                        'text-2xl font-bold text-green-600 dark:text-green-400 w-8 text-center'
                    )
                    with ui.column().classes('flex-1'):
                        ui.label('Log when you wear it').classes(
                            'text-lg font-medium text-gray-800 dark:text-gray-200'
                        )
                        ui.label('Use "Log Wear" to track occasions, seasons, and ratings').classes(
                            'text-gray-600 dark:text-gray-400 text-sm'
                        )

                with ui.row().classes('items-start gap-4'):
                    ui.label('3.').classes(
                        'text-2xl font-bold text-purple-600 dark:text-purple-400 w-8 text-center'
                    )
                    with ui.column().classes('flex-1'):
                        ui.label('Explore your patterns').classes(
                            'text-lg font-medium text-gray-800 dark:text-gray-200'
                        )
                        ui.label('Visit the Analytics tab to see your fragrance insights and trends').classes(
                            'text-gray-600 dark:text-gray-400 text-sm'
                        )

            # Quick action buttons
            with ui.row().classes('gap-4'):
                ui.button('Add Your First Cologne', on_click=self.show_add_cologne_dialog).classes(
                    'bg-blue-600 hover:bg-blue-700 text-white font-medium px-8 py-3 '
                    'rounded-lg shadow-lg hover:shadow-xl smooth-transition hover-lift text-lg'
                )

                ui.button('Import from CSV', on_click=lambda: ui.notify('Upload a CSV file using the button above!', type='info')).classes(
                    'bg-gray-600 hover:bg-gray-700 text-white font-medium px-8 py-3 '
                    'rounded-lg shadow-lg hover:shadow-xl smooth-transition hover-lift text-lg'
                ).props('outline')

    def setup_footer(self):
        """Setup footer with gradient styling"""
        self.footer_container = ui.element('footer').classes(
            'footer-gradient-light smooth-transition mt-auto py-4 px-6'
        )

        with self.footer_container:
            with ui.row().classes('w-full items-center justify-between'):
                with ui.row().classes('items-center gap-2'):
                    ui.image('data/images/cologne.png').classes('w-4 h-4 opacity-90')
                    ui.label('Scentinel - Track your fragrance journey').classes(
                        'text-white text-sm font-medium opacity-90'
                    )
                ui.label('Made with ❤️ using NiceGUI').classes(
                    'text-white text-xs opacity-75'
                )

def main():
    app_instance = ScentinelApp()
    app_instance.setup_ui()
    
    ui.run(title='Scentinel', port=8080, reload=True)

if __name__ in {"__main__", "__mp_main__"}:
    main()