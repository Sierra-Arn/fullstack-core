# Copyright (c) 2026 Ilya Snegov (aka Sierra Arn)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# packages/server/src/server/shared/parsing.py
import dataclasses
from functools import wraps
from typing import Mapping, Type, TypeVar
from starlette.requests import Request


ShapeType = TypeVar("ShapeType")
"""
Generic type variable representing any request shape in the application.

Request shapes are plain dataclasses that describe the fields a handler
expects to read from form data or query parameters. Each shape normalizes
its own fields in __post_init__ and exposes derived checks as properties,
so handlers work with a typed, cleaned view of the request instead of
performing dictionary lookups and normalization inline.
"""


def _build_shape(
    shape: Type[ShapeType],
    data: Mapping[str, str],
) -> ShapeType:
    """
    Construct a request shape from raw request data.

    Reads each dataclass field declared on the shape from the provided
    mapping by name. Fields absent from the mapping are omitted from the
    call so the dataclass applies its own declared default. Normalization
    and validation are the responsibility of the shape itself, not of this
    function.

    Parameters
    ----------
    shape : Type[ShapeType]
        Dataclass describing the expected fields.
    data : Mapping[str, str]
        Raw request data, typically form data or query parameters.

    Returns
    -------
    ShapeType
        An instance of the shape populated from the request data.
    """
    values = {
        field.name: data[field.name]
        for field in dataclasses.fields(shape)
        if field.name in data
    }

    return shape(**values)


def parse_form(shape: Type[ShapeType]):
    """
    Build a decorator that parses form data into a request shape.

    Extracts the submitted form data and exposes it to the handler as a
    typed dataclass injected under the form keyword argument. This removes
    the repetitive manual field extraction and normalization from every
    route while leaving the decision of how to report invalid input to the
    handler.

    Parameters
    ----------
    shape : Type[ShapeType]
        Dataclass describing the expected form fields.

    Returns
    -------
    callable
        Decorator that wraps a route handler, injecting the parsed form
        shape before execution.
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(request: Request, *args, **kwargs):
            form_data = await request.form()
            kwargs["form"] = _build_shape(shape, form_data)
            return await handler(request, *args, **kwargs)
        return wrapper
    return decorator


def parse_query(shape: Type[ShapeType]):
    """
    Build a decorator that parses query parameters into a request shape.

    Extracts the query parameters and exposes them to the handler as a
    typed dataclass injected under the params keyword argument. Like
    parse_form, it only replaces manual parsing with a convenient typed
    view and leaves reporting of invalid input to the handler.

    Parameters
    ----------
    shape : Type[ShapeType]
        Dataclass describing the expected query parameters.

    Returns
    -------
    callable
        Decorator that wraps a route handler, injecting the parsed query
        shape before execution.
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(request: Request, *args, **kwargs):
            kwargs["params"] = _build_shape(shape, request.query_params)
            return await handler(request, *args, **kwargs)
        return wrapper
    return decorator
