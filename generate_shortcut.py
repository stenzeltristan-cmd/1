#!/usr/bin/env python3
"""
generate_shortcut.py — Builds VideoDownloader.shortcut

Generates a binary-plist iOS Shortcut that downloads videos from
Twitter/X and browser URLs using the Cobalt API (cobalt.tools),
then saves them to the Photos library.

Usage:
    python3 generate_shortcut.py

Output:
    VideoDownloader.shortcut   (import this file into the iOS Shortcuts app)
"""

import plistlib
import uuid

OUTPUT_FILE = "VideoDownloader.shortcut"
OBJ = "\ufffc"  # Unicode object-replacement character used as variable placeholder


# ---------------------------------------------------------------------------
# Token / reference helpers
# ---------------------------------------------------------------------------

def gen_uuid() -> str:
    return str(uuid.uuid4()).upper()


def text_literal(s: str) -> dict:
    """A plain text value with no variable references."""
    return {
        "Value": {"string": s},
        "WFSerializationType": "WFTextTokenString",
    }


def text_with_action_ref(prefix: str, action_uuid: str, output_name: str, suffix: str = "") -> dict:
    """
    Text value that embeds a reference to a previous action's output.
    The placeholder is inserted at len(prefix).
    """
    full = prefix + OBJ + suffix
    start = len(prefix)
    return {
        "Value": {
            "string": full,
            "attachmentsByRange": {
                f"{{{start}, 1}}": {
                    "OutputUUID": action_uuid,
                    "OutputName": output_name,
                    "Type": "ActionOutput",
                    "WFSerializationType": "WFTextTokenAttachment",
                }
            },
        },
        "WFSerializationType": "WFTextTokenString",
    }


def text_with_named_var(prefix: str, var_name: str, suffix: str = "") -> dict:
    """
    Text value that embeds a reference to a named variable.
    """
    full = prefix + OBJ + suffix
    start = len(prefix)
    return {
        "Value": {
            "string": full,
            "attachmentsByRange": {
                f"{{{start}, 1}}": {
                    "Type": "Variable",
                    "VariableName": var_name,
                    "WFSerializationType": "WFTextTokenAttachment",
                }
            },
        },
        "WFSerializationType": "WFTextTokenString",
    }


def shortcut_input_ref() -> dict:
    """Reference to the Shortcut Input (from Share Sheet)."""
    return {
        "Value": {
            "string": OBJ,
            "attachmentsByRange": {
                "{0, 1}": {
                    "Type": "ExtensionInput",
                    "WFSerializationType": "WFTextTokenAttachment",
                }
            },
        },
        "WFSerializationType": "WFTextTokenString",
    }


def action_ref(action_uuid: str, output_name: str = "Returned Result") -> dict:
    """Standalone reference to a previous action's output (no surrounding text)."""
    return text_with_action_ref("", action_uuid, output_name)


# ---------------------------------------------------------------------------
# Action builders
# ---------------------------------------------------------------------------

def a_comment(text: str) -> dict:
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.comment",
        "WFWorkflowActionParameters": {"WFCommentActionText": text},
    }


def a_text(value: str, *, custom_name: str = None) -> tuple[dict, str]:
    """Returns (action_dict, uuid)."""
    uid = gen_uuid()
    params: dict = {
        "UUID": uid,
        "WFTextActionText": text_literal(value),
    }
    if custom_name:
        params["CustomOutputName"] = custom_name
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
        "WFWorkflowActionParameters": params,
    }, uid


def a_set_var(name: str, value_token: dict) -> dict:
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.setvariable",
        "WFWorkflowActionParameters": {
            "WFVariableName": name,
            "WFInput": value_token,
        },
    }


def a_get_var(name: str) -> tuple[dict, str]:
    uid = gen_uuid()
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.getvariable",
        "WFWorkflowActionParameters": {
            "UUID": uid,
            "WFVariable": {
                "Value": {
                    "VariableName": name,
                    "Type": "Variable",
                },
                "WFSerializationType": "WFTextTokenString",
            },
        },
    }, uid


