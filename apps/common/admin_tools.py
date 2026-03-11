from django.contrib import admin, messages
from django.apps import apps
from django.core.management import call_command, get_commands, load_command_class
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse


def _discover_project_commands():
    project_app_names = {
        app_config.name
        for app_config in apps.get_app_configs()
        if app_config.name.startswith("apps.")
    }
    command_registry = get_commands()
    commands = []

    for command_name, app_label in sorted(command_registry.items()):
        if app_label not in project_app_names:
            continue
        if command_name.startswith("_"):
            continue

        description = ""
        try:
            command_class = load_command_class(app_label, command_name)
            description = (getattr(command_class, "help", "") or "").strip()
        except Exception:
            description = ""

        commands.append(
            {
                "name": command_name,
                "app_label": app_label,
                "description": description or "No description provided.",
            }
        )

    return commands


def commands_page(request):
    discovered_commands = _discover_project_commands()
    discovered_command_names = {command["name"] for command in discovered_commands}

    if request.method == "POST":
        command_name = request.POST.get("command")

        if command_name in discovered_command_names:
            try:
                call_command(command_name)
            except Exception as exc:
                messages.error(request, f"Failed to run '{command_name}': {exc}")
            else:
                messages.success(request, f"Command '{command_name}' executed successfully.")
        else:
            messages.warning(request, "Unknown command requested.")

        return HttpResponseRedirect(reverse("admin_commands_page"))

    context = {
        **admin.site.each_context(request),
        "title": "Commands",
        "commands": discovered_commands,
    }
    return TemplateResponse(request, "admin/tools/commands.html", context)
