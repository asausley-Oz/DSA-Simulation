"""Planning Center -> CareHub visit-request sync.

Pull a small set of people from your Planning Center account and turn them into
CareHub visit requests. The Planning Center side is fully automated through the
official People API. The CareHub side is intentionally hand-off friendly: by
default the tool produces an import-ready CSV and a printable worksheet so you
can create the requests through CareHub's own interface with your own login.
"""

__version__ = "0.1.0"

from .models import Person, VisitRequest

__all__ = ["Person", "VisitRequest", "__version__"]
