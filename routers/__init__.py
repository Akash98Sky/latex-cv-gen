from routers import files, templates

file_routes = files.router.routes
template_routes = templates.router.routes

all_routes = [
    *file_routes,
    *template_routes
]