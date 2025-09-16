from nicegui import ui
import sys
import os

def get_resource_path(relative_path: str) -> str:
    """Get the correct path for resources in both development and executable environments"""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in PyInstaller executable
        meipass = getattr(sys, '_MEIPASS')  # Type-safe access
        return os.path.join(meipass, relative_path)
    else:
        # Running in development - paths are relative to project root
        return relative_path

class WelcomeTab:
    """Welcome/Landing page tab for Scentinel."""
    def __init__(self, app):
        self.app = app

    def setup_tab_content(self):
        """Setup the welcome landing page for new users."""
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
                    with ui.column().classes('items-center mb-8'):
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
                            on_click=lambda: self.app.navigate_to_tab('collection')
                        ).classes(
                            'text-white font-semibold px-8 py-4 rounded-xl smooth-transition hover-lift text-lg'
                        ).style('border: 2px solid white; background: transparent;')

                        ui.button(
                            'Import Collection',
                            on_click=lambda: self.app.navigate_to_tab('settings')
                        ).classes(
                            'text-white font-semibold px-8 py-4 rounded-xl smooth-transition hover-lift text-lg'
                        ).style('border: 2px solid white; background: transparent;')

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
                'w-full bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 py-20 px-6 pb-24'
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
                            on_click=self.app.show_add_cologne_dialog
                        ).classes(
                            'bg-purple-600 hover:bg-purple-700 text-white font-semibold px-8 py-4 '
                            'rounded-xl shadow-lg hover:shadow-xl smooth-transition hover-lift text-lg'
                        )

                        ui.button(
                            'Explore the Dashboard',
                            on_click=lambda: self.app.navigate_to_tab('collection')
                        ).classes(
                            'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 '
                            'hover:bg-gray-300 dark:hover:bg-gray-600 font-semibold px-8 py-4 '
                            'rounded-xl smooth-transition hover-lift text-lg'
                        )