def a_ask_input(prompt: str, input_type: str = "URL") -> tuple[dict, str]:
    uid = gen_uuid()
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.ask",
        "WFWorkflowActionParameters": {
            "UUID": uid,
            "WFAskActionPrompt": text_literal(prompt),
            "WFInputType": input_type,
        },
    }, uid


def a_if_start(group_uuid: str, input_token: dict, condition: int,
               compare_to: str = None) -> dict:
    """
    condition values:
      2  = Has any value
      3  = Has no value
      0  = equals (requires compare_to)
    """
    params: dict = {
        "GroupingIdentifier": group_uuid,
        "WFControlFlowMode": 0,
        "WFInput": {"Value": input_token, "WFSerializationType": "WFTextTokenString"}
        if not isinstance(input_token, dict) or "WFSerializationType" not in input_token
        else input_token,
        "WFCondition": condition,
    }
    if compare_to is not None:
        params["WFConditionalActionString"] = text_literal(compare_to)
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
        "WFWorkflowActionParameters": params,
    }


def a_otherwise(group_uuid: str) -> dict:
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
        "WFWorkflowActionParameters": {
            "GroupingIdentifier": group_uuid,
            "WFControlFlowMode": 1,
        },
    }


def a_end_if(group_uuid: str) -> dict:
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.conditional",
        "WFWorkflowActionParameters": {
            "GroupingIdentifier": group_uuid,
            "WFControlFlowMode": 2,
        },
    }


def a_get_url(url_token: dict, *, method: str = "GET",
              headers: list = None, json_body: list = None) -> tuple[dict, str]:
    """
    GET or POST request.
    headers / json_body: list of (key_str, value_token) pairs.
    """
    uid = gen_uuid()
    params: dict = {
        "UUID": uid,
        "WFURL": url_token,
    }
    if method != "GET":
        params["Advanced"] = True
        params["WFHTTPMethod"] = method
    if headers:
        params["WFHTTPInputHeaders"] = {
            "WFDictionaryFieldValueItems": [
                {
                    "WFItemType": 0,
                    "WFKey": text_literal(k),
                    "WFValue": v,
                }
                for k, v in headers
            ]
        }
    if json_body:
        params["WFHTTPBodyType"] = "JSON"
        params["WFJSONValues"] = {
            "WFDictionaryFieldValueItems": [
                {
                    "WFItemType": 0,
                    "WFKey": text_literal(k),
                    "WFValue": v,
                }
                for k, v in json_body
            ]
        }
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.getcontentsofurl",
        "WFWorkflowActionParameters": params,
    }, uid


def a_get_dict_value(key: str, dict_token: dict) -> tuple[dict, str]:
    uid = gen_uuid()
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
        "WFWorkflowActionParameters": {
            "UUID": uid,
            "WFInput": dict_token,
            "WFDictionaryKey": text_literal(key),
        },
    }, uid


def a_save_to_photos(media_token: dict) -> dict:
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.savephotoalbum",
        "WFWorkflowActionParameters": {
            "WFInput": media_token,
        },
    }


def a_notification(body: str, title: str = "Video Downloader") -> dict:
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.notification",
        "WFWorkflowActionParameters": {
            "WFNotificationActionBody": text_literal(body),
            "WFNotificationActionTitle": text_literal(title),
            "WFNotificationActionSound": True,
        },
    }


def a_show_alert(message_token, title: str = "Error") -> dict:
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.alert",
        "WFWorkflowActionParameters": {
            "WFAlertActionMessage": message_token,
            "WFAlertActionTitle": text_literal(title),
            "WFAlertActionCancelButtonShown": False,
        },
    }


# ---------------------------------------------------------------------------
# Build the shortcut
# ---------------------------------------------------------------------------

