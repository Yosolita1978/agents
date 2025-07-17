#!/usr/bin/env python
"""
Sustainability Training Panel Web Application
"""

import panel as pn
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure Panel first
pn.extension('tabulator')

# Import after Panel is configured
from sustainability.panel_bridge import create_sustainability_app

# Create and serve the app
def create_app():
    app = create_sustainability_app()
    return app.layout

# Make it servable
create_app().servable()