import os
import secrets

from flask import current_app


def save_project(form_project):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_project.filename)
    project_fn = random_hex + f_ext
    project_path = os.path.join(current_app.root_path, 'graph_projects', project_fn)
    form_project.save(project_path)
    return project_path
