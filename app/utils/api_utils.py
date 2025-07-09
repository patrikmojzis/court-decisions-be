from typing import TYPE_CHECKING

import pydantic
import requests
from flask import request, g, jsonify, has_request_context

from app.exceptions.http_exception import HttpException
from app.exceptions.unauthorised_exception import UnauthorisedException
from app.http_files.resources.resource_base import ResourceBase

if TYPE_CHECKING:
    from app.models.model_base import ModelBase


def validate_request(schema, *, exclude_unset=False):
    try:
        json_data = request.get_json()
        validated = schema(**json_data).model_dump(exclude_unset=exclude_unset)
        g.validated = validated
    except pydantic.ValidationError as e:
        raise HttpException('invalid_request', 422, data=e.errors())


def paginate_all(model: type['ModelBase'], *, query: dict = None, resource: type['ResourceBase'] = ResourceBase):
    if query is None:
        query = {}

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search = request.args.get('query', None)

    if search:
        built_query = model.build_search_query_from_string(search)
        query = {**query, **built_query}

    if g.get("expand_query"):
        query = {**query, **g.get("expand_query")}

    total_records = model.count(query)
    total_pages = total_records // per_page + (1 if total_records % per_page else 0)

    result = model.find(query, limit=per_page, skip=(page - 1) * per_page,  sort=[('created_at', -1)])

    return jsonify({
        'meta': {
            'current_page': page,
            'per_page': per_page,
            'last_page': total_pages,
            'total': total_records,
        },
        'data': resource(result).dump()
    })


def get_client_ip():
    # Try to get IP from X-Forwarded-For header first (for proxy cases)
    if 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    # Then try X-Real-IP header
    elif 'X-Real-IP' in request.headers:
        ip = request.headers['X-Real-IP']
    # Finally fall back to remote address
    else:
        ip = request.remote_addr
    return ip


def download_video(url, output_path):
    response = requests.get(url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def get_bearer_auth_token() -> str | None:
    """Get the token from the request."""
    if has_request_context():
        # It's an HTTP request
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]  # Get the token part of the header
        else:
            # Fallback to checking the query parameters if no Authorization header or not a Bearer token
            return request.args.get('token')
    else:
        raise UnauthorisedException()