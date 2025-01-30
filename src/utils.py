# External imports
from datetime import datetime, timezone
from typing import Type, TypeVar, Optional, Any
from sqlmodel import SQLModel, select
from fastapi import HTTPException, status

def current_timestamp() -> float:
    # Returns the current UTC timestamp
    return datetime.now(timezone.utc).timestamp()

T = TypeVar("T", bound=SQLModel)

def build_sqlmodel_get_all_query(model: Type[T], offset: int = 0, limit: int | None = None, created_before: int | None = None, created_after: int | None = None, created_by: int | None = None, order_by: str | None = "id", forbidden_order_by: list[str] = [], order_by_direction: str = "asc", additional_filters: list[Any] | None = None):
    if "deleted_at" not in forbidden_order_by:
        forbidden_order_by = list(forbidden_order_by) + ["deleted_at"]  # Avoid modifying original list

    statement = select(model).where(model.deleted_at == None)

    if created_after is not None and created_before is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query 'created_before' and 'created_after' cannot be declared together!")

    if created_before is not None:
        statement = statement.where(model.created_at < created_before)

    if created_after is not None:
        statement = statement.where(model.created_at > created_after)

    if created_by is not None:
        statement = statement.where(model.created_by == created_by)

    if order_by is not None:
        try:
            if order_by not in forbidden_order_by:
                column = getattr(model, order_by)
                if order_by_direction.lower() == "asc":
                    statement = statement.order_by(asc(column))
                elif order_by_direction.lower() == "desc":
                    statement = statement.order_by(desc(column))
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order_by_direction field! Valid options: asc, desc")
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot order by this field!")
        except AttributeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order_by field!")

    if additional_filters is not None:
        for filter_condition in additional_filters:
            statement = statement.where(filter_condition)

    if limit is not None:
        statement = statement.limit(limit)

    statement = statement.offset(offset)

    return statement