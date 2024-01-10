from functools import wraps
from typing import Any, Dict, List, Union

import deprecation
from colorama import Back, Fore, Style
from colorama.ansi import AnsiCodes


def color_t(text: str, color: Union[AnsiCodes, str]) -> str:
    """
    Returns a colour formatted text with default background
    """
    return color_format_string(text, color, Back.RESET)


def color_var_fore(label: str, value: str, color: Union[AnsiCodes, str]) -> str:
    """
    Returns a colour formatted string of a variable or key-value pair with a white label and coloured value
    """
    return color_var(label, Fore.RESET, value, color)


def color_var(
    label: str,
    label_color: Union[AnsiCodes, str],
    value: str,
    value_color: Union[AnsiCodes, str],
) -> str:
    """
    Returns a colour formatted string of a variable or key-value pair
    """
    return color_var_fore_back(
        label, label_color, Back.RESET, value, value_color, Back.RESET
    )


def color_var_fore_back(
    label: str,
    label_color_fore: Union[AnsiCodes, str],
    label_color_back: Union[AnsiCodes, str],
    value: str,
    value_color_fore: Union[AnsiCodes, str],
    value_color_back: Union[AnsiCodes, str],
):
    """
    Returns a colour formatted string that represents a variable or key-value pair
    """

    formatted_string = "{} {}".format(
        # Format label (or key)
        color_format_string(label, label_color_fore, label_color_back),
        # Format value
        color_format_string(value, value_color_fore, value_color_back),
    )

    return formatted_string


def color_format_string(
    text: str, color_fore: Union[AnsiCodes, str], color_back: Union[AnsiCodes, str]
) -> str:
    """
    Format text with foreground, background and reset
    """

    return "{}{}{}{}".format(color_fore, color_back, text, Style.RESET_ALL)


@deprecation.deprecated(
    deprecated_in="3.0.5",
    removed_in="3.11.0",
    current_version="3.0.5",
    details="Use argparse or typer packages instead",
)
def get_arg(key: str, args: List[Dict[str, str]]) -> Any:
    """
    Gets an argument by key or returns None if it's not present.
    NOTE: Assumes that the arguments have been parsed by parse_cli_args()
    """

    arg_value = None
    for argument in args:
        if key in argument:
            arg_value = argument[key]

    return arg_value


@deprecation.deprecated(
    deprecated_in="3.0.5",
    removed_in="3.11.0",
    current_version="3.0.5",
    details="Use argparse or typer packages instead",
)
def parse_cli_args(args: List[str]) -> List[Dict[str, Any]]:
    """
    This is used in conjunction with argparse to manage non-defined args
    and create named args.

    Processes a 1-dimensional array of arguments into an array of dicts, such
    that:
    [   '--server-name', 'localhost:1234',
        '--non-interactive',
        '--random-location=A and B = -- and C',
        '-x', '10',
        '-f=True',
        '-d'
    ]
    becomes:
    [
        {'server-name': 'localhost:1234'},
        {'non-interactive': True},
        {'random-location': 'A and B = -- and C'},
        {'x': '10'},
        {'f': 'True'},
        {'d': True}
    ]
    """

    action_args = []
    for current_index in range(0, len(args)):
        current_arg = args[current_index]

        if len(current_arg) <= 2 and current_arg[0:1] == "-":
            if current_index < (len(args) - 1):
                next_index = current_index + 1
                next_arg = args[next_index]
                if not next_arg[0:1] == "-":
                    # Append the current arg and the next arg as Key:Value
                    # options and skip forward one index
                    action_args.append({current_arg[1:]: next_arg})
                    current_index = next_index
            else:
                # Case individual switch: "-d"
                action_args.append({current_arg[1:2]: True})
                continue

            continue
        elif current_arg[0:2] == "--":
            # Check to see if the current argument contains a value or
            # if the value is located in the next argument index
            current_arg_value = __process_arg(current_arg)

            if current_arg_value is not None:
                action_args.append(current_arg_value)
                continue
            else:
                # There are no embedded values in current_arg, so check the next
                # index if it exists

                # If we are NOT at the last current_index, which is len(args) - 1
                # then check the next index to see if it starts with "--"
                # If it does not, then the next index contains the value for this argument
                if current_index < (len(args) - 1):
                    next_index = current_index + 1
                    next_arg = args[next_index]
                    if not next_arg[0:1] == "-":
                        # Append the current arg and the next arg as Key:Value
                        # options and skip forward one index
                        action_args.append({current_arg[2:]: next_arg})
                        current_index = next_index

                    else:
                        # Next index contains a new argument key, so we add
                        # this key as a current with no value
                        action_args.append({current_arg[2:]: True})
                        continue
                else:
                    # As the last value and starting with "--", this must be a
                    # current argument with no value
                    action_args.append({current_arg[2:]: True})
                    continue

        elif current_arg[0:1] == "-":
            current_arg_value = __process_arg(current_arg)
            if current_arg_value is not None:
                action_args.append(current_arg_value)
                continue

        else:
            # This value could not be identified as a specific argument
            # so we pass on trying to figure it out. Most likely a value
            # to a previous_arg at previous_index
            pass

    return action_args


def __process_arg(arg) -> Union[Dict, None]:
    """
    Processes an individual argument, returning a dictionary with a key and value
    if there is an equal sign in that argument. Removes leading "--" and "-" from
    argument keys
    """

    equal_char_pos = arg.find("=", 0)
    if equal_char_pos >= 0:
        arg_key = arg[0:equal_char_pos]
        arg_value = arg[equal_char_pos + 1 : len(arg)]

        if arg_key[0:2] == "--":
            arg_key = arg_key[2:]

        elif arg_key[0:1] == "-":
            arg_key = arg_key[1:]

        return {arg_key: arg_value}

    else:
        return None


@deprecation.deprecated(
    deprecated_in="3.0.5",
    removed_in="3.11.0",
    current_version="3.0.5",
    details="Use argparse or typer packages instead",
)
def executor_action(func):
    """
    Decorator for functions to be permitted to be called from the CLI executor.

    If a function does not have @executor_action decorator, it will not be allowed
    to be directly called.
    """
    func.__dict__["function_exposed_to_action_executor"] = True

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@deprecation.deprecated(
    deprecated_in="3.0.5",
    removed_in="3.11.0",
    current_version="3.0.5",
    details="Use argparse or typer packages instead",
)
def check_action_valid_for_executor(module, action):
    """Checks if the action specified is valid for the executor and can be executed"""
    if getattr(module, action, None) is None:
        return False
    else:
        return getattr(module, action).__dict__.get(
            "function_exposed_to_action_executor", False
        )
