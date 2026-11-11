import os
from django.conf import settings
from django.http import HttpResponse, Http404

def index_spa_view(request):
    frontend_dist_index = settings.BASE_DIR.parent / 'frontend' / 'dist' / 'index.html'
    if os.path.exists(frontend_dist_index):
        with open(frontend_dist_index, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    return HttpResponse(
        "<h1>DocSec API is running.</h1><p>Frontend dist not found. Run 'npm run build' in frontend/ or 'npm run dev' on port 3000.</p>"
    )
