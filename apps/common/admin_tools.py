from django.contrib import admin, messages
from django.apps import apps
from django.core.management import call_command, get_commands, load_command_class
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
import shlex


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


def _command_accepts_option(app_label, command_name, option):
    """Return True when a management command defines a specific CLI option."""
    try:
        command = load_command_class(app_label, command_name)
        parser = command.create_parser("manage.py", command_name)
    except Exception:
        return False

    option_strings = {
        opt
        for action in parser._actions
        for opt in action.option_strings
    }
    return option in option_strings


def commands_page(request):
    discovered_commands = _discover_project_commands()
    discovered_command_names = {command["name"] for command in discovered_commands}
    command_app_map = {command["name"]: command["app_label"] for command in discovered_commands}

    if request.method == "POST":
        command_name = request.POST.get("command")
        raw_args = (request.POST.get("command_args") or "").strip()

        if command_name in discovered_command_names:
            try:
                parsed_args = shlex.split(raw_args) if raw_args else []

                # Auto-pass the logged-in admin email when supported by the command.
                if request.user.is_authenticated:
                    app_label = command_app_map.get(command_name)
                    has_executed_by_option = _command_accepts_option(
                        app_label,
                        command_name,
                        "--executed-by-email",
                    )
                    already_has_executed_by = "--executed-by-email" in parsed_args
                    if has_executed_by_option and not already_has_executed_by:
                        parsed_args.extend(["--executed-by-email", request.user.email])

                call_command(command_name, *parsed_args)
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
