"""

    Build instructions for tracker exe
    
"""

# Build default PyS60 application
Application("Tracker",
    python_files = [
        "default.py",
		"lib/datatypes.py",
		"lib/datums.py",
 		"lib/gps.py",
		"lib/helpers.py",
 		"lib/osal.py",
		"lib/registry.py",
 		"lib/s60osal.py",
 		"lib/trace.py",
		"lib/waypoints.py",
 		"lib/widgets.py",
		"lib/xmlparser.py" ],
    additional_files = [
		("plugins/dashview.py",		"data/tracker030/plugins/dashview.py"),
		("plugins/datumrd.py",		"data/tracker030/plugins/datumrd.py"),
		("plugins/datumutm.py",		"data/tracker030/plugins/datumutm.py"),
		("plugins/datumwgs84.py",	"data/tracker030/plugins/datumwgs84.py"),
		("plugins/lmwaypoints.py",	"data/tracker030/plugins/lmwaypoints.py"),
		("plugins/lrgps.py",		"data/tracker030/plugins/lrgps.py"),
		("plugins/mapview.py",		"data/tracker030/plugins/mapview.py"),
		("plugins/recorder.py",		"data/tracker030/plugins/recorder.py"),
		("plugins/timers.py",		"data/tracker030/plugins/timers.py"),
		("plugins/uiregistry.py",	"data/tracker030/plugins/uiregistry.py") ],
)