def build_shortcut() -> dict:
    actions = []

    # ── 1. Header comment ──────────────────────────────────────────────────
    actions.append(a_comment(
        "Video Downloader\n"
        "━━━━━━━━━━━━━━━\n"
        "Downloads videos from Twitter/X and browser URLs using the Cobalt API.\n\n"
        "SETUP: Edit the Text action below and replace YOUR_COBALT_API_KEY\n"
        "with your real key from cobalt.tools (free tier available).\n\n"
        "USAGE:\n"
        "• Share Sheet: share any video URL from Safari or the Twitter/X app\n"
        "• Manual: run the shortcut and paste a URL when prompted"
    ))

    # ── 2. API key text action ─────────────────────────────────────────────
    api_key_action, api_key_uuid = a_text("YOUR_COBALT_API_KEY", custom_name="APIKey")
    actions.append(api_key_action)
    actions.append(a_set_var("APIKey", action_ref(api_key_uuid, "APIKey")))

    # ── 3. Determine video URL (Share Sheet vs manual input) ───────────────
    url_group = gen_uuid()

    # If Shortcut Input has any value → use it
    actions.append(a_if_start(url_group, shortcut_input_ref(), condition=2))
    actions.append(a_set_var("VideoURL", shortcut_input_ref()))

    # Otherwise → ask the user
    actions.append(a_otherwise(url_group))
    ask_action, ask_uuid = a_ask_input("Enter the video URL (Twitter/X, YouTube, etc.):", "URL")
    actions.append(ask_action)
    actions.append(a_set_var("VideoURL", action_ref(ask_uuid, "Provided Input")))

    actions.append(a_end_if(url_group))

    # ── 4. Call the Cobalt API ─────────────────────────────────────────────
    cobalt_headers = [
        ("Accept",        text_literal("application/json")),
        ("Content-Type",  text_literal("application/json")),
        ("Authorization", text_with_named_var("Api-Key ", "APIKey")),
    ]
    cobalt_body = [
        ("url", text_with_named_var("", "VideoURL")),
    ]
    cobalt_action, cobalt_uuid = a_get_url(
        text_literal("https://api.cobalt.tools/"),
        method="POST",
        headers=cobalt_headers,
        json_body=cobalt_body,
    )
    actions.append(cobalt_action)

    # ── 5. Extract the download URL from the response ──────────────────────
    dl_url_action, dl_url_uuid = a_get_dict_value("url", action_ref(cobalt_uuid, "Contents of URL"))
    actions.append(dl_url_action)

    # ── 6. Branch on whether we got a download URL ─────────────────────────
    dl_group = gen_uuid()
    actions.append(a_if_start(dl_group, action_ref(dl_url_uuid, "Value"), condition=2))

    # Download the video file
    download_action, download_uuid = a_get_url(action_ref(dl_url_uuid, "Value"))
    actions.append(download_action)

    # Save to Photos
    actions.append(a_save_to_photos(action_ref(download_uuid, "Contents of URL")))

    # Success notification
    actions.append(a_notification("Video saved to Photos!"))

    # Otherwise → show the error from the API response
    actions.append(a_otherwise(dl_group))

    err_action, err_uuid = a_get_dict_value("error", action_ref(cobalt_uuid, "Contents of URL"))
    actions.append(err_action)
    err_msg_action, err_msg_uuid = a_get_dict_value("code", action_ref(err_uuid, "Value"))
    actions.append(err_msg_action)
    actions.append(a_show_alert(
        action_ref(err_msg_uuid, "Value"),
        title="Cobalt API Error"
    ))

    actions.append(a_end_if(dl_group))

    # ── Top-level shortcut structure ───────────────────────────────────────
    return {
        "WFWorkflowName": "Video Downloader",
        "WFWorkflowActions": actions,
        "WFWorkflowClientVersion": "1263.0.1",
        "WFWorkflowHasShortcutInputVariables": False,
        "WFWorkflowIcon": {
            "WFWorkflowIconGlyphNumber": 59767,   # arrow-down-circle
            "WFWorkflowIconStartColor": 1285160703,  # blue
        },
        "WFWorkflowImportQuestions": [],
        "WFWorkflowInputContentItemClasses": ["WFURLContentItem"],
        "WFWorkflowMinimumClientVersion": 900,
        "WFWorkflowMinimumClientVersionString": "900",
        "WFWorkflowTypes": ["NCWidget", "WatchKit"],
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    shortcut = build_shortcut()
    with open(OUTPUT_FILE, "wb") as f:
        plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)
    action_count = len(shortcut["WFWorkflowActions"])
    print(f"Written {OUTPUT_FILE}  ({action_count} actions)")
