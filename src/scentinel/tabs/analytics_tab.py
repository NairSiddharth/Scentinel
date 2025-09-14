#!/usr/bin/env python3
"""
AnalyticsTab class for managing analytics dashboard UI and logic.
"""
from typing import Any, Optional
from nicegui import ui
from .base_tab import BaseTab

class AnalyticsTab(BaseTab):
    def __init__(self, database):
        super().__init__(database)
        self.analytics_container = None

    def setup_tab_content(self, container):
        """Setup the analytics tab UI within the provided container"""
        self.analytics_container = container
        with container:
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

    def refresh_analytics(self):
        """Refresh analytics dashboard with latest data"""
        if not self.analytics_container:
            return
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
                                import plotly.express as px
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
                                import plotly.express as px
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
                            import plotly.express as px
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
                            import plotly.express as px
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
                        import plotly.express as px
                        brand_fig = px.bar(
                            x=analytics_data['brand_stats']['brands'],
                            y=analytics_data['brand_stats']['wear_counts'],
                            title='Most Worn Brands'
                        )
                        brand_fig.update_layout(height=300)
                        ui.plotly(brand_fig).classes('w-full flex-1')

                    # Note preferences
                    if analytics_data['note_preferences']['notes']:
                        import plotly.express as px
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
                if 'analytics_data' in locals() and analytics_data.get('collection_overview', {}).get('total_wears', 0) == 0:
                    ui.label('Add some wear history to see analytics!').classes('text-body2 p-4')
