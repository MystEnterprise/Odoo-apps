{
    'name': 'Success Pipeline',
    'version': '19.0.1.0.0',
    'summary': 'Dual-track pipeline for leads and product innovation',
    'description': """
Success Pipeline
================
A dual-track pipeline for growing businesses managing both sales leads and product innovation simultaneously.

Key Features
------------
* Parallel Leads and Game-Changer (innovation) pipelines
* Stage-specific fields that appear as deals progress
* Live KPI dashboard with team accountability tracking
* Supplier database with sourcing history
* Non-negotiables tracker for team discipline
* Export-ready data for supplier and customer analysis
    """,
    'author': 'Myst Enterprise',
    'website': 'https://www.mystenterprise.com',
    'category': 'Sales/CRM',
    'price': 149.00,
    'currency': 'USD',
    'license': 'OPL-1',
    'depends': ['base', 'mail', 'board', 'base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/success_settings_views.xml',
        'views/success_dashboard_views.xml',
        'views/success_lead_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'success_pipeline/static/src/js/dashboard.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
