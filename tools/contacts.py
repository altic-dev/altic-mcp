import subprocess
import json
from .constants import SCRIPTS_PREFIX
from rapidfuzz import fuzz, process
from collections import OrderedDict
from . import result

_contact_cache = OrderedDict()
_CACHE_MAX_SIZE = 100


def _add_to_cache(contact_name: str, full_contact: str):
    """Add or update a contact in the LRU cache."""
    if contact_name in _contact_cache:
        del _contact_cache[contact_name]

    _contact_cache[contact_name] = full_contact

    if len(_contact_cache) > _CACHE_MAX_SIZE:
        _contact_cache.popitem(last=False)


def _search_cache(name: str, limit: int = 5) -> list:
    """
    Search for contacts in cache.
    Returns list of tuples: (contact_name, full_contact)
    """
    if not _contact_cache:
        return []

    search_term = name.lower()

    exact_matches = [
        (contact_name, full_contact)
        for contact_name, full_contact in _contact_cache.items()
        if search_term in contact_name.lower()
    ]

    if exact_matches:
        for contact_name, full_contact in exact_matches[:limit]:
            _add_to_cache(contact_name, full_contact)
        return exact_matches[:limit]

    matches = process.extract(
        name, list(_contact_cache.keys()), scorer=fuzz.token_sort_ratio, limit=limit
    )

    result = []
    match_threshold = 70
    for matched_name, match_score in matches:
        if match_score >= match_threshold:
            full_contact = _contact_cache[matched_name]
            result.append((matched_name, full_contact))
            _add_to_cache(matched_name, full_contact)

    return result


def search_contacts(name: str) -> str:
    script_path = SCRIPTS_PREFIX / "fetch-all-contacts.applescript"
    match_threshold = 70

    cached_results = _search_cache(name, limit=5)
    if cached_results:
        output = ""
        for idx, (contact_name, full_contact) in enumerate(cached_results):
            output += f"Option {idx + 1}: {full_contact}\n"
        return output

    try:
        result = subprocess.run(
            ["osascript", script_path],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            return f"Unable to execute script to fetch contacts: {result.stderr}"

        contacts = result.stdout.strip().split("\n")

        contact_map = {}
        for contact in contacts:
            if "|" in contact:
                contact_name = contact.split("|")[0]
                contact_map[contact_name] = contact

        search_term = name.lower()

        exact_matches = [
            contact_name
            for contact_name in contact_map.keys()
            if search_term in contact_name.lower()
        ]

        if exact_matches:
            output = ""
            for idx, matched_name in enumerate(exact_matches[:5]):  # Limit to 5
                full_contact = contact_map[matched_name]
                output += f"Option {idx + 1}: {full_contact}\n"
                _add_to_cache(matched_name, full_contact)
            return output

        matches = process.extract(
            name, list(contact_map.keys()), scorer=fuzz.token_sort_ratio, limit=5
        )

        output = ""
        for idx, match in enumerate(matches):
            matched_name = match[0]
            match_score = match[1]

            if match_score >= match_threshold:
                full_contact = contact_map[matched_name]
                output += f"Option {idx + 1}: {full_contact} (score: {match_score})\n"
                _add_to_cache(matched_name, full_contact)

        if not output:
            return f"No contacts found matching '{name}'"

        return output

    except Exception as e:
        error_msg = f"Failed to retrieve contacts: {str(e)}"
        return error_msg


def _run_manager(action: str, *args: str, timeout: int = 60) -> str:
    script_path = SCRIPTS_PREFIX / "contacts-manager.applescript"
    tool_action = f"contacts.{action}"

    try:
        completed = subprocess.run(
            ["osascript", script_path, action, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if completed.returncode != 0:
            error_msg = completed.stderr.strip() or "Unknown error"
            return result.error(
                tool_action,
                error_msg,
                permission_required="Contacts",
            )

        stdout = completed.stdout.strip()
        data = {} if not stdout else json.loads(stdout)
        return result.ok(tool_action, data)
    except subprocess.TimeoutExpired:
        return result.error(tool_action, "Operation timed out", code="timeout")
    except Exception as exc:
        return result.error(tool_action, str(exc))


def _has_contact_name(first_name: str = "", last_name: str = "") -> bool:
    return bool(first_name.strip() or last_name.strip())


def get_contact(identifier: str) -> str:
    if not identifier or not identifier.strip():
        return result.error(
            "contacts.get",
            "identifier cannot be empty",
            code="validation_error",
        )
    return _run_manager("get", identifier.strip())


def create_contact(
    first_name: str,
    last_name: str,
    organization: str = "",
    phone: str = "",
    email: str = "",
    note: str = "",
) -> str:
    if not _has_contact_name(first_name, last_name):
        return result.error(
            "contacts.create",
            "first_name or last_name is required",
            code="validation_error",
        )
    return _run_manager(
        "create",
        first_name.strip(),
        last_name.strip(),
        organization.strip(),
        phone.strip(),
        email.strip(),
        note,
    )


def update_contact(
    identifier: str,
    first_name: str = "",
    last_name: str = "",
    organization: str = "",
    phone: str = "",
    email: str = "",
    note: str = "",
) -> str:
    if not identifier or not identifier.strip():
        return result.error(
            "contacts.update",
            "identifier cannot be empty",
            code="validation_error",
        )
    return _run_manager(
        "update",
        identifier.strip(),
        first_name.strip(),
        last_name.strip(),
        organization.strip(),
        phone.strip(),
        email.strip(),
        note,
    )
