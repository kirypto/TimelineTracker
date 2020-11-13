from typing import Union, Tuple, Optional, Set

from domain.tags import Tag


def error_response(message: Union[str, BaseException], status_code: int) -> Tuple[dict, int]:
    return {"error": str(message)}, status_code


def parse_optional_tag_query_param(tag_query_param: Optional[str]) -> Optional[Set[Tag]]:
    if tag_query_param is None:
        return None
    return {Tag(tag_str) for tag_str in tag_query_param.split(",") if len(tag_str) > 0}